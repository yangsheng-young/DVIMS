# -*- coding: utf-8 -*-

"""
==========================================================
Project : NNBI_database
File    : compare_dialog.py
Author  :
Date    :
Description : Multi-shot comparison dialog
==========================================================
"""

from PySide2.QtCore import (
    Qt,
    Signal,
)

from PySide2.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QSpinBox,
    QPushButton,
    QProgressBar,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QAbstractItemView,
)

from mds.compare_data import CompareRequest


class CompareDialog(QDialog):
    """
    多炮号对比设置窗口。

    功能：
    1. 设置Tree名称
    2. 设置节点路径
    3. 输入多个炮号
    4. 按范围生成炮号
    5. 启动多炮号异步读取
    6. 显示读取进度
    7. 显示每个炮号的成功和失败状态
    8. 取消当前读取任务
    9. 将最终CompareResult发送给主窗口
    """

    compareFinished = Signal(object)

    def __init__(
            self,
            controller,
            config,
            default_node="",
            parent=None
    ):

        super(
            CompareDialog,
            self
        ).__init__(
            parent
        )

        self.controller = controller
        self.config = config

        self.default_node = str(
            default_node
            if default_node is not None
            else ""
        ).strip()

        self.current_request = None
        self.current_result = None

        self._task_running = False

        self.edit_tree = None
        self.edit_node = None
        self.edit_shots = None

        self.spin_start_shot = None
        self.spin_end_shot = None
        self.spin_step = None

        self.btn_generate = None
        self.btn_start = None
        self.btn_cancel = None
        self.btn_close = None
        self.btn_clear = None

        self.progress_bar = None
        self.lbl_progress = None
        self.lbl_summary = None

        self.result_table = None

        self.init_ui()
        self.load_defaults()
        self.create_connections()
        self.update_button_state()

    # =====================================================
    # UI
    # =====================================================

    def init_ui(self):

        self.setWindowTitle(
            "Compare Multiple Shots"
        )

        self.setWindowModality(
            Qt.NonModal
        )

        self.resize(
            760,
            650
        )

        self.setMinimumSize(
            680,
            560
        )

        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        main_layout.setSpacing(
            10
        )

        main_layout.addWidget(
            self.create_source_group()
        )

        main_layout.addWidget(
            self.create_shot_group()
        )

        main_layout.addWidget(
            self.create_progress_group()
        )

        main_layout.addWidget(
            self.create_result_group(),
            1
        )

        main_layout.addLayout(
            self.create_button_layout()
        )

    def create_source_group(self):

        group = QGroupBox(
            "Data Source"
        )

        layout = QGridLayout(
            group
        )

        layout.addWidget(
            QLabel("Tree"),
            0,
            0
        )

        self.edit_tree = QLineEdit()

        self.edit_tree.setPlaceholderText(
            "Example: RFDATA_TREE"
        )

        layout.addWidget(
            self.edit_tree,
            0,
            1
        )

        layout.addWidget(
            QLabel("Node"),
            1,
            0
        )

        self.edit_node = QLineEdit()

        self.edit_node.setPlaceholderText(
            "Example: "
            "\\RFDATA_TREE::TOP.FASTDAQ."
            "SIG_NNBI:NNBI"
        )

        layout.addWidget(
            self.edit_node,
            1,
            1
        )

        layout.setColumnStretch(
            1,
            1
        )

        return group

    def create_shot_group(self):

        group = QGroupBox(
            "Shot List"
        )

        main_layout = QVBoxLayout(
            group
        )

        range_layout = QGridLayout()

        range_layout.addWidget(
            QLabel("Start Shot"),
            0,
            0
        )

        self.spin_start_shot = QSpinBox()

        self.configure_shot_spinbox(
            self.spin_start_shot
        )

        range_layout.addWidget(
            self.spin_start_shot,
            0,
            1
        )

        range_layout.addWidget(
            QLabel("End Shot"),
            0,
            2
        )

        self.spin_end_shot = QSpinBox()

        self.configure_shot_spinbox(
            self.spin_end_shot
        )

        range_layout.addWidget(
            self.spin_end_shot,
            0,
            3
        )

        range_layout.addWidget(
            QLabel("Step"),
            0,
            4
        )

        self.spin_step = QSpinBox()

        self.spin_step.setRange(
            1,
            1000000
        )

        self.spin_step.setValue(
            1
        )

        range_layout.addWidget(
            self.spin_step,
            0,
            5
        )

        self.btn_generate = QPushButton(
            "Generate"
        )

        self.btn_generate.setToolTip(
            "Generate shot list from the range."
        )

        range_layout.addWidget(
            self.btn_generate,
            0,
            6
        )

        range_layout.setColumnStretch(
            6,
            1
        )

        main_layout.addLayout(
            range_layout
        )

        shot_label = QLabel(
            "Shots"
        )

        main_layout.addWidget(
            shot_label
        )

        self.edit_shots = QPlainTextEdit()

        self.edit_shots.setPlaceholderText(
            "Input multiple shots separated by spaces, "
            "commas, semicolons or new lines.\n"
            "Example:\n"
            "49050, 49051, 49052"
        )

        self.edit_shots.setMinimumHeight(
            100
        )

        main_layout.addWidget(
            self.edit_shots
        )

        return group

    def create_progress_group(self):

        group = QGroupBox(
            "Progress"
        )

        layout = QVBoxLayout(
            group
        )

        self.lbl_progress = QLabel(
            "Ready"
        )

        layout.addWidget(
            self.lbl_progress
        )

        self.progress_bar = QProgressBar()

        self.progress_bar.setRange(
            0,
            100
        )

        self.progress_bar.setValue(
            0
        )

        self.progress_bar.setTextVisible(
            True
        )

        layout.addWidget(
            self.progress_bar
        )

        self.lbl_summary = QLabel(
            "Total: 0    Success: 0    Failed: 0"
        )

        layout.addWidget(
            self.lbl_summary
        )

        return group

    def create_result_group(self):

        group = QGroupBox(
            "Result"
        )

        layout = QVBoxLayout(
            group
        )

        self.result_table = QTableWidget()

        self.result_table.setColumnCount(
            5
        )

        self.result_table.setHorizontalHeaderLabels(
            [
                "Shot",
                "Status",
                "Points",
                "Node",
                "Message",
            ]
        )

        self.result_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.result_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.result_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.result_table.setAlternatingRowColors(
            True
        )

        self.result_table.verticalHeader().setVisible(
            False
        )

        header = self.result_table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.Stretch
        )

        layout.addWidget(
            self.result_table
        )

        return group

    def create_button_layout(self):

        layout = QHBoxLayout()

        self.btn_clear = QPushButton(
            "Clear Results"
        )

        self.btn_start = QPushButton(
            "Start Compare"
        )

        self.btn_cancel = QPushButton(
            "Cancel"
        )

        self.btn_close = QPushButton(
            "Close"
        )

        self.btn_start.setDefault(
            True
        )

        layout.addWidget(
            self.btn_clear
        )

        layout.addStretch(
            1
        )

        layout.addWidget(
            self.btn_start
        )

        layout.addWidget(
            self.btn_cancel
        )

        layout.addWidget(
            self.btn_close
        )

        return layout

    # =====================================================
    # SpinBox
    # =====================================================

    @staticmethod
    def configure_shot_spinbox(
            spinbox
    ):

        spinbox.setRange(
            -2147483647,
            2147483647
        )

        spinbox.setValue(
            -1
        )

    # =====================================================
    # Defaults
    # =====================================================

    def load_defaults(self):

        tree = ""

        if self.controller is not None:

            try:

                tree = self.controller.tree()

            except Exception:

                tree = ""

        if not tree:
            tree = str(
                getattr(
                    self.config,
                    "tree",
                    ""
                )
            ).strip()

        self.edit_tree.setText(
            tree
        )

        self.edit_node.setText(
            self.default_node
        )

        shot = -1

        if self.controller is not None:

            try:

                current_shot = (
                    self.controller.shot()
                )

                if current_shot is not None:
                    shot = int(
                        current_shot
                    )

            except Exception:

                shot = -1

        if shot == -1:

            try:

                shot = int(
                    getattr(
                        self.config,
                        "shot",
                        -1
                    )
                )

            except Exception:

                shot = -1

        self.spin_start_shot.setValue(
            shot
        )

        self.spin_end_shot.setValue(
            shot
        )

        if shot != -1:
            self.edit_shots.setPlainText(
                str(shot)
            )

    # =====================================================
    # Connections
    # =====================================================

    def create_connections(self):

        self.btn_generate.clicked.connect(
            self.generate_shot_list
        )

        self.btn_start.clicked.connect(
            self.start_compare
        )

        self.btn_cancel.clicked.connect(
            self.cancel_compare
        )

        self.btn_clear.clicked.connect(
            self.clear_results
        )

        self.btn_close.clicked.connect(
            self.close
        )

        if self.controller is None:
            return

        self.controller.compareStarted.connect(
            self.on_compare_started
        )

        self.controller.compareShotStarted.connect(
            self.on_shot_started
        )

        self.controller.compareShotFinished.connect(
            self.on_shot_finished
        )

        self.controller.compareProgressChanged.connect(
            self.on_progress_changed
        )

        self.controller.compareFinished.connect(
            self.on_compare_finished
        )

        self.controller.compareError.connect(
            self.on_compare_error
        )

    # =====================================================
    # Shot List
    # =====================================================

    def generate_shot_list(self):

        start_shot = (
            self.spin_start_shot.value()
        )

        end_shot = (
            self.spin_end_shot.value()
        )

        step = (
            self.spin_step.value()
        )

        if start_shot <= end_shot:

            shots = range(
                start_shot,
                end_shot + 1,
                step
            )

        else:

            shots = range(
                start_shot,
                end_shot - 1,
                -step
            )

        shot_text = ", ".join(
            str(shot)
            for shot in shots
        )

        self.edit_shots.setPlainText(
            shot_text
        )

    def build_request(self):

        tree = self.edit_tree.text().strip()

        node = self.edit_node.text().strip()

        shot_text = (
            self.edit_shots.toPlainText()
        )

        request = CompareRequest(
            tree=tree,
            node=node,
            shots=shot_text
        )

        valid, message = (
            request.validate()
        )

        if not valid:
            QMessageBox.warning(
                self,
                "Compare",
                message
            )

            return None

        return request

    # =====================================================
    # Start and Cancel
    # =====================================================

    def start_compare(self):

        if self._task_running:
            return

        if self.controller is None:
            QMessageBox.warning(
                self,
                "Compare",
                "MDSplus controller is not available."
            )

            return

        if not self.controller.is_connected():
            QMessageBox.warning(
                self,
                "Compare",
                "MDSplus server is not connected."
            )

            return

        request = self.build_request()

        if request is None:
            return

        self.current_request = request
        self.current_result = None

        self.clear_results(
            reset_inputs=False
        )

        started = (
            self.controller.start_compare(
                request
            )
        )

        if not started:
            QMessageBox.warning(
                self,
                "Compare",
                "Unable to start the comparison task. "
                "Another MDSplus operation may be running."
            )

    def cancel_compare(self):

        if not self._task_running:
            return

        reply = QMessageBox.question(
            self,
            "Cancel Compare",
            "Cancel the current comparison task?\n\n"
            "The current MDSplus database call cannot be "
            "interrupted immediately. The task will stop "
            "after the current call returns.",
            QMessageBox.Yes |
            QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.controller.cancel_compare()

        self.lbl_progress.setText(
            "Cancelling..."
        )

        self.btn_cancel.setEnabled(
            False
        )

    # =====================================================
    # Worker Slots
    # =====================================================

    def on_compare_started(
            self,
            request
    ):

        self._task_running = True
        self.current_request = request

        self.progress_bar.setValue(
            0
        )

        self.lbl_progress.setText(
            "Comparison started"
        )

        self.update_summary(
            total=request.shot_count(),
            success=0,
            failed=0
        )

        self.update_button_state()

    def on_shot_started(
            self,
            shot,
            current,
            total
    ):

        self.lbl_progress.setText(
            "Reading Shot {} ({}/{})".format(
                shot,
                current,
                total
            )
        )

    def on_shot_finished(
            self,
            item
    ):

        self.append_result_row(
            item
        )

    def on_progress_changed(
            self,
            completed,
            total
    ):

        if total <= 0:
            percent = 0
        else:
            percent = int(
                completed
                *
                100
                /
                total
            )

        self.progress_bar.setValue(
            percent
        )

        success = 0
        failed = 0

        for row in range(
                self.result_table.rowCount()
        ):

            status_item = (
                self.result_table.item(
                    row,
                    1
                )
            )

            if status_item is None:
                continue

            status = status_item.text()

            if status == "Success":
                success += 1
            elif status == "Failed":
                failed += 1

        self.update_summary(
            total=total,
            success=success,
            failed=failed
        )

    def on_compare_finished(
            self,
            result
    ):

        self._task_running = False
        self.current_result = result

        self.progress_bar.setValue(
            100
            if not result.cancelled
            else
            self.progress_bar.value()
        )

        if result.cancelled:

            self.lbl_progress.setText(
                "Comparison cancelled"
            )

        else:

            self.lbl_progress.setText(
                "Comparison completed"
            )

        self.update_summary(
            total=result.total_count(),
            success=result.success_count(),
            failed=result.failed_count()
        )

        self.update_button_state()

        if not result.restore_success:
            QMessageBox.warning(
                self,
                "Tree Restore Error",
                result.restore_error
                or
                "Failed to restore the previous Tree."
            )

        self.compareFinished.emit(
            result
        )

    def on_compare_error(
            self,
            message
    ):

        self._task_running = False

        self.lbl_progress.setText(
            "Comparison error"
        )

        self.update_button_state()

        QMessageBox.critical(
            self,
            "Compare Error",
            str(message)
        )

    # =====================================================
    # Result Table
    # =====================================================

    def append_result_row(
            self,
            item
    ):

        row = self.result_table.rowCount()

        self.result_table.insertRow(
            row
        )

        shot_item = QTableWidgetItem(
            str(item.shot)
        )

        if item.success:

            status_text = "Success"
            points_text = str(
                item.point_count()
            )
            message_text = ""

        else:

            status_text = "Failed"
            points_text = "0"
            message_text = item.error

        status_item = QTableWidgetItem(
            status_text
        )

        points_item = QTableWidgetItem(
            points_text
        )

        node_item = QTableWidgetItem(
            item.node
        )

        message_item = QTableWidgetItem(
            message_text
        )

        shot_item.setTextAlignment(
            Qt.AlignCenter
        )

        status_item.setTextAlignment(
            Qt.AlignCenter
        )

        points_item.setTextAlignment(
            Qt.AlignCenter
        )

        self.result_table.setItem(
            row,
            0,
            shot_item
        )

        self.result_table.setItem(
            row,
            1,
            status_item
        )

        self.result_table.setItem(
            row,
            2,
            points_item
        )

        self.result_table.setItem(
            row,
            3,
            node_item
        )

        self.result_table.setItem(
            row,
            4,
            message_item
        )

        self.result_table.scrollToBottom()

    def clear_results(
            self,
            reset_inputs=False
    ):

        if self._task_running:
            return

        self.result_table.setRowCount(
            0
        )

        self.progress_bar.setValue(
            0
        )

        self.lbl_progress.setText(
            "Ready"
        )

        self.lbl_summary.setText(
            "Total: 0    Success: 0    Failed: 0"
        )

        self.current_result = None

        if reset_inputs:
            self.edit_shots.clear()

    def update_summary(
            self,
            total,
            success,
            failed
    ):

        self.lbl_summary.setText(
            "Total: {}    Success: {}    Failed: {}".format(
                total,
                success,
                failed
            )
        )

    # =====================================================
    # Button State
    # =====================================================

    def update_button_state(self):

        running = bool(
            self._task_running
        )

        self.edit_tree.setEnabled(
            not running
        )

        self.edit_node.setEnabled(
            not running
        )

        self.edit_shots.setEnabled(
            not running
        )

        self.spin_start_shot.setEnabled(
            not running
        )

        self.spin_end_shot.setEnabled(
            not running
        )

        self.spin_step.setEnabled(
            not running
        )

        self.btn_generate.setEnabled(
            not running
        )

        self.btn_start.setEnabled(
            not running
        )

        self.btn_cancel.setEnabled(
            running
        )

        self.btn_clear.setEnabled(
            not running
        )

        self.btn_close.setEnabled(
            not running
        )

    # =====================================================
    # Node
    # =====================================================

    def set_node(
            self,
            node
    ):

        if node is None:
            node = ""

        self.edit_node.setText(
            str(node).strip()
        )

    # =====================================================
    # Close
    # =====================================================

    def reject(self):

        if self._task_running:
            QMessageBox.information(
                self,
                "Compare",
                "The comparison task is still running. "
                "Cancel it before closing this window."
            )

            return

        super(
            CompareDialog,
            self
        ).reject()

    def closeEvent(
            self,
            event
    ):

        if self._task_running:
            QMessageBox.information(
                self,
                "Compare",
                "The comparison task is still running. "
                "Cancel it before closing this window."
            )

            event.ignore()

            return

        event.accept()
