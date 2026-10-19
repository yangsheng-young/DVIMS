# -*- coding: utf-8 -*-

"""
-------------------------------------------------
Project : NNBI_database
File    : worker.py
Author  :
Date    :
Description : MDSplus Data Worker
-------------------------------------------------
"""
import time

from PySide2.QtCore import (
    QThread,
    Signal,
)

from mds.compare_data import (
    CompareRequest,
    CompareResult,
)


class DataWorker(QThread):
    """
    MDSplus信号数据读取线程

    所有数据库读取统一通过MDSManager完成。
    """

    data_loaded = Signal(object)
    error = Signal(str)

    def __init__(
            self,
            manager,
            parent=None
    ):

        super(DataWorker, self).__init__(
            parent
        )

        self.manager = manager
        self.node = ""

        # 每次任务启动时固定查询参数，防止运行中参数变化
        # 影响正在执行的数据库读取。
        self.query_options = None
        self.active_query_options = None

        self._running = False
        self._stopping = False

        self._start_time = None
        self._timed_out = False

    # =====================================================
    # Parameter
    # =====================================================

    def set_node(
            self,
            node
    ):

        if node is None:
            self.node = ""
        else:
            self.node = str(node).strip()

    def current_node(self):

        return self.node

    def set_query_options(
            self,
            downsample_enabled=None,
            max_points=None
    ):
        """
        设置下一次DataWorker任务使用的查询参数。

        None表示任务启动时读取MDSManager的当前默认值。
        """

        if (
                downsample_enabled is None
                and
                max_points is None
        ):
            self.query_options = None

            return

        options = self.manager.query_options()

        if downsample_enabled is not None:
            options["downsample_enabled"] = bool(
                downsample_enabled
            )

        if max_points is not None:

            try:
                max_points = int(
                    max_points
                )
            except Exception:
                max_points = options["max_points"]

            options["max_points"] = max(
                100,
                max_points
            )

        self.query_options = options

    def current_query_options(self):

        if self.active_query_options is not None:
            return dict(
                self.active_query_options
            )

        if self.query_options is not None:
            return dict(
                self.query_options
            )

        return self.manager.query_options()

    # =====================================================
    # Start
    # =====================================================

    def start_loading(
            self,
            node=None,
            downsample_enabled=None,
            max_points=None
    ):

        if self.isRunning():
            return False

        if node is not None:
            self.set_node(node)

        if self.node == "":
            return False

        self.set_query_options(
            downsample_enabled=downsample_enabled,
            max_points=max_points
        )

        if self.query_options is None:
            self.active_query_options = (
                self.manager.query_options()
            )
        else:
            self.active_query_options = dict(
                self.query_options
            )

        self._running = True
        self._stopping = False
        self._timed_out = False
        self._start_time = time.monotonic()

        self.start()

        return True

    def check_timeout(self):
        """
        判断当前读取是否超过配置时间
        """

        if self._start_time is None:
            return False

        timeout = self.manager.timeout()

        elapsed = (
                time.monotonic()
                -
                self._start_time
        )

        return elapsed >= timeout

    # =====================================================
    # Thread
    # =====================================================

    def run(self):

        try:

            if self.node == "":
                raise RuntimeError(
                    "Node is empty."
                )

            if self.should_stop():
                return

            options = (
                    self.active_query_options
                    or
                    self.manager.query_options()
            )

            signal_data = self.manager.load_signal(
                self.node,
                downsample_enabled=options.get(
                    "downsample_enabled"
                ),
                max_points=options.get(
                    "max_points"
                )
            )

            if self.should_stop():
                return

            if signal_data is None:
                raise RuntimeError(
                    "Signal loading returned no data."
                )

            self.data_loaded.emit(
                signal_data
            )

        except Exception as error:

            if not self.should_stop():
                self.error.emit(
                    str(error)
                )

        finally:

            self._running = False
            self._stopping = False
            self.active_query_options = None

    # =====================================================
    # Control
    # =====================================================

    def should_stop(self):

        return (
                not self._running
                or self._stopping
                or self.isInterruptionRequested()
        )

    def stop(
            self,
            timed_out=False
    ):
        """
        请求停止线程
        """

        self._timed_out = bool(
            timed_out
        )

        self._stopping = True
        self._running = False

        self.requestInterruption()

    def stop_and_wait(
            self,
            timeout=3000
    ):

        if not self.isRunning():
            return True

        self.stop()

        try:
            timeout = int(timeout)
        except Exception:
            timeout = 3000

        if timeout < 0:
            timeout = 0

        return bool(
            self.wait(timeout)
        )

    def is_running(self):

        return self.isRunning()

    def timed_out(self):

        return self._timed_out

    # =====================================================
    # Reserved Interface
    # =====================================================

    def load_history(self):

        pass

    def load_multiple_nodes(self):

        pass

    def load_realtime(self):

        pass


