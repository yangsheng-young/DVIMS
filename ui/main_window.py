# -*- coding: utf-8 -*-

"""
==========================================================
Project : NNBI_database
File    : main_window.py
Author  :
Date    :
Description : Main Window
==========================================================
"""

from PySide2.QtCore import (
    Qt,
    QTimer,
)

from PySide2.QtWidgets import (
    QMainWindow,
    QDockWidget,
    QMessageBox,
    QInputDialog,
    QFileDialog,
)

from ui.menu_bar import MenuBar
from ui.tool_bar import ToolBar
from ui.status_bar import StatusBar
from ui.connect_dialog import ConnectDialog
from ui.settings_dialog import SettingsDialog
from ui.about_dialog import AboutDialog
from ui.compare_dialog import CompareDialog
from ui.tree_browser import TreeBrowser
from ui.waveform_area import WaveformArea
from ui.parameter_panel import ParameterPanel
from ui.additional_parameter_panel import AdditionalParameterPanel

from mds.mds_controller import MDSController

from performance.performance_export import PerformanceExporter
from validation.validation_manager import ValidationManager


class MainWindow(QMainWindow):
    """
    NNBI_database 主窗口

    功能：
    1. MDSplus服务器连接
    2. MDSplus Tree打开和关闭
    3. Tree结构显示
    4. Signal节点异步读取
    5. 多Tab波形显示
    6. 当前波形刷新
    7. 波形PNG和CSV导出
    8. 自动刷新
    9. 运行时配置更新
    """

    def __init__(
            self,
            config
    ):

        super(MainWindow, self).__init__()

        self.config = config

        # =================================================
        # UI Module
        # =================================================

        self.menu_bar = None
        self.tool_bar = None
        self.status_bar = None

        self.tree_browser = None
        self.waveform_area = None
        self.parameter_panel = None
        self.additional_parameter_panel = None

        self.tree_dock = None
        self.parameter_dock = None
        self.additional_parameter_dock = None

        # =================================================
        # Compare
        # =================================================

        self.compare_dialog = None
        self.last_compare_result = None

        # =================================================
        # Refresh
        # =================================================

        self.refresh_timer = None

        # =================================================
        # State
        # =================================================

        self.mds_controller = None

        # =================================================
        # Performance Test
        # =================================================

        self.performance_test_enabled = False

        self.performance_exporter = (
            PerformanceExporter()
        )

        # =================================================
        # Validation Test
        # =================================================

        self.validation_test_enabled = False

        self.validation_manager = (
            ValidationManager()
        )

        # =================================================
        # Initialize
        # =================================================

        self.init_window()
        self.init_mds()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.init_refresh_timer()
        self.apply_runtime_config()
        self.startup_connection()

    # =====================================================
    # MDSplus
    # =====================================================

    def init_mds(self):
        """
        初始化MDSplus控制器
        """

        self.mds_controller = MDSController(
            timeout=self.config.timeout,
            downsample_enabled=bool(
                getattr(
                    self.config,
                    "downsample_enabled",
                    True
                )
            ),
            max_points=int(
                getattr(
                    self.config,
                    "max_points",
                    10000
                )
            ),
            parent=self
        )

    # =====================================================
    # Window
    # =====================================================

    def init_window(self):
        """
        初始化主窗口
        """

        self.setWindowTitle(
            "{} {}".format(
                self.config.name,
                self.config.version
            )
        )

        self.resize(
            1400,
            900
        )

        self.setMinimumSize(
            1000,
            700
        )

        self.setDockNestingEnabled(
            True
        )

    # =====================================================
    # Widgets
    # =====================================================

    def create_widgets(self):
        """
        创建主窗口组件
        """

        # =================================================
        # MenuBar
        # =================================================

        self.menu_bar = MenuBar(
            self
        )

        self.setMenuBar(
            self.menu_bar
        )

        # =================================================
        # ToolBar
        # =================================================

        self.tool_bar = ToolBar(
            self
        )

        self.addToolBar(
            self.tool_bar
        )

        # =================================================
        # StatusBar
        # =================================================

        self.status_bar = StatusBar(
            self
        )

        self.setStatusBar(
            self.status_bar
        )

        # =================================================
        # TreeBrowser
        # =================================================

        self.tree_browser = TreeBrowser(
            self.config,
            self
        )

        # =================================================
        # WaveformArea
        # =================================================

        self.waveform_area = WaveformArea(
            self.config,
            self
        )

        # =================================================
        # ParameterPanel
        # =================================================

        self.parameter_panel = ParameterPanel(
            self.config,
            self
        )

        self.parameter_panel.set_query_options(
            downsample_enabled=(
                self.mds_controller.downsample_enabled()
            ),
            max_points=(
                self.mds_controller.max_points()
            )
        )

        self.parameter_panel.set_tree_shot(
            getattr(
                self.config,
                "tree",
                ""
            ),
            getattr(
                self.config,
                "shot",
                None
            )
        )

        # =================================================
        # AdditionalParameterPanel
        # =================================================

        self.additional_parameter_panel = AdditionalParameterPanel(
            self.config,
            self
        )

        self.additional_parameter_panel.set_tree_shot(
            getattr(
                self.config,
                "tree",
                ""
            ),
            getattr(
                self.config,
                "shot",
                None
            )
        )

    # =====================================================
    # Layout
    # =====================================================

    def create_layout(self):
        """
        创建主窗口布局
        """

        # =================================================
        # Central Widget
        # =================================================

        self.setCentralWidget(
            self.waveform_area
        )

        # =================================================
        # Tree Dock
        # =================================================

        self.tree_dock = QDockWidget(
            "Tree Browser",
            self
        )

        self.tree_dock.setObjectName(
            "TreeBrowserDock"
        )

        self.tree_dock.setWidget(
            self.tree_browser
        )

        self.tree_dock.setAllowedAreas(
            Qt.LeftDockWidgetArea |
            Qt.RightDockWidgetArea
        )

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            self.tree_dock
        )

        # =================================================
        # Parameter Dock
        # =================================================

        self.parameter_dock = QDockWidget(
            "Parameters",
            self
        )

        self.parameter_dock.setObjectName(
            "ParameterDock"
        )

        self.parameter_dock.setWidget(
            self.parameter_panel
        )

        self.parameter_dock.setAllowedAreas(
            Qt.LeftDockWidgetArea |
            Qt.RightDockWidgetArea
        )

        self.parameter_dock.setFeatures(
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetClosable
        )

        self.addDockWidget(
            Qt.RightDockWidgetArea,
            self.parameter_dock
        )

        # =================================================
        # Additional Parameter Dock
        # =================================================

        self.additional_parameter_dock = QDockWidget(
            "Additional Parameters",
            self
        )

        self.additional_parameter_dock.setObjectName(
            "AdditionalParameterDock"
        )

        self.additional_parameter_dock.setWidget(
            self.additional_parameter_panel
        )

        self.additional_parameter_dock.setAllowedAreas(
            Qt.LeftDockWidgetArea |
            Qt.RightDockWidgetArea
        )

        self.additional_parameter_dock.setFeatures(
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetClosable
        )

        self.addDockWidget(
            Qt.RightDockWidgetArea,
            self.additional_parameter_dock
        )

        # 默认与现有Parameters窗口放在同一Dock区域，
        # 用户可以通过标题栏拖动为独立窗口。
        self.tabifyDockWidget(
            self.parameter_dock,
            self.additional_parameter_dock
        )

    # =====================================================
    # Connections
    # =====================================================

    def create_connections(self):
        """
        创建信号连接
        """

        # =================================================
        # TreeBrowser
        # =================================================

        self.tree_browser.nodeOpenRequested.connect(
            self.open_node
        )

        self.tree_browser.overlayRequested.connect(
            self.add_overlay_node
        )

        # =================================================
        # MDS controller
        # =================================================

        self.mds_controller.statusChanged.connect(
            self.set_status
        )

        self.mds_controller.connectionChanged.connect(
            self.on_connection_changed
        )

        self.mds_controller.treeOpened.connect(
            self.on_tree_opened
        )

        self.mds_controller.treeClosed.connect(
            self.on_tree_closed
        )

        self.mds_controller.treeLoaded.connect(
            self.on_tree_loaded
        )

        self.mds_controller.signalLoaded.connect(
            self.on_signal_loaded
        )

        self.mds_controller.errorOccurred.connect(
            self.on_mds_error
        )

        self.mds_controller.busyChanged.connect(
            self.on_mds_busy_changed
        )

        self.mds_controller.shotParametersLoaded.connect(
            self.on_shot_parameters_loaded
        )

        self.mds_controller.shotParametersError.connect(
            self.on_shot_parameters_error
        )

        # =================================================
        # Tree Dock
        # =================================================

        self.tree_dock.visibilityChanged.connect(
            self.on_tree_visibility_changed
        )

        # =================================================
        # Parameter Panel and Dock
        # =================================================

        self.parameter_panel.queryOptionsApplied.connect(
            self.on_query_options_applied
        )

        self.parameter_panel.queryOptionsReloadRequested.connect(
            self.on_query_options_reload_requested
        )

        self.parameter_panel.currentShotRefreshRequested.connect(
            self.on_current_shot_refresh_requested
        )

        self.parameter_dock.visibilityChanged.connect(
            self.on_parameter_visibility_changed
        )

        self.additional_parameter_dock.visibilityChanged.connect(
            self.on_additional_parameter_visibility_changed
        )

        # =================================================
        # Waveform Area
        # =================================================

        self.waveform_area.currentTabChanged.connect(
            self.on_current_waveform_tab_changed
        )

        self.waveform_area.currentPanelChanged.connect(
            self.on_current_waveform_panel_changed
        )

    # =====================================================
    # Waveform Slots
    # =====================================================

    def on_current_waveform_tab_changed(
            self,
            tab
    ):
        """
        当前波形Tab发生变化。

        WaveformTab现在包含多个WaveformPanel，因此节点状态
        由当前活动Panel决定。
        """

        if tab is None:
            self.status_bar.set_node(
                ""
            )

            return

        panel = tab.current_panel()

        self.on_current_waveform_panel_changed(
            panel
        )

    def on_current_waveform_panel_changed(
            self,
            panel
    ):
        """
        当前活动WaveformPanel发生变化。

        状态栏始终显示当前活动面板对应的节点，而不是Tab中
        第一个或最后一个加载的节点。
        """

        if panel is None:

            self.status_bar.set_node(
                ""
            )

            if self.parameter_panel is not None:
                self.parameter_panel.clear_signal_info()

            return

        if bool(
                getattr(
                    panel,
                    "compare_mode",
                    False
                )
        ):

            compare_result = getattr(
                panel,
                "compare_result",
                None
            )

            request = getattr(
                compare_result,
                "request",
                None
            )

            node_path = getattr(
                request,
                "node",
                ""
            )

        else:

            signal_data = getattr(
                panel,
                "signal_data",
                None
            )

            node_path = getattr(
                signal_data,
                "node",
                ""
            ) if signal_data is not None else ""

        self.status_bar.set_node(
            node_path
        )

        if self.parameter_panel is not None:
            signal_data = getattr(
                panel,
                "signal_data",
                None
            )

            self.parameter_panel.set_signal_info(
                signal_data
            )

    # =====================================================
    # Tree Dock Slots
    # =====================================================

    def on_tree_visibility_changed(
            self,
            visible
    ):
        """
        Tree Browser显示状态发生变化
        """

        visible = bool(
            visible
        )

        self.config.show_tree = visible

        if (
                self.menu_bar is not None
                and
                self.menu_bar.action_tree is not None
        ):
            self.menu_bar.action_tree.blockSignals(
                True
            )

            self.menu_bar.action_tree.setChecked(
                visible
            )

            self.menu_bar.action_tree.blockSignals(
                False
            )

    # =====================================================
    # Parameter Dock and Query Slots
    # =====================================================

    def on_parameter_visibility_changed(
            self,
            visible
    ):
        """
        参数Dock显示状态发生变化。
        """

        visible = bool(
            visible
        )

        self.config.show_parameter_panel = visible

        if (
                self.menu_bar is not None
                and
                self.menu_bar.action_parameter_panel is not None
        ):
            self.menu_bar.action_parameter_panel.blockSignals(
                True
            )

            self.menu_bar.action_parameter_panel.setChecked(
                visible
            )

            self.menu_bar.action_parameter_panel.blockSignals(
                False
            )

        self.config.save()

    def on_additional_parameter_visibility_changed(
            self,
            visible
    ):
        """
        附加参数Dock显示状态发生变化。
        """

        visible = bool(
            visible
        )

        self.config.show_additional_parameter_panel = visible

        if (
                self.menu_bar is not None
                and
                self.menu_bar.action_additional_parameter_panel is not None
        ):
            self.menu_bar.action_additional_parameter_panel.blockSignals(
                True
            )

            self.menu_bar.action_additional_parameter_panel.setChecked(
                visible
            )

            self.menu_bar.action_additional_parameter_panel.blockSignals(
                False
            )

        self.config.save()

    def on_query_options_applied(
            self,
            enabled,
            max_points
    ):
        """
        将参数面板中的查询设置应用到后续数据库任务。
        """

        self.mds_controller.set_query_options(
            downsample_enabled=enabled,
            max_points=max_points
        )

        self.config.downsample_enabled = bool(
            enabled
        )

        self.config.max_points = max(
            100,
            int(
                max_points
            )
        )

        self.config.downsample_mode = "stride"

        self.config.save()

        self.set_status(
            "Query options applied    Downsampling: {}    "
            "Maximum points: {}".format(
                "On" if enabled else "Off",
                int(
                    max_points
                )
            )
        )

        return True

    def on_query_options_reload_requested(
            self,
            enabled,
            max_points
    ):
        """
        应用查询参数，并使用新参数重新读取当前活动Panel的节点。
        """

        self.on_query_options_applied(
            enabled,
            max_points
        )

        if self.mds_controller.is_busy():
            QMessageBox.information(
                self,
                "Reload Waveform",
                "MDSplus worker is busy."
            )

            return False

        panel = self.waveform_area.current_panel()

        if panel is None:
            QMessageBox.information(
                self,
                "Reload Waveform",
                "No active waveform panel."
            )

            return False

        if bool(
                getattr(
                    panel,
                    "compare_mode",
                    False
                )
        ):
            QMessageBox.information(
                self,
                "Reload Waveform",
                "Apply and Reload currently supports normal "
                "single-shot waveform panels."
            )

            return False

        signal_data = getattr(
            panel,
            "signal_data",
            None
        )

        node = getattr(
            signal_data,
            "node",
            ""
        ) if signal_data is not None else ""

        node = str(
            node
        ).strip()

        if node == "":
            QMessageBox.information(
                self,
                "Reload Waveform",
                "The current waveform panel has no node."
            )

            return False

        self.status_bar.set_node(
            node
        )

        return self.mds_controller.load_signal(
            node,
            mode="primary",
            downsample_enabled=enabled,
            max_points=max_points
        )

    def build_shot_parameter_definitions(self):
        """
        根据config.ini生成当前炮号参数节点映射。
        """

        return {
            "voltage": {
                "expression": getattr(
                    self.config,
                    "voltage_node",
                    ""
                ),
                "unit": getattr(
                    self.config,
                    "voltage_unit",
                    "kV"
                ),
                "group": "high_voltage",
                "value_type": "number"
            },
            "set_voltage": {
                "expression": getattr(
                    self.config,
                    "set_voltage_node",
                    ""
                ),
                "unit": getattr(
                    self.config,
                    "set_voltage_unit",
                    "kV"
                ),
                "group": "high_voltage",
                "value_type": "number"
            },
            "status": {
                "expression": getattr(
                    self.config,
                    "hv_status_node",
                    ""
                ),
                "unit": "",
                "group": "high_voltage",
                "value_type": "text"
            },
            "beam_current": {
                "expression": getattr(
                    self.config,
                    "beam_current_node",
                    ""
                ),
                "unit": getattr(
                    self.config,
                    "beam_current_unit",
                    "mA"
                ),
                "group": "current",
                "value_type": "number"
            },
            "arc_current": {
                "expression": getattr(
                    self.config,
                    "arc_current_node",
                    ""
                ),
                "unit": getattr(
                    self.config,
                    "arc_current_unit",
                    "A"
                ),
                "group": "current",
                "value_type": "number"
            },
            "filament_current": {
                "expression": getattr(
                    self.config,
                    "filament_current_node",
                    ""
                ),
                "unit": getattr(
                    self.config,
                    "filament_current_unit",
                    "A"
                ),
                "group": "current",
                "value_type": "number"
            }
        }

    def on_current_shot_refresh_requested(self):
        """
        异步读取当前Tree和Shot的高压、电流等参数。
        """

        self.parameter_panel.set_tree_shot(
            self.mds_controller.tree(),
            self.mds_controller.shot()
        )

        # TODO 预留参数
        # self.parameter_panel.clear_shot_parameters()

        return self.mds_controller.load_shot_parameters(
            self.build_shot_parameter_definitions()
        )

    def on_shot_parameters_loaded(
            self,
            result
    ):

        if not isinstance(
                result,
                dict
        ):
            return

        self.parameter_panel.set_tree_shot(
            result.get(
                "tree",
                ""
            ),
            result.get(
                "shot",
                None
            )
        )

        for name, item in result.get(
                "high_voltage",
                {}
        ).items():

            if item.get(
                    "configured",
                    False
            ):

                value = item.get(
                    "value"
                )

                if value is None:
                    value = "Read Error"

                self.parameter_panel.set_high_voltage_parameter(
                    name,
                    value,
                    item.get(
                        "unit",
                        ""
                    )
                )

        for name, item in result.get(
                "current",
                {}
        ).items():

            if item.get(
                    "configured",
                    False
            ):

                value = item.get(
                    "value"
                )

                if value is None:
                    value = "Read Error"

                self.parameter_panel.set_current_parameter(
                    name,
                    value,
                    item.get(
                        "unit",
                        ""
                    )
                )

        errors = result.get(
            "errors",
            {}
        )

        if errors:

            self.set_status(
                "Current shot parameters loaded with "
                "{} error(s)".format(
                    len(
                        errors
                    )
                )
            )

        else:

            self.set_status(
                "Current shot parameters loaded"
            )

    def on_shot_parameters_error(
            self,
            message
    ):

        # TODO 预留参数
        # self.parameter_panel.clear_shot_parameters()

        QMessageBox.warning(
            self,
            "Shot Parameter Error",
            str(
                message
            )
        )

    # =====================================================
    # MDS controller
    # =====================================================

    def on_connection_changed(
            self,
            connected
    ):
        """
        数据库连接状态变化
        """

        if connected:

            self.show_connected()

        else:

            self.show_disconnected()

            self.tree_browser.show_not_connected()

    def on_tree_opened(
            self,
            tree,
            shot
    ):
        """
        Tree打开完成
        """

        self.config.tree = tree
        self.config.shot = shot

        self.config.save()

        self.update_title(
            tree=tree,
            shot=shot
        )

        self.status_bar.set_tree(
            tree
        )

        self.status_bar.set_shot(
            shot
        )

        if self.tool_bar is not None:
            self.tool_bar.set_shot(
                shot
            )

        if self.parameter_panel is not None:
            self.parameter_panel.set_tree_shot(
                tree,
                shot
            )

    def on_tree_closed(self):
        """
        Tree关闭完成
        """

        self.tree_browser.show_tree_closed()

        self.waveform_area.close_all_tabs()

        self.status_bar.set_tree(
            ""
        )

        self.status_bar.set_shot(
            None
        )

        self.status_bar.set_node(
            ""
        )

        if self.parameter_panel is not None:
            self.parameter_panel.clear_tree_shot()
            self.parameter_panel.clear_signal_info()
            # TODO 预留参数
            # self.parameter_panel.clear_shot_parameters()

        if self.additional_parameter_panel is not None:
            self.additional_parameter_panel.clear_tree_shot()
            self.additional_parameter_panel.clear_all_parameters()

        self.update_title()

    def on_tree_loaded(
            self,
            tree_data
    ):
        """
        显示Tree结构
        """

        loaded = self.tree_browser.load_tree(
            tree_data
        )

        if not loaded:
            self.tree_browser.show_empty()

    def on_signal_loaded(
            self,
            signal,
            load_mode
    ):
        """
        显示Signal读取结果
        """

        if signal is None:
            self.set_status(
                "No signal data"
            )

            return

        if load_mode == "overlay":

            overlay_curve = (
                self.waveform_area.add_overlay_signal(
                    signal
                )
            )

            if overlay_curve is None:
                self.set_status(
                    "Failed to add overlay"
                )

                return

            self.set_status(
                "Overlay added    Total : {}".format(
                    self.waveform_area.current_overlay_count()
                )
            )

        else:

            # 普通节点读取结果由WaveformArea决定目标：
            # 1. 相同炮号、相同节点存在时更新原Panel；
            # 2. 相同炮号、不同节点进入同一个Tab的不同Panel；
            # 3. 不同炮号进入不同Tab。
            tab = (
                self.waveform_area.open_or_activate_waveform(
                    signal
                )
            )

            if tab is None:
                self.set_status(
                    "Failed to display waveform"
                )

                return

            panel = tab.current_panel()

            if panel is None:
                self.set_status(
                    "Failed to select waveform panel"
                )

                return

            # =================================================
            # Performance Test Record
            # =================================================

            if self.performance_test_enabled:

                record = (
                    panel.get_performance_record()
                )

                if record is not None:
                    self.performance_exporter.add_record(
                        record
                    )

            # =================================================
            # Validation Test
            # =================================================

            if self.validation_test_enabled:
                self.process_validation_signal(
                    signal
                )

        node_path = getattr(
            signal,
            "node",
            ""
        )

        self.status_bar.set_node(
            node_path
        )

        if self.parameter_panel is not None:
            self.parameter_panel.set_signal_info(
                signal
            )

    def process_validation_signal(
            self,
            signal
    ):
        """
        处理 Full / Stride 自动数值验证。

        Full：
            保存为当前 Shot + Node 的基准数据。

        Stride：
            如果实际发生服务器端降频，
            自动查找对应 Full Reference 并进行数值比较。
        """

        if signal is None:
            return

        try:

            result = (
                self.validation_manager.process_signal(
                    signal
                )
            )

        except Exception as exc:

            QMessageBox.warning(
                self,
                "Waveform Validation",
                (
                    "Validation failed.\n\n"
                    "{}"
                ).format(
                    exc
                )
            )

            return

        if not isinstance(
                result,
                dict
        ):
            return

        result_type = result.get(
            "type",
            ""
        )

        # =================================================
        # Full Reference Saved
        # =================================================

        if result_type == "full_saved":
            self.set_status(
                (
                    "Full reference saved    "
                    "Shot : {}    Node : {}"
                ).format(
                    getattr(
                        signal,
                        "shot",
                        0
                    ),
                    getattr(
                        signal,
                        "node",
                        ""
                    )
                )
            )

            return

        # =================================================
        # Stride Mode But No Actual Downsampling
        # =================================================

        if result_type == "not_downsampled":
            self.set_status(
                (
                    "Validation skipped    "
                    "No actual downsampling occurred"
                )
            )

            return

        # =================================================
        # Full Reference Not Found
        # =================================================

        if result_type == "missing_full":
            QMessageBox.information(
                self,
                "Waveform Validation",
                (
                    "No Full reference was found for "
                    "the current Shot and Node.\n\n"
                    "Please query the same node once "
                    "in Full mode first."
                )
            )

            return

        # =================================================
        # Validation Completed
        # =================================================

        if result_type == "validated":

            record = result.get(
                "record"
            )

            if record is None:
                return

            self.set_status(
                (
                    "Validation completed    "
                    "Compared : {}    "
                    "Max Error : {:.6g}    "
                    "RMSE : {:.6g}"
                ).format(
                    record.compared_points,
                    record.y_max_abs_error,
                    record.y_rmse
                )
            )

            return

    def set_validation_test_mode(
            self,
            enabled
    ):
        """
        开启或关闭 Full vs Stride 数值验证模式。
        """

        self.validation_test_enabled = bool(
            enabled
        )

        if self.validation_test_enabled:

            self.set_status(
                "Validation Test Mode enabled"
            )

        else:

            self.set_status(
                "Validation Test Mode disabled"
            )

    def clear_validation_records(self):
        """
        清空所有 Full Reference 和验证结果。
        """

        full_count = (
            self.validation_manager.full_count()
        )

        result_count = (
            self.validation_manager.result_count()
        )

        if (
                full_count <= 0
                and result_count <= 0
        ):
            self.set_status(
                "No validation data"
            )

            return

        reply = QMessageBox.question(
            self,
            "Clear Validation Data",
            (
                "Clear all validation data?\n\n"
                "Full references : {}\n"
                "Validation results : {}"
            ).format(
                full_count,
                result_count
            ),
            QMessageBox.Yes |
            QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.validation_manager.clear_all()

        self.set_status(
            "Validation data cleared"
        )

    def export_validation_results(self):
        """
        导出 Full vs Stride 数值验证结果。
        """

        count = (
            self.validation_manager.result_count()
        )

        if count <= 0:
            QMessageBox.information(
                self,
                "Waveform Validation",
                "No validation results to export."
            )

            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Validation Results",
            "validation_results.csv",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        if not file_path.lower().endswith(
                ".csv"
        ):
            file_path += ".csv"

        try:

            self.validation_manager.export_csv(
                file_path
            )

        except Exception as exc:

            QMessageBox.warning(
                self,
                "Waveform Validation",
                (
                    "Failed to export validation results.\n\n"
                    "{}"
                ).format(
                    exc
                )
            )

            return

        QMessageBox.information(
            self,
            "Waveform Validation",
            (
                "Validation results exported successfully.\n\n"
                "Records : {}\n\n"
                "{}"
            ).format(
                count,
                file_path
            )
        )

        self.set_status(
            "Validation results exported"
        )

    def on_mds_error(
            self,
            title,
            message
    ):
        """
        显示数据库操作错误
        """

        QMessageBox.warning(
            self,
            str(title),
            str(message)
        )

    def on_mds_busy_changed(
            self,
            busy
    ):
        """
        数据库后台任务状态变化
        """

        self.tree_browser.set_busy(
            busy
        )

        if self.parameter_panel is not None:
            self.parameter_panel.set_busy(
                busy
            )

    # =====================================================
    # Status Interface
    # =====================================================

    def set_status(
            self,
            text
    ):
        """
        设置主状态栏文字
        """

        if self.status_bar is not None:

            self.status_bar.set_status(
                str(text)
            )

        else:

            self.statusBar().showMessage(
                str(text)
            )

    def show_ready(self):
        """
        显示Ready状态
        """

        self.set_status(
            "Ready"
        )

    def show_busy(self):
        """
        显示Busy状态
        """

        self.set_status(
            "Busy..."
        )

    def show_connected(self):
        """
        显示Connected状态
        """

        self.set_status(
            "Connected"
        )

    def show_disconnected(self):
        """
        显示Disconnected状态
        """

        self.set_status(
            "Disconnected"
        )

    # =====================================================
    # Menu Interface
    # =====================================================

    def action_export_png(self):
        """
        导出当前波形PNG
        """

        return self.save_image()

    def action_add_overlay(self):
        """
        将当前Tree节点添加到波形叠加
        """

        return self.add_selected_overlay()

    def action_clear_overlay(self):
        """
        清空当前Tab叠加波形
        """

        return self.clear_current_overlay()

    def action_add_waveform_panel(self):
        """
        在当前Tab增加独立波形面板。
        """

        return self.waveform_area.add_panel_to_current_tab()

    def action_remove_waveform_panel(self):
        """
        删除当前活动波形面板。
        """

        return self.waveform_area.remove_current_panel()

    def action_clear_waveform_panel(self):
        """
        清空当前活动波形面板。
        """

        return self.waveform_area.clear_current_panel()

    def action_layout_vertical(self):

        return self.waveform_area.set_current_tab_vertical_layout()

    def action_layout_horizontal(self):

        return self.waveform_area.set_current_tab_horizontal_layout()

    def action_layout_auto(self):

        return self.waveform_area.set_current_tab_auto_layout()

    def action_layout_grid(self):
        """
        输入行列数并应用到当前Tab。
        """

        rows, accepted = QInputDialog.getInt(
            self,
            "Grid Layout",
            "Rows:",
            int(
                getattr(
                    self.config,
                    "panel_rows",
                    2
                )
            ),
            1,
            20,
            1
        )

        if not accepted:
            return False

        columns, accepted = QInputDialog.getInt(
            self,
            "Grid Layout",
            "Columns:",
            int(
                getattr(
                    self.config,
                    "panel_columns",
                    2
                )
            ),
            1,
            20,
            1
        )

        if not accepted:
            return False

        return self.waveform_area.set_current_tab_grid_layout(
            rows,
            columns
        )

    def action_equal_panel_sizes(self):

        return self.waveform_area.equalize_current_tab_panels()

    def action_connect(self):
        """
        打开数据库连接窗口
        """

        self.open_connect_dialog()

    def action_open_tree(self):
        """
        异步打开Tree，打开成功后由Controller自动加载
        """

        return self.open_tree()

    def action_refresh(self):
        """
        刷新当前波形
        """

        self.refresh_data()

    def action_compare(self):
        """
        多炮号比较
        """

        self.compare_shots()

    def action_export(self):
        """
        导出当前波形数据
        """

        self.export_data()

    def action_settings(self):
        """
        打开设置窗口
        """

        self.open_settings_dialog()

    def action_about(self):
        """
        打开About窗口
        """

        dialog = AboutDialog(
            self.config,
            self
        )

        dialog.exec_()

    def set_performance_test_mode(
            self,
            enabled
    ):
        """
        开启或关闭性能测试模式。

        只有开启后，
        普通波形查询结果才会被记录。
        """

        self.performance_test_enabled = bool(
            enabled
        )

        if self.performance_test_enabled:

            self.set_status(
                "Performance Test Mode enabled"
            )

        else:

            self.set_status(
                "Performance Test Mode disabled"
            )

    def clear_performance_records(self):
        """
        清空当前所有性能测试记录。
        """

        count = (
            self.performance_exporter.count()
        )

        if count <= 0:
            self.set_status(
                "No performance records"
            )

            return

        reply = QMessageBox.question(
            self,
            "Clear Performance Records",
            "Clear all {} performance records?".format(
                count
            ),
            QMessageBox.Yes |
            QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.performance_exporter.clear()

        self.set_status(
            "Performance records cleared"
        )

    def export_performance_results(self):
        """
        导出性能测试结果。

        输出：
            performance_raw.csv
            performance_summary.csv
        """

        count = (
            self.performance_exporter.count()
        )

        if count <= 0:
            QMessageBox.information(
                self,
                "Performance Test",
                "No performance records to export."
            )

            return

        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Performance Result Directory"
        )

        if not directory:
            return

        import os

        raw_path = os.path.join(
            directory,
            "performance_raw.csv"
        )

        summary_path = os.path.join(
            directory,
            "performance_summary.csv"
        )

        try:

            self.performance_exporter.export_raw_csv(
                raw_path
            )

            self.performance_exporter.export_summary_csv(
                summary_path
            )

        except Exception as exc:

            QMessageBox.warning(
                self,
                "Performance Export",
                "Failed to export performance results.\n\n{}".format(
                    exc
                )
            )

            return

        QMessageBox.information(
            self,
            "Performance Export",
            (
                "Performance results exported successfully.\n\n"
                "Records: {}\n\n"
                "Raw:\n{}\n\n"
                "Summary:\n{}"
            ).format(
                count,
                raw_path,
                summary_path
            )
        )

        self.set_status(
            "Performance results exported"
        )

    # =====================================================
    # ToolBar Interface
    # =====================================================

    def switch_shot_from_toolbar(
            self,
            shot
    ):
        """
        从主工具栏切换当前炮号。
        """

        if self.mds_controller is None:
            return False

        if not self.mds_controller.is_connected():
            QMessageBox.information(
                self,
                "Switch Shot",
                "Connect to the MDSplus server first."
            )

            return False

        if self.mds_controller.is_busy():
            QMessageBox.information(
                self,
                "Switch Shot",
                "MDSplus worker is busy."
            )

            return False

        try:

            shot = int(
                shot
            )

        except Exception:

            QMessageBox.warning(
                self,
                "Shot Error",
                "Invalid shot number."
            )

            return False

        if shot == self.config.shot:
            return True

        return self.load_shot(
            shot
        )

    def on_export_png_clicked(self):

        return self.action_export_png()

    def on_add_overlay_clicked(self):

        return self.action_add_overlay()

    def on_clear_overlay_clicked(self):

        return self.action_clear_overlay()

    def on_connect_clicked(self):

        self.action_connect()

    def on_open_tree_clicked(self):

        self.action_open_tree()

    def on_refresh_clicked(self):

        self.action_refresh()

    def on_compare_clicked(self):

        self.action_compare()

    def on_export_clicked(self):

        self.action_export()

    def on_settings_clicked(self):

        self.action_settings()

    # =====================================================
    # Tree Browser Interface
    # =====================================================

    def show_tree_browser(
            self,
            visible=True
    ):
        """
        显示或隐藏Tree Browser
        """

        if self.tree_dock is None:
            return

        visible = bool(
            visible
        )

        self.tree_dock.setVisible(
            visible
        )

        self.config.show_tree = visible

    def toggle_tree_browser(self):
        """
        切换Tree Browser显示状态
        """

        if self.tree_dock is None:
            return

        self.show_tree_browser(
            not self.tree_dock.isVisible()
        )

    # =====================================================
    # Parameter Panel Interface
    # =====================================================

    def show_parameter_panel(
            self,
            visible=True
    ):
        """
        显示或隐藏参数Dock。
        """

        if self.parameter_dock is None:
            return False

        self.parameter_dock.setVisible(
            bool(
                visible
            )
        )

        return True

    def toggle_parameter_panel(self):
        """
        切换参数Dock显示状态。
        """

        if self.parameter_dock is None:
            return False

        return self.show_parameter_panel(
            not self.parameter_dock.isVisible()
        )

    # =====================================================
    # Additional Parameter Panel Interface
    # =====================================================

    def show_additional_parameter_panel(
            self,
            visible=True
    ):

        if self.additional_parameter_dock is None:
            return False

        self.additional_parameter_dock.setVisible(
            bool(
                visible
            )
        )

        if visible:
            self.additional_parameter_dock.raise_()

        return True

    def toggle_additional_parameter_panel(self):

        if self.additional_parameter_dock is None:
            return False

        return self.show_additional_parameter_panel(
            not self.additional_parameter_dock.isVisible()
        )

    # =====================================================
    # Waveform Area Interface
    # =====================================================

    def clear_current_overlay(self):
        """
        清空当前Tab的全部叠加曲线
        """

        if self.waveform_area is None:
            return False

        overlay_count = (
            self.waveform_area.current_overlay_count()
        )

        if overlay_count <= 0:
            self.set_status(
                "No overlay curves"
            )

            return False

        self.waveform_area.clear_overlay()

        self.set_status(
            "Overlay cleared"
        )

        return True

    def add_waveform_tab(
            self,
            title="New Tab"
    ):
        """
        添加空波形Tab
        """

        return self.waveform_area.add_empty_tab(
            title
        )

    def close_current_tab(self):
        """
        关闭当前Tab
        """

        return (
            self.waveform_area.close_current_tab()
        )

    def close_all_tabs(self):
        """
        关闭全部Tab
        """

        self.waveform_area.close_all_tabs()

    def clear_current_waveform(self):
        """
        清空当前波形Tab
        """

        return (
            self.waveform_area.clear_current_tab()
        )

    # =====================================================
    # Window Title
    # =====================================================

    def update_title(
            self,
            tree="",
            shot=None
    ):
        """
        更新主窗口标题
        """

        title = "{} {}".format(
            self.config.name,
            self.config.version
        )

        if tree:
            title += "    [{}]".format(
                tree
            )

        if shot is not None:
            title += "    Shot: {}".format(
                shot
            )

        self.setWindowTitle(
            title
        )

    # =====================================================
    # Dialog
    # =====================================================

    def open_connect_dialog(self):
        """
        打开MDSplus连接设置窗口
        """

        dialog = ConnectDialog(
            self.config,
            self
        )

        if dialog.exec_():
            self.connect_server()

    def open_settings_dialog(self):
        """
        打开设置窗口
        """

        dialog = SettingsDialog(
            self.config,
            self
        )

        dialog.settingsApplied.connect(
            self.apply_runtime_config
        )

        if dialog.exec_():
            self.config.save()

            self.apply_runtime_config()

    def open_compare_dialog(self):
        """
        打开多炮号对比窗口。

        默认使用当前TreeBrowser选中的节点。窗口采用非模态方式，
        因此主窗口保留对话框对象，避免局部变量被回收。
        """

        if self.mds_controller is None:
            QMessageBox.warning(
                self,
                "Compare",
                "MDSplus controller is not available."
            )

            return False

        if not self.mds_controller.is_connected():
            QMessageBox.information(
                self,
                "Compare",
                "Connect to the MDSplus server first."
            )

            return False

        node = self.tree_browser.current_path()

        if node is None:
            node = ""
        else:
            node = str(
                node
            ).strip()

        if (
                self.compare_dialog is not None
                and
                self.compare_dialog.isVisible()
        ):

            if node:
                self.compare_dialog.set_node(
                    node
                )

            self.compare_dialog.raise_()
            self.compare_dialog.activateWindow()

            return True

        self.compare_dialog = CompareDialog(
            controller=self.mds_controller,
            config=self.config,
            default_node=node,
            parent=self
        )

        self.compare_dialog.setAttribute(
            Qt.WA_DeleteOnClose,
            True
        )

        self.compare_dialog.compareFinished.connect(
            self.on_compare_finished
        )

        self.compare_dialog.destroyed.connect(
            self.on_compare_dialog_destroyed
        )

        self.compare_dialog.show()
        self.compare_dialog.raise_()
        self.compare_dialog.activateWindow()

        return True

    def on_compare_dialog_destroyed(self):
        """
        CompareDialog销毁后清理主窗口引用。
        """

        self.compare_dialog = None

    def on_compare_finished(
            self,
            result
    ):
        """
        接收多炮号对比结果，并交给WaveformArea显示。
        """

        if result is None:
            self.set_status(
                "Comparison returned no result"
            )

            return False

        self.last_compare_result = result

        success_items = result.success_items()
        failed_items = result.failed_items()

        success_count = len(
            success_items
        )

        failed_count = len(
            failed_items
        )

        if success_count <= 0:
            self.set_status(
                "Comparison finished    Success: 0    "
                "Failed: {}".format(
                    failed_count
                )
            )

            QMessageBox.information(
                self,
                "Compare",
                "No shot was loaded successfully."
            )

            return False

        tab = self.waveform_area.show_compare_result(
            result
        )

        if tab is None:
            self.set_status(
                "Failed to display comparison result"
            )

            return False

        request = getattr(
            result,
            "request",
            None
        )

        node_path = getattr(
            request,
            "node",
            ""
        )

        self.status_bar.set_node(
            node_path
        )

        self.set_status(
            "Comparison finished    Success: {}    "
            "Failed: {}".format(
                success_count,
                failed_count
            )
        )

        return True

    # =====================================================
    # Runtime Config
    # =====================================================

    def apply_runtime_config(self):
        """
        应用运行时配置
        """

        self.mds_controller.set_timeout(
            self.config.timeout
        )

        self.mds_controller.set_query_options(
            downsample_enabled=bool(
                getattr(
                    self.config,
                    "downsample_enabled",
                    self.mds_controller.downsample_enabled()
                )
            ),
            max_points=int(
                getattr(
                    self.config,
                    "max_points",
                    self.mds_controller.max_points()
                )
            )
        )

        if self.parameter_panel is not None:
            options = self.mds_controller.query_options()

            self.parameter_panel.set_query_options(
                downsample_enabled=options[
                    "downsample_enabled"
                ],
                max_points=options[
                    "max_points"
                ]
            )

        self.apply_theme()
        self.apply_ui_config()
        self.apply_refresh_config()

        if self.waveform_area is not None:
            self.waveform_area.apply_config()

        if (
                self.tree_browser is not None
                and
                hasattr(
                    self.tree_browser,
                    "apply_config"
                )
        ):
            self.tree_browser.apply_config()

    def apply_ui_config(self):
        """
        应用主界面显示配置
        """

        show_toolbar = bool(
            getattr(
                self.config,
                "show_toolbar",
                True
            )
        )

        show_statusbar = bool(
            getattr(
                self.config,
                "show_statusbar",
                True
            )
        )

        show_tree = bool(
            getattr(
                self.config,
                "show_tree",
                True
            )
        )

        show_parameter_panel = bool(
            getattr(
                self.config,
                "show_parameter_panel",
                True
            )
        )

        show_additional_parameter_panel = bool(
            getattr(
                self.config,
                "show_additional_parameter_panel",
                False
            )
        )

        if self.tool_bar is not None:
            self.tool_bar.setVisible(
                show_toolbar
            )

            self.tool_bar.set_shot(
                self.config.shot
            )

        if self.status_bar is not None:
            self.status_bar.setVisible(
                show_statusbar
            )

        if self.tree_dock is not None:
            self.tree_dock.setVisible(
                show_tree
            )

        if self.parameter_dock is not None:
            self.parameter_dock.setVisible(
                show_parameter_panel
            )

        if self.additional_parameter_dock is not None:
            self.additional_parameter_dock.setVisible(
                show_additional_parameter_panel
            )

        if (
                self.menu_bar is not None
                and
                self.menu_bar.action_tree is not None
        ):
            self.menu_bar.action_tree.blockSignals(
                True
            )

            self.menu_bar.action_tree.setChecked(
                show_tree
            )

            self.menu_bar.action_tree.blockSignals(
                False
            )

        if (
                self.menu_bar is not None
                and
                self.menu_bar.action_parameter_panel is not None
        ):
            self.menu_bar.action_parameter_panel.blockSignals(
                True
            )

            self.menu_bar.action_parameter_panel.setChecked(
                show_parameter_panel
            )

            self.menu_bar.action_parameter_panel.blockSignals(
                False
            )

        if (
                self.menu_bar is not None
                and
                self.menu_bar.action_additional_parameter_panel is not None
        ):
            self.menu_bar.action_additional_parameter_panel.blockSignals(
                True
            )

            self.menu_bar.action_additional_parameter_panel.setChecked(
                show_additional_parameter_panel
            )

            self.menu_bar.action_additional_parameter_panel.blockSignals(
                False
            )

    def apply_theme(self):
        """
        应用主界面主题

        波形绘图区颜色由config中的：
        background = k
        foreground = w
        控制。
        """

        theme = getattr(
            self.config,
            "theme",
            "Dark"
        )

        if theme == "Dark":

            self.setStyleSheet(
                """
                QMainWindow,
                QWidget {
                    background-color: #2b2b2b;
                    color: #dddddd;
                }

                QMenuBar,
                QMenu,
                QToolBar,
                QStatusBar {
                    background-color: #333333;
                    color: #dddddd;
                }

                QTreeWidget,
                QLineEdit,
                QSpinBox,
                QDoubleSpinBox,
                QComboBox {
                    background-color: #202020;
                    color: #dddddd;
                    border: 1px solid #555555;
                }

                QPushButton {
                    background-color: #444444;
                    color: #ffffff;
                    border: 1px solid #666666;
                    padding: 4px 10px;
                }

                QPushButton:hover {
                    background-color: #555555;
                }

                QPushButton:pressed {
                    background-color: #333333;
                }

                QPushButton:checked {
                    background-color: #666666;
                }

                QTabWidget::pane {
                    border: 1px solid #444444;
                }

                QTabBar::tab {
                    background-color: #333333;
                    color: #dddddd;
                    padding: 6px 12px;
                }

                QTabBar::tab:selected {
                    background-color: #555555;
                    color: #ffffff;
                }
                """
            )

        else:

            self.setStyleSheet(
                ""
            )

    # =====================================================
    # Refresh Timer
    # =====================================================

    def init_refresh_timer(self):
        """
        初始化自动刷新定时器
        """

        self.refresh_timer = QTimer(
            self
        )

        self.refresh_timer.timeout.connect(
            self.refresh_data
        )

    def apply_refresh_config(self):
        """
        应用自动刷新配置
        """

        if self.refresh_timer is None:
            return

        interval = getattr(
            self.config,
            "interval",
            1000
        )

        try:

            interval = int(
                interval
            )

        except Exception:

            interval = 1000

        if interval < 100:
            interval = 100

        self.refresh_timer.setInterval(
            interval
        )

        auto_refresh = bool(
            getattr(
                self.config,
                "auto_refresh",
                False
            )
        )

        if auto_refresh:

            self.refresh_timer.start()

        else:

            self.refresh_timer.stop()

    # =====================================================
    # Startup
    # =====================================================

    def startup_connection(self):
        """
        根据配置异步执行启动连接
        """

        if not getattr(
                self.config,
                "auto_connect",
                False
        ):
            return

        self.connect_server()

    # =====================================================
    # MDSplus Connection
    # =====================================================

    def connect_server(self):
        """
        异步连接MDSplus服务器
        """

        self.config.save()

        return self.mds_controller.connect_server(
            host=self.config.host,
            port=self.config.port,
            auto_open=self.config.auto_open_tree,
            tree=self.config.tree,
            shot=self.config.shot
        )

    def disconnect_server(self):
        """
        断开MDSplus服务器
        """

        if self.refresh_timer is not None:
            self.refresh_timer.stop()

        disconnected = (
            self.mds_controller.disconnect_server()
        )

        if not disconnected:
            self.apply_refresh_config()

            return False

        self.waveform_area.close_all_tabs()

        self.update_title()

        self.status_bar.reset()

        if self.parameter_panel is not None:
            self.parameter_panel.clear_tree_shot()
            self.parameter_panel.clear_signal_info()
            # TODO 预留参数
            # self.parameter_panel.clear_shot_parameters()

        if self.additional_parameter_panel is not None:
            self.additional_parameter_panel.clear_tree_shot()
            self.additional_parameter_panel.clear_all_parameters()

        self.config.save()

        self.apply_refresh_config()

        return True

    # =====================================================
    # MDSplus Tree
    # =====================================================

    def open_tree(self):
        """
        异步打开MDSplus Tree
        """

        return self.mds_controller.open_tree(
            self.config.tree,
            self.config.shot,
            load_after_open=True
        )

    def close_tree(self):
        """
        关闭当前Tree
        """

        return self.mds_controller.close_tree()

    def load_tree(self):
        """
        异步加载Tree
        """

        self.tree_browser.show_loading()

        started = self.mds_controller.load_tree()

        if not started:
            self.tree_browser.show_empty()

        return started

    def reload_tree(self):
        """
        异步重新加载Tree
        """

        self.tree_browser.show_loading()

        return self.mds_controller.reload_tree()

    def load_shot(
            self,
            shot
    ):
        """
        异步切换炮号
        """

        try:

            shot = int(
                shot
            )

        except Exception:

            QMessageBox.warning(
                self,
                "Shot Error",
                "Invalid shot number."
            )

            return False

        return self.mds_controller.load_shot(
            self.config.tree,
            shot
        )

    # =====================================================
    # Signal Node
    # =====================================================

    def open_node(
            self,
            node=None
    ):
        """
        异步读取主波形
        """

        if node is None:
            node = self.tree_browser.current_path()

        if node is None:
            return False

        node = str(
            node
        ).strip()

        if node == "":
            return False

        self.status_bar.set_node(
            node
        )

        return self.mds_controller.load_signal(
            node,
            mode="primary"
        )

    def add_overlay_node(
            self,
            node=None
    ):
        """
        异步读取叠加波形
        """

        if not self.waveform_area.current_panel_has_data():
            QMessageBox.information(
                self,
                "Overlay",
                "Select a waveform panel with primary data "
                "before adding overlay signals."
            )

            return False

        if node is None:
            node = self.tree_browser.current_path()

        if node is None:
            return False

        node = str(
            node
        ).strip()

        if node == "":
            return False

        self.status_bar.set_node(
            node
        )

        return self.mds_controller.load_signal(
            node,
            mode="overlay"
        )

    def add_selected_overlay(self):
        """
        将TreeBrowser当前选中节点添加到当前Tab
        """

        path = self.tree_browser.current_path()

        if path is None:
            return False

        path = str(
            path
        ).strip()

        if path == "":
            QMessageBox.information(
                self,
                "Overlay",
                "Select a signal node in Tree Browser."
            )

            return False

        return self.add_overlay_node(
            path
        )

    def refresh_data(self):
        """
        刷新当前波形
        """

        path = self.waveform_area.current_node()

        if not path:
            path = self.tree_browser.current_path()

        if path is None:
            return False

        path = str(
            path
        ).strip()

        if path == "":
            return False

        return self.mds_controller.refresh_signal(
            path
        )

    # =====================================================
    # Export
    # =====================================================

    def export_data(self):
        """
        导出当前Tab波形CSV数据
        """

        if self.waveform_area is None:
            return False

        if not self.waveform_area.current_panel_has_data():
            QMessageBox.information(
                self,
                "Export",
                "The current waveform panel has no data."
            )

            return False

        return self.waveform_area.export_csv()

    def save_image(self):
        """
        保存当前Tab波形图片
        """

        if self.waveform_area is None:
            return False

        if not self.waveform_area.current_panel_has_data():
            QMessageBox.information(
                self,
                "Save Image",
                "The current waveform panel has no data."
            )

            return False

        return self.waveform_area.export_png()

    # =====================================================
    # Compare
    # =====================================================

    def compare_shots(self):
        """
        打开多炮号比较窗口。
        """

        return self.open_compare_dialog()

    # =====================================================
    # Event
    # =====================================================

    def closeEvent(
            self,
            event
    ):
        """
        程序关闭事件
        """

        reply = QMessageBox.question(
            self,
            "Exit",
            "Exit NNBI_database ?",
            QMessageBox.Yes |
            QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            event.ignore()

            return

        if self.refresh_timer is not None:
            self.refresh_timer.stop()

        closed = self.mds_controller.shutdown()

        if not closed:
            QMessageBox.warning(
                self,
                "Worker Busy",
                "A MDSplus background task is still running.\n"
                "The stop request has been sent.\n"
                "Please close the program again after the task stops."
            )

            self.apply_refresh_config()

            event.ignore()

            return

        if self.compare_dialog is not None:
            self.compare_dialog.close()
            self.compare_dialog = None

        self.config.save()

        event.accept()
