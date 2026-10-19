# -*- coding: utf-8 -*-

"""
==========================================================
Project : NNBI_database
File    : waveform_tab.py
Author  :
Date    :
Description : Multi-panel Waveform Tab
==========================================================
"""

from PySide2.QtCore import (
    Signal,
)

from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
)

from ui.waveform_layout import WaveformLayout


class WaveformTab(QWidget):
    """
    多波形面板Tab。

    一个WaveformTab可以包含多个独立WaveformPanel。

    功能：
    1. 动态增加和删除WaveformPanel；
    2. 管理当前活动面板；
    3. 支持纵向、横向、自动和自定义网格布局；
    4. 支持拖动QSplitter调整各面板大小；
    5. 保留原WaveformTab对外接口，兼容WaveformArea；
    6. 主波形、Overlay、Compare、Crosshair、Legend和导出
       均作用于当前活动面板；
    7. clear()清空当前Tab中的全部面板。
    """

    activePanelChanged = Signal(object)
    panelAdded = Signal(object)
    panelRemoved = Signal(object)

    layoutChanged = Signal(
        str,
        int,
        int
    )

    def __init__(
            self,
            config,
            parent=None
    ):

        super(WaveformTab, self).__init__(
            parent
        )

        self.config = config

        self.main_layout = None
        self.toolbar_layout = None

        self.lbl_layout = None
        self.combo_layout = None

        self.lbl_rows = None
        self.spin_rows = None

        self.lbl_columns = None
        self.spin_columns = None

        self.btn_apply_layout = None
        self.btn_add_panel = None
        self.btn_remove_panel = None
        self.btn_equal_size = None

        self.waveform_layout = None

        self.init_ui()
        self.create_connections()
        self.create_default_panel()

    # =====================================================
    # UI
    # =====================================================

    def init_ui(self):
        """
        初始化Tab容器和布局工具栏。
        """

        self.main_layout = QVBoxLayout(
            self
        )

        self.main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.main_layout.setSpacing(
            0
        )

        self.create_layout_toolbar()

        self.waveform_layout = WaveformLayout(
            self.config,
            self
        )

        self.main_layout.addWidget(
            self.waveform_layout,
            1
        )

    def create_layout_toolbar(self):
        """
        创建当前Tab内部的面板布局工具栏。
        """

        toolbar_widget = QWidget(
            self
        )

        self.toolbar_layout = QHBoxLayout(
            toolbar_widget
        )

        self.toolbar_layout.setContentsMargins(
            5,
            3,
            5,
            3
        )

        self.toolbar_layout.setSpacing(
            5
        )

        self.lbl_layout = QLabel(
            "Layout:",
            toolbar_widget
        )

        self.combo_layout = QComboBox(
            toolbar_widget
        )

        self.combo_layout.addItem(
            "Vertical",
            "vertical"
        )

        self.combo_layout.addItem(
            "Horizontal",
            "horizontal"
        )

        self.combo_layout.addItem(
            "Auto",
            "auto"
        )

        self.combo_layout.addItem(
            "Grid",
            "grid"
        )

        self.lbl_rows = QLabel(
            "Rows:",
            toolbar_widget
        )

        self.spin_rows = QSpinBox(
            toolbar_widget
        )

        self.spin_rows.setRange(
            1,
            20
        )

        self.spin_rows.setValue(
            2
        )

        self.spin_rows.setFixedWidth(
            55
        )

        self.lbl_columns = QLabel(
            "Columns:",
            toolbar_widget
        )

        self.spin_columns = QSpinBox(
            toolbar_widget
        )

        self.spin_columns.setRange(
            1,
            20
        )

        self.spin_columns.setValue(
            2
        )

        self.spin_columns.setFixedWidth(
            55
        )

        self.btn_apply_layout = QPushButton(
            "Apply",
            toolbar_widget
        )

        self.btn_add_panel = QPushButton(
            "Add Plot",
            toolbar_widget
        )

        self.btn_remove_panel = QPushButton(
            "Remove Plot",
            toolbar_widget
        )

        self.btn_equal_size = QPushButton(
            "Equal Size",
            toolbar_widget
        )

        self.toolbar_layout.addWidget(
            self.lbl_layout
        )

        self.toolbar_layout.addWidget(
            self.combo_layout
        )

        self.toolbar_layout.addWidget(
            self.lbl_rows
        )

        self.toolbar_layout.addWidget(
            self.spin_rows
        )

        self.toolbar_layout.addWidget(
            self.lbl_columns
        )

        self.toolbar_layout.addWidget(
            self.spin_columns
        )

        self.toolbar_layout.addWidget(
            self.btn_apply_layout
        )

        self.toolbar_layout.addSpacing(
            10
        )

        self.toolbar_layout.addWidget(
            self.btn_add_panel
        )

        self.toolbar_layout.addWidget(
            self.btn_remove_panel
        )

        self.toolbar_layout.addWidget(
            self.btn_equal_size
        )

        self.toolbar_layout.addStretch(
            1
        )

        self.main_layout.addWidget(
            toolbar_widget
        )

        self.update_grid_controls()

    # =====================================================
    # Connections
    # =====================================================

    def create_connections(self):
        """
        创建控件和WaveformLayout信号连接。
        """

        self.combo_layout.currentIndexChanged.connect(
            self.update_grid_controls
        )

        self.btn_apply_layout.clicked.connect(
            self.apply_selected_layout
        )

        self.btn_add_panel.clicked.connect(
            self.add_panel
        )

        self.btn_remove_panel.clicked.connect(
            self.remove_active_panel
        )

        self.btn_equal_size.clicked.connect(
            self.equalize_panel_sizes
        )

    def connect_layout_signals(self):
        """
        WaveformLayout创建完成后连接信号。
        """

        self.waveform_layout.activePanelChanged.connect(
            self.on_active_panel_changed
        )

        self.waveform_layout.panelAdded.connect(
            self.panelAdded
        )

        self.waveform_layout.panelRemoved.connect(
            self.panelRemoved
        )

        self.waveform_layout.layoutChanged.connect(
            self.on_layout_changed
        )

    # =====================================================
    # Default Panel
    # =====================================================

    def create_default_panel(self):
        """
        创建默认独立波形面板。
        """

        self.connect_layout_signals()

        panel_count = max(
            1,
            int(
                getattr(
                    self.config,
                    "default_panel_count",
                    1
                )
            )
        )

        first_panel = None

        for index in range(
                panel_count
        ):

            panel = self.waveform_layout.add_panel(
                make_active=(
                        index == 0
                )
            )

            if first_panel is None:
                first_panel = panel

        layout_mode = str(
            getattr(
                self.config,
                "panel_layout",
                "auto"
            )
        ).strip().lower()

        if layout_mode == "vertical":

            self.set_vertical_layout()

        elif layout_mode == "horizontal":

            self.set_horizontal_layout()

        elif layout_mode == "grid":

            self.set_grid_layout(
                getattr(
                    self.config,
                    "panel_rows",
                    2
                ),
                getattr(
                    self.config,
                    "panel_columns",
                    2
                )
            )

        else:

            self.set_auto_layout()

        self.update_remove_button()

        return first_panel

    # =====================================================
    # Panel Management
    # =====================================================

    def add_panel(
            self,
            panel=None,
            make_active=True
    ):
        """
        增加一个独立波形面板。
        """

        result = self.waveform_layout.add_panel(
            panel=panel,
            make_active=make_active
        )

        self.update_remove_button()

        return result

    def remove_active_panel(self):
        """
        删除当前活动面板。

        始终保留至少一个面板。
        """

        if self.panel_count() <= 1:

            panel = self.current_panel()

            if panel is not None:
                panel.clear()

            return False

        result = self.waveform_layout.remove_panel(
            self.current_panel()
        )

        self.update_remove_button()

        return result

    def remove_panel(
            self,
            panel
    ):
        """
        删除指定面板。
        """

        if self.panel_count() <= 1:

            if panel is not None:
                panel.clear()

            return False

        result = self.waveform_layout.remove_panel(
            panel
        )

        self.update_remove_button()

        return result

    def clear_all_panels(
            self,
            keep_one=True
    ):
        """
        删除或清空当前Tab内全部面板。
        """

        if keep_one:

            panels = self.panels()

            if not panels:
                self.add_panel()

                return True

            first_panel = panels[0]

            for panel in panels[1:]:
                self.waveform_layout.remove_panel(
                    panel
                )

            first_panel.clear()

            self.waveform_layout.set_active_panel(
                first_panel
            )

        else:

            self.waveform_layout.clear_panels()

        self.update_remove_button()

        return True

    def panel_count(self):

        return self.waveform_layout.panel_count()

    def panels(self):

        return list(
            self.waveform_layout.panels
        )

    def panel_at(
            self,
            index
    ):

        return self.waveform_layout.panel_at(
            index
        )

    def current_panel(self):

        return self.waveform_layout.current_panel()

    def set_active_panel(
            self,
            panel
    ):

        return self.waveform_layout.set_active_panel(
            panel
        )

    def first_empty_panel(self):

        return self.waveform_layout.first_empty_panel()

    def get_or_create_empty_panel(
            self,
            make_active=True
    ):
        """
        返回一个空面板；不存在时自动创建。
        """

        panel = self.first_empty_panel()

        if panel is None:

            panel = self.add_panel(
                make_active=make_active
            )

        elif make_active:

            self.set_active_panel(
                panel
            )

        return panel

    def update_remove_button(self):

        self.btn_remove_panel.setEnabled(
            self.panel_count() > 1
        )

    # =====================================================
    # Active Panel
    # =====================================================

    def on_active_panel_changed(
            self,
            panel
    ):

        self.activePanelChanged.emit(
            panel
        )

    # =====================================================
    # Dynamic Layout
    # =====================================================

    def selected_layout_mode(self):

        mode = self.combo_layout.currentData()

        if mode is None:
            mode = "vertical"

        return str(
            mode
        )

    def update_grid_controls(self):
        """
        只有Grid模式允许编辑行列数量。
        """

        is_grid = (
                self.selected_layout_mode()
                ==
                "grid"
        )

        self.lbl_rows.setEnabled(
            is_grid
        )

        self.spin_rows.setEnabled(
            is_grid
        )

        self.lbl_columns.setEnabled(
            is_grid
        )

        self.spin_columns.setEnabled(
            is_grid
        )

    def apply_selected_layout(self):
        """
        应用工具栏中选择的布局。
        """

        mode = self.selected_layout_mode()

        if mode == "vertical":
            return self.set_vertical_layout()

        if mode == "horizontal":
            return self.set_horizontal_layout()

        if mode == "auto":
            return self.set_auto_layout()

        return self.set_grid_layout(
            self.spin_rows.value(),
            self.spin_columns.value()
        )

    def set_vertical_layout(self):

        self.set_layout_combo(
            "vertical"
        )

        return self.waveform_layout.set_vertical_layout()

    def set_horizontal_layout(self):

        self.set_layout_combo(
            "horizontal"
        )

        return self.waveform_layout.set_horizontal_layout()

    def set_auto_layout(self):

        self.set_layout_combo(
            "auto"
        )

        return self.waveform_layout.set_auto_layout()

    def set_grid_layout(
            self,
            rows,
            columns
    ):

        rows = max(
            1,
            int(rows)
        )

        columns = max(
            1,
            int(columns)
        )

        self.spin_rows.setValue(
            rows
        )

        self.spin_columns.setValue(
            columns
        )

        self.set_layout_combo(
            "grid"
        )

        return self.waveform_layout.set_grid_layout(
            rows,
            columns
        )

    def set_layout_combo(
            self,
            mode
    ):

        for index in range(
                self.combo_layout.count()
        ):

            if (
                    self.combo_layout.itemData(
                        index
                    )
                    ==
                    mode
            ):
                self.combo_layout.blockSignals(
                    True
                )

                self.combo_layout.setCurrentIndex(
                    index
                )

                self.combo_layout.blockSignals(
                    False
                )

                break

        self.update_grid_controls()

    def equalize_panel_sizes(self):

        return self.waveform_layout.equalize_sizes()

    def on_layout_changed(
            self,
            mode,
            rows,
            columns
    ):

        self.layoutChanged.emit(
            str(mode),
            int(rows),
            int(columns)
        )

    # =====================================================
    # Compatibility Properties
    # =====================================================

    @property
    def signal_data(self):
        """
        返回当前活动面板的SignalData。
        """

        panel = self.current_panel()

        if panel is None:
            return None

        return panel.signal_data

    @signal_data.setter
    def signal_data(
            self,
            value
    ):
        """
        兼容旧代码直接设置signal_data。
        """

        panel = self.current_panel()

        if panel is None:
            panel = self.add_panel()

        panel.signal_data = value

    @property
    def compare_mode(self):

        panel = self.current_panel()

        if panel is None:
            return False

        return bool(
            panel.compare_mode
        )

    @property
    def compare_result(self):

        panel = self.current_panel()

        if panel is None:
            return None

        return panel.compare_result

    @property
    def plot_widget(self):

        panel = self.current_panel()

        if panel is None:
            return None

        return panel.plot_widget

    @property
    def overlay(self):

        panel = self.current_panel()

        if panel is None:
            return None

        return panel.overlay

    # =====================================================
    # Original WaveformTab Compatibility Interface
    # =====================================================

    def set_title(
            self,
            title
    ):

        panel = self.current_panel()

        if panel is None:
            return

        panel.set_title(
            title
        )

    def title(self):

        panel = self.current_panel()

        if panel is None:
            return ""

        return panel.title()

    def set_status(
            self,
            text
    ):

        panel = self.current_panel()

        if panel is None:
            return

        panel.set_status(
            text
        )

    def load_signal(
            self,
            signal_data,
            panel=None
    ):
        """
        将SignalData加载到指定面板。

        panel为None时加载到当前活动面板。
        """

        if signal_data is None:
            return False

        if panel is None:
            panel = self.current_panel()

        if panel is None:
            panel = self.add_panel()

        self.set_active_panel(
            panel
        )

        return panel.load_signal(
            signal_data
        )

    def load_signal_to_new_panel(
            self,
            signal_data
    ):
        """
        新建面板并加载波形。
        """

        panel = self.add_panel(
            make_active=True
        )

        success = panel.load_signal(
            signal_data
        )

        if not success:
            self.remove_panel(
                panel
            )

            return None

        return panel

    def load_signal_to_empty_panel(
            self,
            signal_data
    ):
        """
        优先加载到空面板，无空面板时自动增加面板。
        """

        panel = self.get_or_create_empty_panel(
            make_active=True
        )

        if not panel.load_signal(
                signal_data
        ):
            return None

        return panel

    def refresh(self):
        """
        重新绘制当前活动面板。
        """

        panel = self.current_panel()

        if panel is None:
            return False

        return panel.refresh()

    def refresh_all(self):
        """
        刷新当前Tab中的全部面板。
        """

        result = False

        for panel in self.panels():

            if panel.has_data():
                panel.refresh()
                result = True

        return result

    def display_compare(
            self,
            result,
            panel=None
    ):
        """
        在指定或当前面板中显示多炮号对比。
        """

        if panel is None:
            panel = self.current_panel()

        if panel is None:
            panel = self.add_panel()

        self.set_active_panel(
            panel
        )

        return panel.display_compare(
            result
        )

    def clear_compare(self):

        panel = self.current_panel()

        if panel is None:
            return

        return panel.clear_compare()

    def add_overlay_signal(
            self,
            signal_data,
            key=None,
            color=None,
            width=None,
            replace=False
    ):
        """
        向当前活动面板增加Overlay。
        """

        panel = self.current_panel()

        if panel is None:
            return None

        return panel.add_overlay_signal(
            signal_data=signal_data,
            key=key,
            color=color,
            width=width,
            replace=replace
        )

    def remove_overlay_curve(
            self,
            key
    ):

        panel = self.current_panel()

        if panel is None:
            return False

        return panel.remove_overlay_curve(
            key
        )

    def clear_overlay(self):

        panel = self.current_panel()

        if panel is None:
            return

        return panel.clear_overlay()

    def overlay_count(self):

        panel = self.current_panel()

        if panel is None:
            return 0

        return panel.overlay_count()

    def auto_scale(self):

        panel = self.current_panel()

        if panel is None:
            return

        return panel.auto_scale()

    def auto_scale_all(self):

        for panel in self.panels():

            if panel.has_data():
                panel.auto_scale()

    def clear(self):
        """
        清空当前Tab中的全部波形面板。

        保留面板数量和当前布局，只清除数据。
        """

        for panel in self.panels():
            panel.clear()

        return True

    def clear_active_panel(self):

        panel = self.current_panel()

        if panel is None:
            return False

        panel.clear()

        return True

    def has_data(self):
        """
        判断当前Tab中是否任一面板存在数据。
        """

        for panel in self.panels():

            if panel.has_data():
                return True

        return False

    def current_panel_has_data(self):

        panel = self.current_panel()

        if panel is None:
            return False

        return panel.has_data()

    def export_png(self):
        """
        导出当前活动面板PNG。
        """

        panel = self.current_panel()

        if panel is None:
            return False

        return panel.export_png()

    def export_csv(self):
        """
        导出当前活动面板CSV。
        """

        panel = self.current_panel()

        if panel is None:
            return False

        return panel.export_csv()

    def set_crosshair_enabled(
            self,
            enabled
    ):

        panel = self.current_panel()

        if panel is None:
            return

        return panel.set_crosshair_enabled(
            enabled
        )

    def set_legend_visible(
            self,
            visible
    ):

        panel = self.current_panel()

        if panel is None:
            return

        return panel.set_legend_visible(
            visible
        )

    def apply_config(self):
        """
        将配置应用到全部面板。
        """

        return self.waveform_layout.apply_config()

    # =====================================================
    # Search
    # =====================================================

    def find_panel_by_node(
            self,
            node_path
    ):
        """
        根据节点路径查找当前Tab中的面板。
        """

        if node_path is None:
            return None

        target = str(
            node_path
        ).strip().upper()

        if target == "":
            return None

        for panel in self.panels():

            signal_data = getattr(
                panel,
                "signal_data",
                None
            )

            if signal_data is None:
                continue

            panel_node = getattr(
                signal_data,
                "node",
                ""
            )

            panel_node = str(
                panel_node
            ).strip().upper()

            if panel_node == target:
                return panel

        return None

    def activate_panel_by_node(
            self,
            node_path
    ):

        panel = self.find_panel_by_node(
            node_path
        )

        if panel is None:
            return False

        return self.set_active_panel(
            panel
        )

    # =====================================================
    # Close
    # =====================================================

    def closeEvent(
            self,
            event
    ):

        for panel in self.panels():

            try:
                panel.close()
            except Exception:
                pass

        super(WaveformTab, self).closeEvent(
            event
        )