class MultiShotWorker(QThread):
    """
    多炮号Signal异步读取线程。

    功能：
    1. 接收CompareRequest
    2. 保存当前Tree状态
    3. 依次打开多个Shot
    4. 读取同一个Node的SignalData
    5. 单炮号失败时继续读取下一炮
    6. 实时发送进度和单炮结果
    7. 任务结束后恢复原Tree状态
    8. 支持停止请求

    注意：
    MDSplus底层阻塞调用不能被QThread强制中断。
    stop()只能阻止后续炮号继续读取，并在当前数据库调用
    返回后结束线程。
    """

    # 开始执行整个对比任务
    compare_started = Signal(object)

    # 开始读取一个炮号
    # 参数：shot, 当前序号, 总炮数
    shot_started = Signal(
        int,
        int,
        int
    )

    # 单炮号读取完成
    # 参数：CompareShotResult
    shot_finished = Signal(object)

    # 当前任务进度
    # 参数：已完成数量, 总炮数
    progress_changed = Signal(
        int,
        int
    )

    # 整个对比任务完成
    # 参数：CompareResult
    compare_finished = Signal(object)

    # 任务级错误
    error = Signal(str)

    def __init__(
            self,
            manager,
            parent=None
    ):

        super(MultiShotWorker, self).__init__(parent)

        self.manager = manager

        self.request = None
        self.result = None

        # 整个多炮任务共用同一份查询参数快照。
        self.query_options = None
        self.active_query_options = None

        self.original_tree_state = None

        self._running = False
        self._stopping = False
        self._timed_out = False

        self._start_time = None
        self._current_shot = None

    # =====================================================
    # Request
    # =====================================================

    def set_request(
            self,
            request
    ):
        """
        设置多炮号对比请求。
        """

        if not isinstance(
                request,
                CompareRequest
        ):
            raise TypeError(
                "request must be CompareRequest."
            )

        self.request = request.copy()

    def current_request(self):

        if self.request is None:
            return None

        return self.request.copy()

    def current_result(self):

        return self.result

    def current_shot(self):

        return self._current_shot

    def set_query_options(
            self,
            downsample_enabled=None,
            max_points=None
    ):
        """
        设置下一次多炮任务使用的查询参数。
        """

        if (
                downsample_enabled is None
                and
                max_points is None
        ):
            self.query_options = None

            return

        options = self.manager.query_options()

        if downsample_enabled is not None:
            options["downsample_enabled"] = bool(
                downsample_enabled
            )

        if max_points is not None:

            try:
                max_points = int(
                    max_points
                )
            except Exception:
                max_points = options["max_points"]

            options["max_points"] = max(
                100,
                max_points
            )

        self.query_options = options

    def current_query_options(self):

        if self.active_query_options is not None:
            return dict(
                self.active_query_options
            )

        if self.query_options is not None:
            return dict(
                self.query_options
            )

        return self.manager.query_options()

    # =====================================================
    # Start
    # =====================================================

    def start_compare(
            self,
            request=None,
            downsample_enabled=None,
            max_points=None
    ):
        """
        启动多炮号读取任务。

        Parameters
        ----------
        request : CompareRequest or None

        Returns
        -------
        bool
            是否成功启动线程。
        """

        if self.isRunning():
            return False

        if request is not None:

            try:

                self.set_request(
                    request
                )

            except Exception as error:

                self.error.emit(
                    str(error)
                )

                return False

        if self.request is None:
            self.error.emit(
                "Compare request is not available."
            )

            return False

        valid, message = (
            self.request.validate()
        )

        if not valid:
            self.error.emit(
                message
            )

            return False

        if self.manager is None:
            self.error.emit(
                "MDSplus manager is not available."
            )

            return False

        if not self.manager.is_connected():
            self.error.emit(
                "MDSplus server is not connected."
            )

            return False

        self.set_query_options(
            downsample_enabled=downsample_enabled,
            max_points=max_points
        )

        if self.query_options is None:
            self.active_query_options = (
                self.manager.query_options()
            )
        else:
            self.active_query_options = dict(
                self.query_options
            )

        self.result = CompareResult(
            self.request
        )

        self.original_tree_state = None

        self._running = True
        self._stopping = False
        self._timed_out = False

        self._current_shot = None
        self._start_time = time.monotonic()

        self.start()

        return True

    # =====================================================
    # Thread
    # =====================================================

    def run(self):
        """
        后台执行多炮号读取。
        """

        request = self.request

        if request is None:
            self._running = False

            self.error.emit(
                "Compare request is not available."
            )

            return

        result = self.result

        if result is None:
            result = CompareResult(
                request
            )

            self.result = result

        task_failed = False

        self.compare_started.emit(
            request.copy()
        )

        try:

            self.original_tree_state = (
                self.manager.capture_tree_state()
            )

            total = request.shot_count()

            self.progress_changed.emit(
                0,
                total
            )

            for index, shot in enumerate(
                    request.shots
            ):

                if self.should_stop():
                    result.cancelled = True

                    break

                self._current_shot = shot

                self.shot_started.emit(
                    int(shot),
                    int(index + 1),
                    int(total)
                )

                try:

                    signal_data = (
                        self.manager.load_compare_signal(
                            request.tree,
                            shot,
                            request.node,
                            downsample_enabled=(
                                self.active_query_options.get(
                                    "downsample_enabled"
                                )
                            ),
                            max_points=(
                                self.active_query_options.get(
                                    "max_points"
                                )
                            )
                        )
                    )

                    if self.should_stop():
                        result.cancelled = True

                        break

                    item = result.add_success(
                        shot,
                        signal_data
                    )

                except Exception as error:

                    if self.should_stop():
                        result.cancelled = True

                        break

                    item = result.add_error(
                        shot,
                        str(error)
                    )

                self.shot_finished.emit(
                    item
                )

                self.progress_changed.emit(
                    result.completed_count(),
                    total
                )

        except Exception as error:

            if not self.should_stop():
                task_failed = True

                self.error.emit(
                    str(error)
                )

        finally:

            self.restore_original_tree(
                result
            )

            self._current_shot = None
            self._running = False
            self._stopping = False
            self.active_query_options = None

            if not task_failed:
                self.compare_finished.emit(
                    result
                )

    # =====================================================
    # Tree Restore
    # =====================================================

    def restore_original_tree(
            self,
            result
    ):
        """
        恢复任务开始前的Tree状态。
        """

        if result is None:
            return False

        if self.original_tree_state is None:
            result.set_restore_error(
                "Original Tree state is not available."
            )

            return False

        try:

            restored, message = (
                self.manager.restore_tree_state(
                    self.original_tree_state
                )
            )

            if not restored:
                result.set_restore_error(
                    message
                    or
                    "Failed to restore previous Tree."
                )

                return False

            return True

        except Exception as error:

            result.set_restore_error(
                str(error)
            )

            return False

    # =====================================================
    # Control
    # =====================================================

    def should_stop(self):

        return (
                not self._running
                or
                self._stopping
                or
                self.isInterruptionRequested()
        )

    def stop(
            self,
            timed_out=False
    ):
        """
        请求停止多炮号任务。

        当前正在执行的MDSplus调用不会被强制终止。
        当前调用返回后，Worker不会继续读取下一炮。
        """

        self._timed_out = bool(
            timed_out
        )

        self._stopping = True
        self._running = False

        self.requestInterruption()

    def stop_and_wait(
            self,
            timeout=5000
    ):

        if not self.isRunning():
            return True

        self.stop()

        try:

            timeout = int(
                timeout
            )

        except Exception:

            timeout = 5000

        if timeout < 0:
            timeout = 0

        return bool(
            self.wait(
                timeout
            )
        )

    # =====================================================
    # Status
    # =====================================================

    def is_running(self):

        return self.isRunning()

    def timed_out(self):

        return self._timed_out

    def elapsed_time(self):

        if self._start_time is None:
            return 0.0

        return max(
            0.0,
            time.monotonic()
            -
            self._start_time
        )

    def completed_count(self):

        if self.result is None:
            return 0

        return self.result.completed_count()

    def total_count(self):

        if self.request is None:
            return 0

        return self.request.shot_count()

    def progress_percent(self):

        total = self.total_count()

        if total <= 0:
            return 0

        completed = self.completed_count()

        return int(
            completed
            *
            100
            /
            total
        )


