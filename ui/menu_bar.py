# -*- coding: utf-8 -*-
"""
-------------------------------------------------
Project : NNBI_database
File    : menu_bar.py
Author  :
Date    :
Description : Menu Bar
-------------------------------------------------
"""

from PySide2.QtWidgets import (
    QMenuBar,
    QAction,
)


class MenuBar(QMenuBar):
    """
    主菜单
    """

    def __init__(self, parent=None):
        super(MenuBar, self).__init__(parent)

        self.main_window = parent

        # ==========================
        # Menu
        # ==========================
        self.file_menu = None
        self.view_menu = None
        self.mds_menu = None

        self.validation_menu = None

        self.window_menu = None
        self.help_menu = None

        # ==========================
        # Actions
        # ==========================
        self.action_connect = None
        self.action_open_tree = None
        self.action_refresh = None
        self.action_compare = None
        self.action_export = None
        self.action_export_png = None
        self.action_exit = None

        self.action_add_overlay = None
        self.action_clear_overlay = None

        self.overlay_menu = None

        self.action_tree = None
        self.action_parameter_panel = None
        self.action_additional_parameter_panel = None

        self.action_settings = None

        # ==========================
        # Validation
        # ==========================

        self.action_validation_test = None
        self.action_clear_validation = None
        self.action_export_validation = None

        # Performance Test
        self.action_performance_test = None
        self.action_clear_performance = None
        self.action_export_performance = None

        self.performance_menu = None

        self.panel_menu = None
        self.layout_menu = None

        self.action_add_panel = None
        self.action_remove_panel = None
        self.action_clear_panel = None

        self.action_layout_vertical = None
        self.action_layout_horizontal = None
        self.action_layout_auto = None
        self.action_layout_grid = None
        self.action_equal_size = None

        self.action_about = None

        self.create_actions()

        self.create_menus()

        self.create_connections()

    # =====================================================
    # 创建Action
    # =====================================================

    def create_actions(self):
        # -----------------------------
        # File
        # -----------------------------

        self.action_connect = QAction(
            "Connect",
            self
        )

        self.action_open_tree = QAction(
            "Open Tree",
            self
        )

        self.action_refresh = QAction(
            "Refresh",
            self
        )

        self.action_compare = QAction(
            "Compare",
            self
        )

        self.action_export = QAction(
            "Export CSV",
            self
        )

        self.action_export_png = QAction(
            "Export PNG",
            self
        )

        self.action_export_png.setStatusTip(
            "Export current waveform as PNG image"
        )

        self.action_add_overlay = QAction(
            "Add Selected Node to Overlay",
            self
        )

        self.action_add_overlay.setStatusTip(
            "Add selected Tree node to current waveform"
        )

        self.action_clear_overlay = QAction(
            "Clear Current Overlay",
            self
        )

        self.action_clear_overlay.setStatusTip(
            "Clear overlay curves in current waveform tab"
        )

        self.action_exit = QAction(
            "Exit",
            self
        )

        # -----------------------------
        # View
        # -----------------------------

        self.action_tree = QAction(
            "Tree Browser",
            self
        )

        self.action_tree.setCheckable(True)

        self.action_tree.setChecked(True)

        self.action_parameter_panel = QAction(
            "Parameter Panel",
            self
        )

        self.action_parameter_panel.setCheckable(
            True
        )

        self.action_parameter_panel.setChecked(
            True
        )

        self.action_parameter_panel.setStatusTip(
            "Show or hide the runtime parameter panel"
        )

        self.action_additional_parameter_panel = QAction(
            "Additional Parameters",
            self
        )

        self.action_additional_parameter_panel.setCheckable(
            True
        )

        self.action_additional_parameter_panel.setChecked(
            False
        )

        self.action_additional_parameter_panel.setStatusTip(
            "Show or hide the extensible additional parameter panel"
        )

        # -----------------------------
        # Window
        # -----------------------------

        self.action_settings = QAction(
            "Settings",
            self
        )

        # -----------------------------
        # Waveform Panel
        # -----------------------------

        self.action_add_panel = QAction(
            "Add Plot Panel",
            self
        )

        self.action_remove_panel = QAction(
            "Remove Current Panel",
            self
        )

        self.action_clear_panel = QAction(
            "Clear Current Panel",
            self
        )

        self.action_layout_vertical = QAction(
            "Vertical",
            self
        )

        self.action_layout_horizontal = QAction(
            "Horizontal",
            self
        )

        self.action_layout_auto = QAction(
            "Auto",
            self
        )

        self.action_layout_grid = QAction(
            "Grid...",
            self
        )

        self.action_equal_size = QAction(
            "Equal Panel Sizes",
            self
        )

        # -----------------------------
        # Validation
        # -----------------------------

        self.action_validation_test = QAction(
            "Validation Test Mode",
            self
        )

        self.action_validation_test.setCheckable(
            True
        )

        self.action_validation_test.setChecked(
            False
        )

        self.action_validation_test.setStatusTip(
            "Enable Full vs Stride waveform validation"
        )

        self.action_clear_validation = QAction(
            "Clear Validation Data",
            self
        )

        self.action_clear_validation.setStatusTip(
            "Clear Full references and validation results"
        )

        self.action_export_validation = QAction(
            "Export Validation Results",
            self
        )

        self.action_export_validation.setStatusTip(
            "Export Full vs Stride validation results to CSV"
        )

        # -----------------------------
        # Performance Test
        # -----------------------------

        self.action_performance_test = QAction(
            "Performance Test Mode",
            self
        )

        self.action_performance_test.setCheckable(
            True
        )

        self.action_performance_test.setChecked(
            False
        )

        self.action_performance_test.setStatusTip(
            "Enable performance data recording"
        )

        self.action_clear_performance = QAction(
            "Clear Performance Records",
            self
        )

        self.action_clear_performance.setStatusTip(
            "Clear all recorded performance test data"
        )

        self.action_export_performance = QAction(
            "Export Performance Results",
            self
        )

        self.action_export_performance.setStatusTip(
            "Export raw and summary performance CSV files"
        )

        # -----------------------------
        # Help
        # -----------------------------

        self.action_about = QAction(
            "About",
            self
        )

    # =====================================================
    # 创建Menu
    # =====================================================

    def create_menus(self):
        # -----------------------------
        # File
        # -----------------------------

        self.file_menu = self.addMenu("File")

        self.file_menu.addAction(
            self.action_connect
        )

        self.file_menu.addAction(
            self.action_open_tree
        )

        self.file_menu.addSeparator()

        self.file_menu.addAction(
            self.action_refresh
        )

        self.file_menu.addAction(
            self.action_compare
        )

        self.file_menu.addAction(
            self.action_export
        )

        self.file_menu.addAction(
            self.action_export_png
        )

        self.file_menu.addSeparator()

        self.file_menu.addAction(
            self.action_exit
        )

        # -----------------------------
        # Overlay
        # -----------------------------

        self.overlay_menu = self.addMenu(
            "Overlay"
        )

        self.overlay_menu.addAction(
            self.action_add_overlay
        )

        self.overlay_menu.addAction(
            self.action_clear_overlay
        )

        # -----------------------------
        # View
        # -----------------------------

        self.view_menu = self.addMenu("View")

        self.view_menu.addAction(
            self.action_tree
        )

        self.view_menu.addAction(
            self.action_parameter_panel
        )

        self.view_menu.addAction(
            self.action_additional_parameter_panel
        )

        self.view_menu.addSeparator()

        self.panel_menu = self.view_menu.addMenu(
            "Waveform Panels"
        )

        self.panel_menu.addAction(
            self.action_add_panel
        )

        self.panel_menu.addAction(
            self.action_remove_panel
        )

        self.panel_menu.addAction(
            self.action_clear_panel
        )

        self.layout_menu = self.view_menu.addMenu(
            "Panel Layout"
        )

        self.layout_menu.addAction(
            self.action_layout_vertical
        )

        self.layout_menu.addAction(
            self.action_layout_horizontal
        )

        self.layout_menu.addAction(
            self.action_layout_auto
        )

        self.layout_menu.addAction(
            self.action_layout_grid
        )

        self.layout_menu.addSeparator()

        self.layout_menu.addAction(
            self.action_equal_size
        )

        # -----------------------------
        # MDS
        # -----------------------------

        self.mds_menu = self.addMenu("MDS")

        self.mds_menu.addAction(
            self.action_connect
        )

        self.mds_menu.addAction(
            self.action_open_tree
        )

        self.mds_menu.addAction(
            self.action_refresh
        )

        # -----------------------------
        # Validation
        # -----------------------------

        self.validation_menu = self.addMenu(
            "Validation"
        )

        self.validation_menu.addAction(
            self.action_validation_test
        )

        self.validation_menu.addSeparator()

        self.validation_menu.addAction(
            self.action_clear_validation
        )

        self.validation_menu.addAction(
            self.action_export_validation
        )

        # -----------------------------
        # Performance
        # -----------------------------

        self.performance_menu = self.addMenu(
            "Performance"
        )

        self.performance_menu.addAction(
            self.action_performance_test
        )

        self.performance_menu.addSeparator()

        self.performance_menu.addAction(
            self.action_clear_performance
        )

        self.performance_menu.addAction(
            self.action_export_performance
        )

        # -----------------------------
        # Window
        # -----------------------------

        self.window_menu = self.addMenu("Window")

        self.window_menu.addAction(
            self.action_settings
        )

        # -----------------------------
        # Help
        # -----------------------------

        self.help_menu = self.addMenu("Help")

        self.help_menu.addAction(
            self.action_about
        )

    # =====================================================
    # 信号连接
    # =====================================================

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
            self.main_window.action_settings
        )

        self.action_about.triggered.connect(
            self.main_window.action_about
        )

        self.action_tree.toggled.connect(
            self.main_window.toggle_tree_browser
        )

        self.action_parameter_panel.toggled.connect(
            self.main_window.show_parameter_panel
        )

        self.action_additional_parameter_panel.toggled.connect(
            self.main_window.show_additional_parameter_panel
        )

        self.action_exit.triggered.connect(
            self.main_window.close
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

        self.action_clear_panel.triggered.connect(
            self.main_window.action_clear_waveform_panel
        )

        self.action_layout_vertical.triggered.connect(
            self.main_window.action_layout_vertical
        )

        self.action_layout_horizontal.triggered.connect(
            self.main_window.action_layout_horizontal
        )

        self.action_layout_auto.triggered.connect(
            self.main_window.action_layout_auto
        )

        self.action_layout_grid.triggered.connect(
            self.main_window.action_layout_grid
        )

        self.action_equal_size.triggered.connect(
            self.main_window.action_equal_panel_sizes
        )

        # -----------------------------
        # Performance Test
        # -----------------------------
        self.action_performance_test.toggled.connect(
            self.main_window.set_performance_test_mode
        )

        self.action_clear_performance.triggered.connect(
            self.main_window.clear_performance_records
        )

        self.action_export_performance.triggered.connect(
            self.main_window.export_performance_results
        )

        # =================================================
        # Validation
        # =================================================

        self.action_validation_test.toggled.connect(
            self.main_window.set_validation_test_mode
        )

        self.action_clear_validation.triggered.connect(
            self.main_window.clear_validation_records
        )

        self.action_export_validation.triggered.connect(
            self.main_window.export_validation_results
        )
