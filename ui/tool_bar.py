# -*- coding: utf-8 -*-
"""
-------------------------------------------------
Project : NNBI_database
File    : tree_browser.py
Author  :
File    : tool_bar.py
Author  :
Date    :
Description : Tool Bar
-------------------------------------------------
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QAction,
    QLabel,
    QPushButton,
    QSpinBox,
    QToolBar,
)


class ToolBar(QToolBar):
    """
    主工具栏
    """

    def __init__(self, parent=None):
        super(ToolBar, self).__init__(parent)

        self.main_window = parent

        # ==================================================
        # Toolbar Property
        # ==================================================
        self.setObjectName("MainToolBar")
        self.setWindowTitle("Main ToolBar")
        self.setMovable(False)
        self.setFloatable(False)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # ==================================================
        # Actions
        # ==================================================
        self.action_connect = None
        self.action_open_tree = None
        self.action_refresh = None
        self.action_compare = None
        self.action_add_overlay = None
        self.action_clear_overlay = None
        self.action_export = None
        self.action_export_png = None
        self.action_settings = None

        self.action_add_panel = None
        self.action_remove_panel = None
        self.action_layout_auto = None
        self.action_equal_size = None

        # ==================================================
        # Shot Switch
        # ==================================================

        self.label_shot = None
        self.spin_shot = None
        self.btn_switch_shot = None

        self.create_actions()
        self.create_toolbar()
        self.create_connections()

    # ==================================================
    # Create Actions
    # ==================================================

    def create_actions(self):
        self.action_connect = QAction("Connect", self)
        self.action_connect.setStatusTip("Connect to MDSplus Server")

        self.action_open_tree = QAction("Open Tree", self)
        self.action_open_tree.setStatusTip("Open Tree")

        self.action_refresh = QAction("Refresh", self)
        self.action_refresh.setStatusTip("Refresh Current Data")

        self.action_add_overlay = QAction(
            "Add Overlay",
            self
        )
        self.action_add_overlay.setStatusTip(
            "Add selected Tree node to current waveform"
        )
        self.action_clear_overlay = QAction(
            "Clear Overlay",
            self
        )
        self.action_clear_overlay.setStatusTip(
            "Clear current waveform overlays"
        )

        self.action_compare = QAction("Compare", self)
        self.action_compare.setStatusTip("Compare Multi Shots")

        self.action_export = QAction("Export CSV", self)
        self.action_export.setStatusTip("Export Data as CSV")

        self.action_export_png = QAction("Export PNG", self)
        self.action_export_png.setStatusTip("Export current waveform as PNG image")

        self.action_settings = QAction("Settings", self)
        self.action_settings.setStatusTip("Application Settings")

        self.action_add_panel = QAction("Add Plot", self)
        self.action_add_panel.setStatusTip(
            "Add a waveform panel to the current tab"
        )

        self.action_remove_panel = QAction("Remove Plot", self)
        self.action_remove_panel.setStatusTip(
            "Remove the active waveform panel"
        )

        self.action_layout_auto = QAction("Auto Layout", self)
        self.action_layout_auto.setStatusTip(
            "Automatically arrange waveform panels"
        )

        self.action_equal_size = QAction("Equal Size", self)
        self.action_equal_size.setStatusTip(
            "Restore equal waveform panel sizes"
        )

    # ==================================================
    # Create Toolbar
    # ==================================================

    def create_toolbar(self):
        self.addAction(self.action_connect)

        self.addSeparator()

        self.addAction(self.action_open_tree)

        self.addSeparator()

        self.create_shot_switch()

        self.addSeparator()

        self.addAction(self.action_refresh)

        self.addSeparator()

        self.addAction(
            self.action_add_overlay
        )

        self.addAction(
            self.action_clear_overlay
        )

        self.addSeparator()

        self.addAction(self.action_compare)

        self.addSeparator()

        self.addAction(self.action_add_panel)
        self.addAction(self.action_remove_panel)
        self.addAction(self.action_layout_auto)
        self.addAction(self.action_equal_size)

        self.addSeparator()

        self.addAction(
            self.action_export
        )

        self.addAction(
            self.action_export_png
        )

        self.addSeparator()

        self.addAction(self.action_settings)

    # ==================================================
    # Shot Switch
    # ==================================================

    def create_shot_switch(self):
        """
        创建主工具栏炮号切换控件。
        """

        self.label_shot = QLabel(
            "Shot:"
        )

        self.spin_shot = QSpinBox(
            self
        )

        self.spin_shot.setRange(
            -1,
            2147483647
        )

        self.spin_shot.setValue(
            int(
                getattr(
                    self.main_window.config,
                    "shot",
                    -1
                )
            )
        )

        self.spin_shot.setMinimumWidth(
            100
        )

        self.spin_shot.setToolTip(
            "Input shot number"
        )

        self.btn_switch_shot = QPushButton(
            "Switch",
            self
        )

        self.btn_switch_shot.setToolTip(
            "Switch current shot"
        )

        self.addWidget(
            self.label_shot
        )

        self.addWidget(
            self.spin_shot
        )

        self.addWidget(
            self.btn_switch_shot
        )

    def switch_shot(self):
        """
        将工具栏输入的炮号交给主窗口处理。
        """

        if self.spin_shot is None:
            return False

        return self.main_window.switch_shot_from_toolbar(
            self.spin_shot.value()
        )

    def set_shot(
            self,
            shot
    ):
        """
        同步工具栏显示的当前炮号。
        """

        if self.spin_shot is None:
            return

        try:
            shot = int(
                shot
            )
        except Exception:
            shot = -1

        self.spin_shot.blockSignals(
            True
        )

        self.spin_shot.setValue(
            shot
        )

        self.spin_shot.blockSignals(
            False
        )

    # ==================================================
    # Connections
    # ==================================================

    def create_connections(self):
        self.action_connect.triggered.connect(
            self.main_window.action_connect
        )

        self.action_open_tree.triggered.connect(
            self.main_window.action_open_tree
        )

        self.action_refresh.triggered.connect(
            self.main_window.refresh_data
        )

        self.action_compare.triggered.connect(
            self.main_window.compare_shots
        )

        self.action_export.triggered.connect(
            self.main_window.export_data
        )

        self.action_export_png.triggered.connect(
            self.main_window.action_export_png
        )

        self.action_settings.triggered.connect(
            self.main_window.open_settings_dialog
        )

        self.action_add_overlay.triggered.connect(
            self.main_window.action_add_overlay
        )

        self.action_clear_overlay.triggered.connect(
            self.main_window.action_clear_overlay
        )

        self.action_add_panel.triggered.connect(
            self.main_window.action_add_waveform_panel
        )

        self.action_remove_panel.triggered.connect(
            self.main_window.action_remove_waveform_panel
        )

        self.action_layout_auto.triggered.connect(
            self.main_window.action_layout_auto
        )

        self.action_equal_size.triggered.connect(
            self.main_window.action_equal_panel_sizes
        )

        self.btn_switch_shot.clicked.connect(
            self.switch_shot
        )

        self.spin_shot.lineEdit().returnPressed.connect(
            self.switch_shot
        )
