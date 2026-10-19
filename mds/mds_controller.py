# -*- coding: utf-8 -*-

"""
-------------------------------------------------
Project : NNBI_database
File    : mds_controller.py
Author  :
Date    :
Description : MDSplus Controller
-------------------------------------------------
"""

from PySide2.QtCore import (
    QObject,
    Signal,
    QTimer,
)

from mds.mds_manager import MDSManager
from mds.worker import (
    DataWorker,
    TreeWorker,
    MDSOperationWorker,
    MultiShotWorker,
    ShotParameterWorker,
)
from mds.compare_data import CompareRequest


class MDSController(QObject):
    """
    MDSplus任务控制器

    功能：
    1. 管理MDSManager
    2. 管理DataWorker和TreeWorker
    3. 管理连接、Tree和Signal读取
    4. 管理任务超时
    5. 向界面发送状态和结果
    """

    statusChanged = Signal(str)

    connectionChanged = Signal(bool)

    treeOpened = Signal(str, int)
    treeClosed = Signal()
    treeLoaded = Signal(object)

    signalLoaded = Signal(object, str)

    errorOccurred = Signal(str, str)

    busyChanged = Signal(bool)

    # =====================================================
    # Multi-shot Compare Signals
    # =====================================================

    compareStarted = Signal(object)

    compareShotStarted = Signal(int, int, int)

    compareShotFinished = Signal(object)

    compareProgressChanged = Signal(int, int)

    compareFinished = Signal(object)

    compareError = Signal(str)

    shotParametersLoaded = Signal(object)
    shotParametersError = Signal(str)

    def __init__(
            self,
            timeout=5,
            downsample_enabled=True,
            max_points=10000,
            parent=None
    ):

        super(MDSController, self).__init__(
            parent
        )

        self.manager = MDSManager(
            timeout=timeout,
            downsample_enabled=downsample_enabled,
            max_points=max_points
        )

        self.data_worker = DataWorker(
            self.manager,
            self
        )

        self.tree_worker = TreeWorker(
            self.manager,
            self
        )

        self.data_timeout_timer = QTimer(
            self
        )

        self.tree_timeout_timer = QTimer(
            self
        )

        self.data_timeout_timer.setSingleShot(
            True
        )

        self.tree_timeout_timer.setSingleShot(
            True
        )

        self.operation_worker = MDSOperationWorker(
            self.manager,
            self
        )

        self.compare_worker = MultiShotWorker(
            self.manager,
            self
        )

        self.parameter_worker = ShotParameterWorker(
            self.manager,
            self
        )

        self.operation_timeout_timer = QTimer(
            self
        )

        self.operation_timeout_timer.setSingleShot(
            True
        )

        self.pending_auto_open = False
        self.pending_tree = ""
        self.pending_shot = -1
        self.pending_load_tree = False

        self.current_load_mode = "primary"
        self.current_loading_node = ""

        self.create_connections()

    # =====================================================
    # Connections
    # =====================================================

    def create_connections(self):

        self.data_worker.started.connect(
            self.on_data_worker_started
        )

        self.data_worker.data_loaded.connect(
            self.on_signal_loaded
        )

        self.data_worker.error.connect(
            self.on_data_worker_error
        )

        self.data_worker.finished.connect(
            self.on_data_worker_finished
        )

        self.tree_worker.started.connect(
            self.on_tree_worker_started
        )

        self.tree_worker.tree_loaded.connect(
            self.on_tree_loaded
        )

        self.tree_worker.error.connect(
            self.on_tree_worker_error
        )

        self.tree_worker.finished.connect(
            self.on_tree_worker_finished
        )

        self.operation_worker.started.connect(
            self.on_operation_started
        )

        self.operation_worker.operation_finished.connect(
            self.on_operation_finished
        )

        self.operation_worker.error.connect(
            self.on_operation_error
        )

        self.operation_worker.finished.connect(
            self.on_operation_worker_finished
        )

        self.operation_timeout_timer.timeout.connect(
            self.on_operation_timeout
        )

        self.data_timeout_timer.timeout.connect(
            self.on_data_timeout
        )

        self.tree_timeout_timer.timeout.connect(
            self.on_tree_timeout
        )

        self.parameter_worker.started.connect(
            self.on_parameter_worker_started
        )

        self.parameter_worker.parameters_loaded.connect(
            self.on_shot_parameters_loaded
        )

        self.parameter_worker.error.connect(
            self.on_shot_parameters_error
        )

        self.parameter_worker.finished.connect(
            self.on_parameter_worker_finished
        )

        self.compare_worker.compare_started.connect(
            self.on_compare_started
        )

        self.compare_worker.shot_started.connect(
            self.on_compare_shot_started
        )

        self.compare_worker.shot_finished.connect(
            self.on_compare_shot_finished
        )

        self.compare_worker.progress_changed.connect(
            self.on_compare_progress_changed
        )

        self.compare_worker.compare_finished.connect(
            self.on_compare_finished
        )

        self.compare_worker.error.connect(
            self.on_compare_error
        )

        self.compare_worker.finished.connect(
            self.on_compare_worker_finished
        )

    # =====================================================
    # Timeout
    # =====================================================

    def set_timeout(
            self,
            timeout
    ):

        self.manager.set_timeout(
            timeout
        )

    def timeout(self):

        return self.manager.timeout()

    def timeout_ms(self):

        return self.manager.timeout_ms()

    # =====================================================
    # Data Query Options
    # =====================================================

    def set_downsample_enabled(
            self,
            enabled
    ):

        self.manager.set_downsample_enabled(
            enabled
        )

    def downsample_enabled(self):

        return self.manager.downsample_enabled()

    def set_max_points(
            self,
            max_points
    ):

        self.manager.set_max_points(
            max_points
        )

    def max_points(self):

        return self.manager.max_points()

    def set_query_options(
            self,
            downsample_enabled=None,
            max_points=None
    ):
        """
        更新后续普通查询和多炮对比使用的默认参数。

        已经运行中的Worker使用启动时保存的参数快照，
        不会被这里的修改影响。
        """

        self.manager.set_query_options(
            downsample_enabled=downsample_enabled,
            max_points=max_points
        )

    def query_options(self):

        return self.manager.query_options()

    # =====================================================
    # Status
    # =====================================================

    def is_connected(self):

        return self.manager.is_connected()

    def is_tree_open(self):

        return self.manager.is_tree_open()

    def is_busy(self):

        return (
                self.data_worker.isRunning()
                or
                self.tree_worker.isRunning()
                or
                self.operation_worker.isRunning()
                or
                self.compare_worker.isRunning()
                or
                self.parameter_worker.isRunning()
        )

    def tree(self):

        return self.manager.tree()

    def shot(self):

        return self.manager.shot()

    # =====================================================
    # Connection
    # =====================================================

    def connect_server(
            self,
            host,
            port,
            auto_open=False,
            tree="",
            shot=-1
    ):
        """
        异步连接服务器
        """

        if self.is_busy():
            self.statusChanged.emit(
                "MDSplus worker is busy"
            )

            return False

        if self.manager.is_connected():
            self.manager.disconnect()

            self.connectionChanged.emit(
                False
            )

        self.pending_auto_open = bool(
            auto_open
        )

        self.pending_tree = str(
            tree
        ).strip()

        try:
            self.pending_shot = int(
                shot
            )
        except Exception:
            self.pending_shot = -1

        return self.operation_worker.start_operation(
            "connect",
            host=host,
            port=port
        )

    def disconnect_server(self):

        if not self.stop_all_workers():
            return False

        if self.manager.is_tree_open():
            self.manager.close_tree()

        self.manager.disconnect()

        self.current_loading_node = ""
        self.current_load_mode = "primary"

        self.treeClosed.emit()
        self.connectionChanged.emit(
            False
        )

        self.statusChanged.emit(
            "Disconnected"
        )

        return True

    # =====================================================
    # Tree
    # =====================================================

    def open_tree(
            self,
            tree,
            shot,
            load_after_open=True
    ):
        """
        异步打开Tree
        """

        if not self.manager.is_connected():
            self.errorOccurred.emit(
                "Open Tree",
                "MDSplus server is not connected."
            )

            return False

        if self.is_busy():
            self.statusChanged.emit(
                "MDSplus worker is busy"
            )

            return False

        self.pending_load_tree = bool(
            load_after_open
        )

        return self.operation_worker.start_operation(
            "open_tree",
            tree=tree,
            shot=shot
        )

    def close_tree(self):

        if not self.manager.is_tree_open():
            return False

        if not self.stop_all_workers():
            return False

        self.manager.close_tree()

        self.current_loading_node = ""
        self.current_load_mode = "primary"

        self.treeClosed.emit()

        self.statusChanged.emit(
            "Tree closed"
        )

        return True

    def load_tree(self):

        if not self.manager.is_connected():
            return False

        if not self.manager.is_tree_open():
            return False

        if self.data_worker.isRunning():
            self.statusChanged.emit(
                "Signal data worker is busy"
            )

            return False

        if self.tree_worker.isRunning():
            self.statusChanged.emit(
                "Tree worker is busy"
            )

            return False

        if self.operation_worker.isRunning():
            self.statusChanged.emit(
                "MDSplus operation is busy"
            )

            return False

        return self.tree_worker.start_loading()

    def reload_tree(self):

        if not self.manager.is_tree_open():
            return False

        if not self.stop_tree_worker():
            return False

        return self.load_tree()

    def load_shot(
            self,
            tree,
            shot
    ):
        """
        异步切换炮号
        """

        if not self.manager.is_connected():
            self.errorOccurred.emit(
                "Shot Error",
                "MDSplus server is not connected."
            )

            return False

        if self.is_busy():
            self.statusChanged.emit(
                "MDSplus worker is busy"
            )

            return False

        return self.operation_worker.start_operation(
            "switch_shot",
            tree=tree,
            shot=shot
        )

    def handle_switch_shot_result(
            self,
            result
    ):

        if not isinstance(
                result,
                dict
        ):
            self.errorOccurred.emit(
                "Shot Error",
                "Invalid shot switching result."
            )

            return

        if result.get(
                "success",
                False
        ):
            tree = result.get(
                "tree",
                ""
            )

            shot = result.get(
                "shot"
            )

            self.treeOpened.emit(
                tree,
                shot
            )

            self.statusChanged.emit(
                "Shot opened"
            )

            QTimer.singleShot(
                0,
                self.load_tree
            )

            return

        error_message = result.get(
            "error",
            "Failed to open shot."
        )

        if result.get(
                "restored",
                False
        ):
            old_tree = result.get(
                "tree",
                ""
            )

            old_shot = result.get(
                "shot"
            )

            self.treeOpened.emit(
                old_tree,
                old_shot
            )

            self.errorOccurred.emit(
                "Shot Error",
                "{}\n\nPrevious Tree was restored:\n"
                "Tree: {}\nShot: {}".format(
                    error_message,
                    old_tree,
                    old_shot
                )
            )

            self.statusChanged.emit(
                "Previous shot restored"
            )

            QTimer.singleShot(
                0,
                self.load_tree
            )

            return

        restore_error = result.get(
            "restore_error",
            ""
        )

        self.treeClosed.emit()

        message = error_message

        if restore_error:
            message += (
                "\n\nFailed to restore previous Tree:\n{}"
            ).format(
                restore_error
            )

        self.errorOccurred.emit(
            "Shot Error",
            message
        )

        self.statusChanged.emit(
            "Tree is not open"
        )

    # =====================================================
    # Signal
    # =====================================================

    def load_signal(
            self,
            node,
            mode="primary",
            downsample_enabled=None,
            max_points=None
    ):

        if self.tree_worker.isRunning():
            self.statusChanged.emit(
                "Tree is loading"
            )

            return False

        if self.data_worker.isRunning():
            self.statusChanged.emit(
                "Data worker is busy"
            )

            return False

        if self.operation_worker.isRunning():
            self.statusChanged.emit(
                "MDSplus operation is busy"
            )

            return False

        if not self.manager.is_connected():
            self.statusChanged.emit(
                "MDSplus server is not connected"
            )

            return False

        if not self.manager.is_tree_open():
            self.statusChanged.emit(
                "MDSplus Tree is not open"
            )

            return False

        node = str(
            node
        ).strip()

        if node == "":
            return False

        if mode not in (
                "primary",
                "overlay"
        ):
            mode = "primary"

        self.current_loading_node = node
        self.current_load_mode = mode

        self.manager.set_current_node(
            node
        )

        return self.data_worker.start_loading(
            node,
            downsample_enabled=downsample_enabled,
            max_points=max_points
        )

    def refresh_signal(
            self,
            node,
            downsample_enabled=None,
            max_points=None
    ):

        return self.load_signal(
            node,
            mode="primary",
            downsample_enabled=downsample_enabled,
            max_points=max_points
        )

    # =====================================================
    # Multi-shot Compare
    # =====================================================

    def start_compare(
            self,
            request,
            downsample_enabled=None,
            max_points=None
    ):
        """
        启动多炮号对比任务。

        Parameters
        ----------
        request : CompareRequest

        Returns
        -------
        bool
            是否成功启动任务。
        """

        if not isinstance(
                request,
                CompareRequest
        ):
            self.compareError.emit(
                "Invalid comparison request."
            )

            return False

        valid, message = request.validate()

        if not valid:
            self.compareError.emit(
                message
            )

            return False

        if self.is_busy():
            self.statusChanged.emit(
                "MDSplus worker is busy"
            )

            return False

        if not self.manager.is_connected():
            self.compareError.emit(
                "MDSplus server is not connected."
            )

            return False

        return self.compare_worker.start_compare(
            request,
            downsample_enabled=downsample_enabled,
            max_points=max_points
        )

    def cancel_compare(self):
        """
        请求停止当前多炮号对比任务。
        """

        if not self.compare_worker.isRunning():
            return False

        self.compare_worker.stop()

        self.statusChanged.emit(
            "Cancelling comparison..."
        )

        return True

    def is_compare_running(self):

        return self.compare_worker.isRunning()

    # =====================================================
    # Current Shot Parameters
    # =====================================================

    def load_shot_parameters(
            self,
            parameter_definitions
    ):

        if self.is_busy():
            self.statusChanged.emit(
                "MDSplus worker is busy"
            )

            return False

        if not self.manager.is_connected():
            self.shotParametersError.emit(
                "MDSplus server is not connected."
            )

            return False

        if not self.manager.is_tree_open():
            self.shotParametersError.emit(
                "MDSplus tree is not open."
            )

            return False

        return self.parameter_worker.start_loading(
            parameter_definitions
        )

    # =====================================================
    # DataWorker Slots
    # =====================================================

    def on_data_worker_started(self):

        self.busyChanged.emit(
            True
        )

        self.statusChanged.emit(
            "Loading signal..."
        )

        self.data_timeout_timer.start(
            self.timeout_ms()
        )

    def on_signal_loaded(
            self,
            signal_data
    ):

        self.signalLoaded.emit(
            signal_data,
            self.current_load_mode
        )

    def on_data_worker_error(
            self,
            message
    ):

        if self.current_load_mode == "overlay":
            title = "Overlay Load Error"
        else:
            title = "Load Error"

        self.errorOccurred.emit(
            title,
            str(message)
        )

    def on_data_worker_finished(self):

        self.data_timeout_timer.stop()

        self.current_loading_node = ""
        self.current_load_mode = "primary"

        self.busyChanged.emit(
            self.is_busy()
        )

        if self.data_worker.timed_out():
            return

        if self.manager.is_connected():

            self.statusChanged.emit(
                "Ready"
            )

        else:

            self.statusChanged.emit(
                "Disconnected"
            )

    # =====================================================
    # TreeWorker Slots
    # =====================================================

    def on_tree_worker_started(self):

        self.busyChanged.emit(
            True
        )

        self.statusChanged.emit(
            "Loading Tree..."
        )

        self.tree_timeout_timer.start(
            self.timeout_ms()
        )

    def on_tree_loaded(
            self,
            tree_data
    ):

        self.treeLoaded.emit(
            tree_data
        )

    def on_tree_worker_error(
            self,
            message
    ):

        self.errorOccurred.emit(
            "Load Tree Error",
            str(message)
        )

    def on_tree_worker_finished(self):

        self.tree_timeout_timer.stop()

        self.busyChanged.emit(
            self.is_busy()
        )

        if self.tree_worker.timed_out():
            return

        if self.manager.is_connected():

            self.statusChanged.emit(
                "Ready"
            )

        else:

            self.statusChanged.emit(
                "Disconnected"
            )

    # =====================================================
    # OperationWorker Slots
    # =====================================================

    def on_operation_started(self):

        self.busyChanged.emit(
            True
        )

        self.operation_timeout_timer.start(
            self.timeout_ms()
        )

        operation = self.operation_worker.operation

        if operation == "connect":

            self.statusChanged.emit(
                "Connecting..."
            )

        elif operation == "open_tree":

            self.statusChanged.emit(
                "Opening Tree..."
            )

        elif operation == "switch_shot":

            self.statusChanged.emit(
                "Switching shot..."
            )

    def on_operation_finished(
            self,
            operation,
            result
    ):

        if operation == "connect":

            connected = bool(
                result
            )

            self.connectionChanged.emit(
                connected
            )

            if not connected:
                self.pending_auto_open = False
                self.pending_tree = ""
                self.pending_shot = -1
                self.pending_load_tree = False

                self.errorOccurred.emit(
                    "Connection Error",
                    self.manager.last_error
                    or
                    "Failed to connect MDSplus server."
                )

                return

            self.statusChanged.emit(
                "Connected"
            )

            if (
                    self.pending_auto_open
                    and
                    self.pending_tree
            ):
                self.pending_auto_open = False

                QTimer.singleShot(
                    0,
                    self.start_pending_tree_open
                )

        elif operation == "open_tree":

            opened = bool(
                result
            )

            if not opened:
                self.pending_load_tree = False

                self.errorOccurred.emit(
                    "Open Tree Error",
                    self.manager.last_error
                    or
                    "Failed to open Tree."
                )

                return

            self.treeOpened.emit(
                self.manager.tree(),
                self.manager.shot()
            )

            if self.pending_load_tree:
                self.pending_load_tree = False

                QTimer.singleShot(
                    0,
                    self.load_tree
                )

        elif operation == "switch_shot":

            self.handle_switch_shot_result(
                result
            )

    # =====================================================
    # ShotParameterWorker Slots
    # =====================================================

    def on_parameter_worker_started(self):

        self.busyChanged.emit(
            True
        )

        self.statusChanged.emit(
            "Loading current shot parameters..."
        )

    def on_shot_parameters_loaded(
            self,
            result
    ):

        self.shotParametersLoaded.emit(
            result
        )

    def on_shot_parameters_error(
            self,
            message
    ):

        self.shotParametersError.emit(
            str(
                message
            )
        )

    def on_parameter_worker_finished(self):

        self.busyChanged.emit(
            self.is_busy()
        )

        if self.manager.is_connected():

            self.statusChanged.emit(
                "Ready"
            )

        else:

            self.statusChanged.emit(
                "Disconnected"
            )

    # =====================================================
    # MultiShotWorker Slots
    # =====================================================

    def on_compare_started(
            self,
            request
    ):

        self.busyChanged.emit(
            True
        )

        self.statusChanged.emit(
            "Comparing multiple shots..."
        )

        self.compareStarted.emit(
            request
        )

    def on_compare_shot_started(
            self,
            shot,
            current,
            total
    ):

        self.statusChanged.emit(
            "Reading Shot {} ({}/{})".format(
                shot,
                current,
                total
            )
        )

        self.compareShotStarted.emit(
            shot,
            current,
            total
        )

    def on_compare_shot_finished(
            self,
            item
    ):

        self.compareShotFinished.emit(
            item
        )

    def on_compare_progress_changed(
            self,
            completed,
            total
    ):

        self.compareProgressChanged.emit(
            completed,
            total
        )

    def on_compare_finished(
            self,
            result
    ):

        self.compareFinished.emit(
            result
        )

        if result.cancelled:

            self.statusChanged.emit(
                "Comparison cancelled"
            )

        else:

            self.statusChanged.emit(
                "Comparison completed: "
                "{} success, {} failed".format(
                    result.success_count(),
                    result.failed_count()
                )
            )

    def on_compare_error(
            self,
            message
    ):

        self.compareError.emit(
            str(message)
        )

    def on_compare_worker_finished(self):

        self.busyChanged.emit(
            self.is_busy()
        )

        if self.manager.is_connected():

            if self.compare_worker.timed_out():

                self.statusChanged.emit(
                    "Comparison timed out"
                )

            else:

                self.statusChanged.emit(
                    "Ready"
                )

        else:

            self.statusChanged.emit(
                "Disconnected"
            )

    def start_pending_tree_open(self):

        self.open_tree(
            self.pending_tree,
            self.pending_shot,
            load_after_open=True
        )

    def on_operation_error(
            self,
            operation,
            message
    ):

        if operation == "connect":

            self.pending_auto_open = False
            self.pending_tree = ""
            self.pending_shot = -1
            self.pending_load_tree = False

        elif operation == "open_tree":

            self.pending_load_tree = False

        title_map = {
            "connect": "Connection Error",
            "open_tree": "Open Tree Error",
            "switch_shot": "Shot Error"
        }

        self.errorOccurred.emit(
            title_map.get(
                operation,
                "MDSplus Error"
            ),
            str(message)
        )

    def on_operation_worker_finished(self):

        self.operation_timeout_timer.stop()

        self.busyChanged.emit(
            self.is_busy()
        )

        if self.operation_worker.timed_out():
            return

        if self.manager.is_connected():

            self.statusChanged.emit(
                "Ready"
            )

        else:

            self.statusChanged.emit(
                "Disconnected"
            )

    def on_operation_timeout(self):

        if not self.operation_worker.isRunning():
            return

        operation = self.operation_worker.operation

        timeout = self.timeout()

        self.operation_worker.stop(
            timed_out=True
        )

        message = (
            "{} timed out after {} seconds.".format(
                operation,
                timeout
            )
        )

        self.manager.invalidate_connection(
            message
        )

        self.connectionChanged.emit(
            False
        )

        self.statusChanged.emit(
            "MDSplus operation timed out"
        )

        self.errorOccurred.emit(
            "MDSplus Timeout",
            message + "\nPlease reconnect."
        )

    # =====================================================
    # Timeout Slots
    # =====================================================

    def on_data_timeout(self):

        if not self.data_worker.isRunning():
            return

        timeout = self.timeout()

        self.data_worker.stop(
            timed_out=True
        )

        message = (
            "Signal loading timed out after "
            "{} seconds.".format(
                timeout
            )
        )

        self.manager.invalidate_connection(
            message
        )

        self.current_loading_node = ""
        self.current_load_mode = "primary"

        self.statusChanged.emit(
            "Signal loading timed out"
        )

        self.connectionChanged.emit(
            False
        )

        self.errorOccurred.emit(
            "MDSplus Timeout",
            message + "\nPlease reconnect."
        )

    def on_tree_timeout(self):

        if not self.tree_worker.isRunning():
            return

        timeout = self.timeout()

        self.tree_worker.stop(
            timed_out=True
        )

        message = (
            "Tree loading timed out after "
            "{} seconds.".format(
                timeout
            )
        )

        self.manager.invalidate_connection(
            message
        )

        self.statusChanged.emit(
            "Tree loading timed out"
        )

        self.connectionChanged.emit(
            False
        )

        self.errorOccurred.emit(
            "MDSplus Timeout",
            message + "\nPlease reconnect."
        )

    # =====================================================
    # Worker Control
    # =====================================================

    def request_stop_all_workers(self):
        """
        向所有正在运行的Worker发送停止请求，不等待线程退出。
        """

        workers = [
            self.data_worker,
            self.tree_worker,
            self.operation_worker,
            self.compare_worker,
            self.parameter_worker
        ]

        for worker in workers:

            if worker.isRunning():
                worker.stop()

    def stop_data_worker(
            self,
            timeout=None
    ):

        if timeout is None:
            timeout = self.timeout_ms()

        return self.data_worker.stop_and_wait(
            timeout
        )

    def stop_tree_worker(
            self,
            timeout=None
    ):

        if timeout is None:
            timeout = self.timeout_ms()

        return self.tree_worker.stop_and_wait(
            timeout
        )

    def stop_operation_worker(
            self,
            timeout=None
    ):

        if timeout is None:
            timeout = self.timeout_ms()

        return self.operation_worker.stop_and_wait(
            timeout
        )

    def stop_parameter_worker(
            self,
            timeout=None
    ):

        if timeout is None:
            timeout = self.timeout_ms()

        return self.parameter_worker.stop_and_wait(
            timeout
        )

    def stop_compare_worker(
            self,
            timeout=None
    ):

        if timeout is None:
            # 批量任务恢复Tree时可能需要等待更长时间
            timeout = max(
                self.timeout_ms(),
                5000
            )

        return self.compare_worker.stop_and_wait(
            timeout
        )

    def stop_all_workers(
            self,
            timeout=None
    ):

        if timeout is None:
            timeout = self.timeout_ms()

        data_stopped = self.stop_data_worker(
            timeout
        )

        tree_stopped = self.stop_tree_worker(
            timeout
        )

        operation_stopped = self.stop_operation_worker(
            timeout
        )

        compare_stopped = self.stop_compare_worker(
            max(
                timeout,
                5000
            )
        )

        parameter_stopped = self.stop_parameter_worker(
            timeout
        )

        return (
                data_stopped
                and
                tree_stopped
                and
                operation_stopped
                and
                compare_stopped
                and
                parameter_stopped
        )

    def shutdown(self):
        """
        立即尝试关闭全部后台Worker、Tree和数据库连接。

        如果仍有Worker正在运行，则立即返回False，不等待。
        """
        self.request_stop_all_workers()

        if self.is_busy():
            return False

        self.data_timeout_timer.stop()
        self.tree_timeout_timer.stop()
        self.operation_timeout_timer.stop()

        if self.manager.is_tree_open():
            try:
                self.manager.close_tree()
            except Exception:
                return False

        if self.manager.is_connected():
            try:
                self.manager.disconnect()
            except Exception:
                return False

        return True