class MDSOperationWorker(QThread):
    """
    MDSplus通用操作线程

    支持：
    connect
    open_tree
    switch_shot
    """

    operation_finished = Signal(str, object)
    error = Signal(str, str)

    def __init__(
            self,
            manager,
            parent=None
    ):

        super(MDSOperationWorker, self).__init__(
            parent
        )

        self.manager = manager

        self.operation = ""
        self.parameters = {}

        self._timed_out = False
        self._stopping = False

    def start_operation(
            self,
            operation,
            **parameters
    ):

        if self.isRunning():
            return False

        operation = str(
            operation
        ).strip()

        if operation == "":
            return False

        self.operation = operation
        self.parameters = dict(
            parameters
        )

        self._timed_out = False
        self._stopping = False

        self.start()

        return True

    def run(self):

        try:

            if self.operation == "connect":

                result = self.manager.connect(
                    self.parameters.get(
                        "host",
                        ""
                    ),
                    self.parameters.get(
                        "port",
                        "8000"
                    )
                )

            elif self.operation == "open_tree":

                result = self.manager.open_tree(
                    self.parameters.get(
                        "tree",
                        ""
                    ),
                    self.parameters.get(
                        "shot",
                        -1
                    )
                )

            elif self.operation == "switch_shot":

                result = self.manager.switch_shot(
                    self.parameters.get(
                        "tree",
                        ""
                    ),
                    self.parameters.get(
                        "shot",
                        -1
                    )
                )

            else:

                raise RuntimeError(
                    "Unsupported MDSplus operation: {}".format(
                        self.operation
                    )
                )

            if self._stopping:
                return

            self.operation_finished.emit(
                self.operation,
                result
            )

        except Exception as error:

            if not self._stopping:
                self.error.emit(
                    self.operation,
                    str(error)
                )

    def stop(
            self,
            timed_out=False
    ):

        self._timed_out = bool(
            timed_out
        )

        self._stopping = True

        self.requestInterruption()

    def stop_and_wait(
            self,
            timeout=5000
    ):

        if not self.isRunning():
            return True

        self.stop()

        try:
            timeout = int(
                timeout
            )
        except Exception:
            timeout = 5000

        if timeout < 0:
            timeout = 0

        return bool(
            self.wait(
                timeout
            )
        )

    def timed_out(self):

        return self._timed_out


