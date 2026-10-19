# -*- coding: utf-8 -*-

"""
==========================================================
Project : NNBI_database
File    : connect_dialog.py
Author  :
Date    :
==========================================================
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QSpinBox,
    QCheckBox,
    QPushButton,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QMessageBox
)


class ConnectDialog(QDialog):
    """
    MDSplus连接设置窗口
    """

    def __init__(self, config, parent=None):

        super(ConnectDialog, self).__init__(parent)

        self.config = config

        self.init_ui()

        self.load_config()

        self.init_signal()

    # =====================================================
    # UI
    # =====================================================

    def init_ui(self):

        self.setWindowTitle("Connect MDSplus")

        self.setWindowModality(Qt.ApplicationModal)

        self.setMinimumWidth(420)

        self.setMinimumHeight(260)

        # =================================================
        # Host
        # =================================================

        self.label_host = QLabel("Host")

        self.edit_host = QLineEdit()

        # =================================================
        # Port
        # =================================================

        self.label_port = QLabel("Port")

        self.spin_port = QSpinBox()

        self.spin_port.setRange(1, 65535)

        # =================================================
        # Tree
        # =================================================

        self.label_tree = QLabel("Tree")

        self.edit_tree = QLineEdit()

        # =================================================
        # Shot
        # =================================================

        self.label_shot = QLabel("Shot")

        self.spin_shot = QSpinBox()

        self.spin_shot.setRange(-1, 999999999)

        # =================================================
        # Options
        # =================================================

        self.check_auto_connect = QCheckBox(
            "Auto Connect"
        )

        self.check_auto_open_tree = QCheckBox(
            "Auto Open Tree"
        )

        # =================================================
        # Button
        # =================================================

        self.button_ok = QPushButton("OK")

        self.button_cancel = QPushButton("Cancel")

        # =================================================
        # Group
        # =================================================

        self.group_connection = QGroupBox(
            "Connection"
        )

        grid = QGridLayout()

        grid.addWidget(self.label_host, 0, 0)
        grid.addWidget(self.edit_host, 0, 1)

        grid.addWidget(self.label_port, 1, 0)
        grid.addWidget(self.spin_port, 1, 1)

        grid.addWidget(self.label_tree, 2, 0)
        grid.addWidget(self.edit_tree, 2, 1)

        grid.addWidget(self.label_shot, 3, 0)
        grid.addWidget(self.spin_shot, 3, 1)

        grid.addWidget(
            self.check_auto_connect,
            4,
            0,
            1,
            2
        )

        grid.addWidget(
            self.check_auto_open_tree,
            5,
            0,
            1,
            2
        )

        self.group_connection.setLayout(grid)

        # =================================================
        # Bottom Button
        # =================================================

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        button_layout.addWidget(self.button_ok)

        button_layout.addWidget(self.button_cancel)

        # =================================================
        # Main Layout
        # =================================================

        layout = QVBoxLayout()

        layout.addWidget(self.group_connection)

        layout.addStretch()

        layout.addLayout(button_layout)

        self.setLayout(layout)

    # =====================================================
    # Signal
    # =====================================================

    def init_signal(self):

        self.button_ok.clicked.connect(
            self.accept
        )

        self.button_cancel.clicked.connect(
            self.reject
        )

    # =====================================================
    # Load Config
    # =====================================================

    def load_config(self):

        self.edit_host.setText(
            self.config.host
        )

        self.spin_port.setValue(
            self.config.port
        )

        self.edit_tree.setText(
            self.config.tree
        )

        self.spin_shot.setValue(
            self.config.shot
        )

        self.check_auto_connect.setChecked(
            self.config.auto_connect
        )

        self.check_auto_open_tree.setChecked(
            self.config.auto_open_tree
        )

    # =====================================================
    # Save Config
    # =====================================================

    def save_config(self):

        self.config.host = self.edit_host.text().strip()

        self.config.port = self.spin_port.value()

        self.config.tree = self.edit_tree.text().strip()

        self.config.shot = self.spin_shot.value()

        self.config.auto_connect = (
            self.check_auto_connect.isChecked()
        )

        self.config.auto_open_tree = (
            self.check_auto_open_tree.isChecked()
        )

        if self.config.auto_open_tree:
            self.config.auto_connect = True

        self.config.save()

    # =====================================================
    # Check Input
    # =====================================================

    def check_input(self):

        if self.edit_host.text().strip() == "":
            QMessageBox.warning(
                self,
                "Warning",
                "Host cannot be empty."
            )

            self.edit_host.setFocus()

            return False

        if self.edit_tree.text().strip() == "":
            QMessageBox.warning(
                self,
                "Warning",
                "Tree name cannot be empty."
            )

            self.edit_tree.setFocus()

            return False

        return True

    # =====================================================
    # Accept
    # =====================================================

    def accept(self):

        if not self.check_input():
            return

        self.save_config()

        super(
            ConnectDialog,
            self
        ).accept()

    # =====================================================
    # Reject
    # =====================================================

    def reject(self):

        super(
            ConnectDialog,
            self
        ).reject()