class TreeWorker(QThread):
    """
    MDSplus Tree结构读取线程

    Tree的GETNCI递归查询在后台线程中执行，
    避免阻塞主界面线程。
    """

    tree_loaded = Signal(object)
    error = Signal(str)

    def __init__(
            self,
            manager,
            parent=None
    ):

        super(TreeWorker, self).__init__(
            parent
        )

        self.manager = manager

        self._running = False
        self._stopping = False
        self._start_time = None
        self._timed_out = False

    # =====================================================
    # Start
    # =====================================================

    def start_loading(self):

        if self.isRunning():
            return False

        if self.manager is None:
            return False

        if not self.manager.is_connected():
            return False

        if not self.manager.is_tree_open():
            return False

        self._running = True
        self._stopping = False
        self._timed_out = False
        self._start_time = time.monotonic()

        self.start()

        return True

    # =====================================================
    # Thread
    # =====================================================

    def run(self):

        try:

            if self.should_stop():
                return

            tree_data = self.manager.load_tree(
                stop_checker=self.should_stop
            )

            if self.should_stop():
                return

            if tree_data is None:
                raise RuntimeError(
                    "Tree data is empty."
                )

            self.tree_loaded.emit(
                tree_data
            )

        except Exception as error:

            if not self.should_stop():
                self.error.emit(
                    str(error)
                )

        finally:

            self._running = False
            self._stopping = False

    # =====================================================
    # Control
    # =====================================================

    def should_stop(self):

        return (
                not self._running
                or self._stopping
                or self.isInterruptionRequested()
        )

    def stop(
            self,
            timed_out=False
    ):

        self._timed_out = bool(
            timed_out
        )

        self._stopping = True
        self._running = False

        self.requestInterruption()

    def stop_and_wait(
            self,
            timeout=5000
    ):

        if not self.isRunning():
            return True

        self.stop()

        try:
            timeout = int(timeout)
        except Exception:
            timeout = 5000

        if timeout < 0:
            timeout = 0

        return bool(
            self.wait(timeout)
        )

    def is_running(self):

        return self.isRunning()

    def timed_out(self):

        return self._timed_out


class ShotParameterWorker(QThread):
    """
    当前炮号参数读取线程。
    """

    parameters_loaded = Signal(object)
    error = Signal(str)

    def __init__(
            self,
            manager,
            parent=None
    ):

        super(ShotParameterWorker, self).__init__(
            parent
        )

        self.manager = manager
        self.parameter_definitions = {}

        self._running = False
        self._stopping = False

    def start_loading(
            self,
            definitions=None
    ):

        if self.isRunning():
            return False

        self.parameter_definitions = dict(
            definitions
            or
            {}
        )

        self._running = True
        self._stopping = False

        self.start()

        return True

    def run(self):

        try:

            if self.should_stop():
                return

            result = self.manager.load_shot_parameters(
                self.parameter_definitions
            )

            if self.should_stop():
                return

            self.parameters_loaded.emit(
                result
            )

        except Exception as error:

            if not self.should_stop():
                self.error.emit(
                    str(
                        error
                    )
                )

        finally:

            self._running = False
            self._stopping = False

    def should_stop(self):

        return (
                not self._running
                or
                self._stopping
        )

    def stop(
            self,
            timed_out=False
    ):

        self._stopping = True
        self._running = False
        self.requestInterruption()

    def stop_and_wait(
            self,
            timeout=5000
    ):

        if not self.isRunning():
            return True

        self.stop()

        return self.wait(
            int(
                timeout
            )
        )
