# -*- coding: utf-8 -*-

"""
==========================================================
Project : NNBI_database
File    : waveform_panel.py
Author  :
Date    :
Description : Independent Waveform Panel
==========================================================
"""

import os
import time

from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
)

from plot.plot_widget import WaveformPlotWidget
from plot.crosshair import Crosshair
from plot.legend import WaveformLegend
from plot.overlay import WaveformOverlay
from plot.export import WaveformExport

from performance.performance_record import PerformanceRecord


class WaveformPanel(QWidget):
    """
    单个独立波形面板

    功能：
    1. 显示单条 SignalData 波形
    2. 自动缩放
    3. 清空波形
    4. 十字光标
    5. 图例显示
    6. 同一页面多曲线叠加
    7. PNG 导出
    8. CSV 导出
    9. 动态应用配置
    """

    def __init__(
            self,
            config,
            parent=None
    ):

        super(WaveformPanel, self).__init__(
            parent
        )

        self.config = config

        # =================================================
        # Current Signal
        # =================================================

        self.signal_data = None

        self.current_curve_key = ""

        # =================================================
        # Performance Test
        # =================================================

        self.plot_time = 0.0

        self.performance_record = None

        # =================================================
        # Multi-shot Compare
        # =================================================

        self.compare_mode = False
        self.compare_result = None

        # =================================================
        # Layout
        # =================================================

        self.main_layout = None
        self.toolbar_layout = None

        # =================================================
        # Toolbar Widgets
        # =================================================

        self.lbl_title = None

        self.btn_auto = None
        self.btn_crosshair = None
        self.btn_legend = None
        self.btn_clear = None
        self.btn_export_png = None
        self.btn_export_csv = None

        # =================================================
        # Plot Modules
        # =================================================

        self.plot_widget = None
        self.crosshair = None
        self.legend = None
        self.overlay = None
        self.exporter = None

        # =================================================
        # Status
        # =================================================

        self.status_label = None
        self.coordinate_label = None

        self.init_ui()
        self.init_plot_modules()
        self.create_connections()
        self.apply_config()

    # =====================================================
    # UI
    # =====================================================

    def init_ui(self):
        """
        初始化页面界面
        """

        self.main_layout = QVBoxLayout(
            self
        )

        self.main_layout.setContentsMargins(
            5,
            5,
            5,
            5
        )

        self.main_layout.setSpacing(
            5
        )

        self.create_toolbar()
        self.create_plot_area()
        self.create_status_bar()

    # =====================================================
    # Toolbar
    # =====================================================

    def create_toolbar(self):
        """
        创建波形工具栏
        """

        self.toolbar_layout = QHBoxLayout()

        self.toolbar_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.toolbar_layout.setSpacing(
            5
        )

        self.lbl_title = QLabel(
            "Waveform"
        )

        self.btn_auto = QPushButton(
            "Auto Scale"
        )

        self.btn_crosshair = QPushButton(
            "Crosshair"
        )

        self.btn_crosshair.setCheckable(
            True
        )

        self.btn_crosshair.setChecked(
            True
        )

        self.btn_legend = QPushButton(
            "Legend"
        )

        self.btn_legend.setCheckable(
            True
        )

        self.btn_legend.setChecked(
            True
        )

        self.btn_clear = QPushButton(
            "Clear"
        )

        self.btn_export_png = QPushButton(
            "Export PNG"
        )

        self.btn_export_csv = QPushButton(
            "Export CSV"
        )

        self.toolbar_layout.addWidget(
            self.lbl_title
        )

        self.toolbar_layout.addStretch()

        self.toolbar_layout.addWidget(
            self.btn_auto
        )

        self.toolbar_layout.addWidget(
            self.btn_crosshair
        )

        self.toolbar_layout.addWidget(
            self.btn_legend
        )

        self.toolbar_layout.addWidget(
            self.btn_clear
        )

        self.toolbar_layout.addWidget(
            self.btn_export_png
        )

        self.toolbar_layout.addWidget(
            self.btn_export_csv
        )

        self.main_layout.addLayout(
            self.toolbar_layout
        )

    # =====================================================
    # Plot Area
    # =====================================================

    def create_plot_area(self):
        """
        创建波形绘图控件
        """

        self.plot_widget = WaveformPlotWidget(
            self.config,
            self
        )

        self.main_layout.addWidget(
            self.plot_widget
        )

    # =====================================================
    # Status Bar
    # =====================================================

    def create_status_bar(self):
        """
        创建页面状态栏
        """

        status_layout = QHBoxLayout()

        status_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.status_label = QLabel(
            "Ready"
        )

        self.coordinate_label = QLabel(
            ""
        )

        status_layout.addWidget(
            self.status_label
        )

        status_layout.addStretch()

        status_layout.addWidget(
            self.coordinate_label
        )

        self.main_layout.addLayout(
            status_layout
        )

    # =====================================================
    # Plot Modules
    # =====================================================

    def init_plot_modules(self):
        """
        初始化绘图功能模块
        """

        self.legend = WaveformLegend(
            self.plot_widget,
            self
        )

        self.overlay = WaveformOverlay(
            self.plot_widget,
            self.legend,
            self
        )

        self.crosshair = Crosshair(
            self.plot_widget,
            self
        )

        self.exporter = WaveformExport(
            plot_widget=self.plot_widget,
            overlay_manager=self.overlay,
            parent=self
        )

        if self.config is not None:
            self.exporter.apply_config(
                self.config
            )

        self.apply_dark_plot_style()

    # =====================================================
    # Connections
    # =====================================================

    def create_connections(self):
        """
        创建信号连接
        """

        self.btn_auto.clicked.connect(
            self.auto_scale
        )

        self.btn_crosshair.toggled.connect(
            self.on_crosshair_toggled
        )

        self.btn_legend.toggled.connect(
            self.on_legend_toggled
        )

        self.btn_clear.clicked.connect(
            self.clear
        )

        self.btn_export_png.clicked.connect(
            self.export_png
        )

        self.btn_export_csv.clicked.connect(
            self.export_csv
        )

        self.plot_widget.dataChanged.connect(
            self.on_plot_data_changed
        )

        self.plot_widget.plotCleared.connect(
            self.on_plot_cleared
        )

        self.crosshair.pointChanged.connect(
            self.on_crosshair_point_changed
        )

        self.crosshair.pointCleared.connect(
            self.on_crosshair_point_cleared
        )

        self.exporter.exportStarted.connect(
            self.on_export_started
        )

        self.exporter.exportFinished.connect(
            self.on_export_finished
        )

        self.exporter.exportError.connect(
            self.on_export_error
        )

        self.overlay.curveAdded.connect(
            self.on_overlay_changed
        )

        self.overlay.curveRemoved.connect(
            self.on_overlay_changed
        )

        self.overlay.curveUpdated.connect(
            self.on_overlay_changed
        )

        self.overlay.overlayCleared.connect(
            self.on_overlay_cleared
        )

    # =====================================================
    # Basic Interface
    # =====================================================

    def set_title(self, title):
        """
        设置页面标题
        """

        if title is None:
            title = "Waveform"

        title = str(
            title
        ).strip()

        if title == "":
            title = "Waveform"

        self.lbl_title.setText(
            title
        )

    def title(self):
        """
        返回页面标题
        """

        if self.lbl_title is None:
            return ""

        return self.lbl_title.text()

    def set_status(self, text):
        """
        设置页面状态
        """

        if text is None:
            text = ""

        self.status_label.setText(
            str(text)
        )

    def set_coordinate_status(self, text):
        """
        设置坐标状态
        """

        if text is None:
            text = ""

        self.coordinate_label.setText(
            str(text)
        )

    # =====================================================
    # Signal Data
    # =====================================================

    def load_signal(self, signal_data):
        """
        加载并显示一条 SignalData。

        同时记录本次波形绘制耗时，
        并生成 PerformanceRecord。
        """

        if signal_data is None:
            self.clear()

            return False

        # =================================================
        # Plot Timer Start
        # =================================================

        plot_start_time = time.perf_counter()

        self.compare_mode = False
        self.compare_result = None

        self.signal_data = signal_data

        signal_name = self.get_signal_name(
            signal_data
        )

        node_path = getattr(
            signal_data,
            "node",
            ""
        )

        self.set_title(
            signal_name
        )

        self.update_axis_labels(
            signal_data
        )

        success = self.plot_widget.set_data(
            getattr(
                signal_data,
                "x",
                None
            ),
            getattr(
                signal_data,
                "y",
                None
            ),
            signal_name=signal_name,
            node_path=node_path
        )

        if not success:
            self.signal_data = None

            self.plot_time = 0.0
            self.performance_record = None

            self.set_status(
                "No signal data"
            )

            return False

        self.update_primary_legend(
            signal_data
        )

        self.crosshair.set_data(
            self.plot_widget.get_x_data(),
            self.plot_widget.get_y_data()
        )

        self.set_status(
            "{} Points".format(
                self.plot_widget.point_count()
            )
        )

        # =================================================
        # Plot Timer End
        # =================================================

        plot_end_time = time.perf_counter()

        self.plot_time = (
                plot_end_time
                - plot_start_time
        )

        # =================================================
        # Build Performance Record
        # =================================================

        self.performance_record = (
            self.build_performance_record(
                signal_data
            )
        )

        return True

    def build_performance_record(
            self,
            signal_data
    ):
        """
        根据 SignalData 和本次 Plot Time
        创建一条完整的 PerformanceRecord。

        这里只创建记录，不负责保存CSV。
        """

        if signal_data is None:
            return None

        try:
            record = PerformanceRecord(
                shot=getattr(
                    signal_data,
                    "shot",
                    0
                ),

                node=getattr(
                    signal_data,
                    "node",
                    ""
                ),

                mode=getattr(
                    signal_data,
                    "query_mode",
                    ""
                ),

                original_points=getattr(
                    signal_data,
                    "original_size",
                    0
                ),

                max_points=getattr(
                    signal_data,
                    "max_points",
                    0
                ),

                loaded_points=getattr(
                    signal_data,
                    "loaded_size",
                    0
                ),

                stride=getattr(
                    signal_data,
                    "sample_step",
                    1
                ),

                query_time=getattr(
                    signal_data,
                    "query_time",
                    0.0
                ),

                plot_time=self.plot_time
            )

            return record

        except Exception:
            return None

    def get_performance_record(self):
        """
        返回当前Panel最近一次波形加载
        产生的性能测试记录。
        """

        return self.performance_record

    def plot(self):
        """
        重新绘制当前页面数据
        """

        if self.compare_mode:
            return self.display_compare(
                self.compare_result
            )

        if self.signal_data is None:
            return False

        return self.load_signal(
            self.signal_data
        )

    def refresh(self):
        """
        刷新当前页面数据
        """

        return self.plot()

    @staticmethod
    def get_signal_name(signal_data):
        """
        获取信号显示名称
        """

        if signal_data is None:
            return "Signal"

        name = getattr(
            signal_data,
            "name",
            ""
        )

        if not name:
            name = getattr(
                signal_data,
                "node",
                "Signal"
            )

        name = str(
            name
        ).strip()

        if name == "":
            name = "Signal"

        return name

    # =====================================================
    # Multi-shot Compare
    # =====================================================

    def display_compare(
            self,
            result
    ):
        """
        显示多炮号对比结果。
        """

        if result is None:
            return False

        success_items = result.success_items()

        if not success_items:
            return False

        valid_items = [
            item
            for item in success_items
            if item.signal_data is not None
        ]
        if not valid_items:
            return False

        self.clear()

        self.compare_mode = True
        self.compare_result = result
        self.signal_data = None

        first_signal = valid_items[0].signal_data

        self.update_axis_labels(
            first_signal
        )

        request = getattr(
            result,
            "request",
            None
        )

        node = getattr(
            request,
            "node",
            ""
        )

        signal_name = self.get_signal_name(
            first_signal
        )

        self.set_title(
            "{} Compare".format(
                signal_name
            )
        )

        for item in valid_items:

            signal_data = item.signal_data

            if signal_data is None:
                continue

            shot = item.shot

            key = "{}:{}".format(
                node,
                shot
            )

            overlay_curve = self.add_overlay_signal(
                signal_data=signal_data,
                key=key,
                replace=True
            )

            if overlay_curve is None:
                continue

        if self.overlay.is_empty():
            self.compare_mode = False
            self.compare_result = None

            self.set_status(
                "No compare data"
            )

            return False

        self.crosshair.set_data(
            getattr(
                first_signal,
                "x",
                None
            ),
            getattr(
                first_signal,
                "y",
                None
            )
        )

        self.btn_crosshair.blockSignals(
            True
        )

        self.btn_crosshair.setChecked(
            True
        )

        self.btn_crosshair.blockSignals(
            False
        )

        self.set_crosshair_enabled(
            True
        )

        self.btn_legend.blockSignals(
            True
        )

        self.btn_legend.setChecked(
            True
        )

        self.btn_legend.blockSignals(
            False
        )

        self.set_legend_visible(
            True
        )

        if getattr(
                self.config,
                "auto_range",
                True
        ):
            self.auto_scale()

        self.set_status(
            "{} Shot    {} Failed".format(
                result.success_count(),
                result.failed_count()
            )
        )

        return True

    def clear_compare(self):
        """
        清空多炮号对比结果。
        """

        self.compare_mode = False
        self.compare_result = None

        if self.overlay is not None:
            self.overlay.clear()

        if self.legend is not None:
            self.legend.clear()

        if self.crosshair is not None:
            self.crosshair.clear_data()

        if self.plot_widget is not None:
            self.plot_widget.clear_plot()

        self.signal_data = None
        self.current_curve_key = ""

        self.set_title(
            "Waveform"
        )

        self.set_status(
            "Ready"
        )

        self.set_coordinate_status(
            ""
        )

        return True

    # =====================================================
    # Axis
    # =====================================================

    def update_axis_labels(
            self,
            signal_data
    ):
        """
        根据 SignalData 设置坐标轴
        """

        if signal_data is None:
            return

        x_label = getattr(
            signal_data,
            "xlabel",
            None
        )

        if not x_label:
            x_label = getattr(
                signal_data,
                "x_label",
                "Time"
            )

        y_label = getattr(
            signal_data,
            "ylabel",
            None
        )

        if not y_label:
            y_label = getattr(
                signal_data,
                "y_label",
                "Value"
            )

        x_unit = getattr(
            signal_data,
            "x_unit",
            ""
        )

        y_unit = getattr(
            signal_data,
            "y_unit",
            ""
        )

        if not y_unit:
            y_unit = getattr(
                signal_data,
                "unit",
                ""
            )

        self.plot_widget.set_axis_labels(
            x_label=x_label,
            x_unit=x_unit,
            y_label=y_label,
            y_unit=y_unit
        )

    # =====================================================
    # Primary Legend
    # =====================================================

    def update_primary_legend(
            self,
            signal_data
    ):
        """
        更新主波形图例
        """

        if self.legend is None:
            return

        if self.plot_widget.curve is None:
            return

        signal_name = self.get_signal_name(
            signal_data
        )

        shot = getattr(
            signal_data,
            "shot",
            None
        )

        if shot is not None:
            signal_name = (
                "{}  [Shot {}]".format(
                    signal_name,
                    shot
                )
            )

        if self.legend.contains(
                self.plot_widget.curve
        ):

            self.legend.update_name(
                self.plot_widget.curve,
                signal_name
            )

        else:

            self.legend.add_curve(
                self.plot_widget.curve,
                signal_name
            )

    # =====================================================
    # Overlay Interface
    # =====================================================

    def add_overlay_signal(
            self,
            signal_data,
            key=None,
            color=None,
            width=None,
            replace=False
    ):
        """
        在当前页面增加一条叠加曲线
        """

        if signal_data is None:
            return None

        overlay_curve = self.overlay.add_signal(
            signal_data=signal_data,
            key=key,
            color=color,
            width=width,
            replace=replace
        )

        if overlay_curve is None:
            self.set_status(
                "Failed to add overlay"
            )

            return None

        if getattr(
                self.config,
                "auto_range",
                True
        ):
            self.auto_scale()

        self.update_overlay_status()

        return overlay_curve

    def remove_overlay_curve(self, key):
        """
        删除指定叠加曲线
        """

        result = self.overlay.remove_curve(
            key
        )

        self.update_overlay_status()

        return result

    def clear_overlay(self):
        """
        清空叠加曲线
        """

        self.overlay.clear()

        self.update_overlay_status()

    def overlay_count(self):
        """
        返回叠加曲线数量
        """

        if self.overlay is None:
            return 0

        return self.overlay.count()

    def update_overlay_status(self):
        """
        更新叠加曲线状态
        """

        primary_count = (
            self.plot_widget.point_count()
        )

        overlay_count = (
            self.overlay.count()
        )

        if primary_count > 0:

            self.set_status(
                "{} Points    {} Overlay".format(
                    primary_count,
                    overlay_count
                )
            )

        else:

            self.set_status(
                "{} Overlay".format(
                    overlay_count
                )
            )

    # =====================================================
    # Crosshair
    # =====================================================

    def on_crosshair_toggled(
            self,
            enabled
    ):
        """
        用户切换十字光标显示状态
        """

        enabled = bool(
            enabled
        )

        self.set_crosshair_enabled(
            enabled
        )

        if self.config is not None:
            self.config.show_crosshair = enabled

            self.config.save()

    def set_crosshair_enabled(
            self,
            enabled
    ):
        """
        启用或禁用十字光标
        """

        if self.crosshair is None:
            return

        self.crosshair.set_enabled(
            enabled
        )

        if not enabled:
            self.set_coordinate_status(
                ""
            )

    def is_crosshair_enabled(self):
        """
        返回十字光标启用状态
        """

        if self.crosshair is None:
            return False

        return self.crosshair.is_enabled()

    def on_crosshair_point_changed(
            self,
            x_value,
            y_value,
            index
    ):
        """
        十字光标采样点发生变化
        """

        self.set_coordinate_status(
            "X: {}    Y: {}    Index: {}".format(
                self.format_value(
                    x_value
                ),
                self.format_value(
                    y_value
                ),
                index
            )
        )

    def on_crosshair_point_cleared(self):
        """
        清空十字光标坐标状态
        """

        self.set_coordinate_status(
            ""
        )

    @staticmethod
    def format_value(value):
        """
        格式化显示数值
        """

        try:

            value = float(
                value
            )

        except Exception:

            return str(
                value
            )

        absolute_value = abs(
            value
        )

        if (
                absolute_value != 0.0
                and
                (
                        absolute_value >= 100000.0
                        or
                        absolute_value < 0.0001
                )
        ):
            return "{:.6e}".format(
                value
            )

        return "{:.6f}".format(
            value
        )

    # =====================================================
    # Legend
    # =====================================================

    def on_legend_toggled(
            self,
            visible
    ):
        """
        用户切换图例显示状态
        """

        visible = bool(
            visible
        )

        self.set_legend_visible(
            visible
        )

        if self.config is not None:
            self.config.show_legend = visible

            self.config.save()

    def set_legend_visible(
            self,
            visible
    ):
        """
        设置图例显示状态
        """

        if self.legend is None:
            return

        self.legend.set_visible(
            visible
        )

    def is_legend_visible(self):
        """
        返回图例显示状态
        """

        if self.legend is None:
            return False

        return self.legend.is_visible()

    # =====================================================
    # Plot Operations
    # =====================================================

    def auto_scale(self):
        """
        自动调整显示范围
        """

        if self.plot_widget is None:
            return

        if (
                not self.plot_widget.has_data()
                and
                self.overlay.is_empty()
        ):
            return

        self.plot_widget.enableAutoRange(
            axis="xy",
            enable=True
        )

        self.plot_widget.autoRange(
            padding=0.05
        )

    def clear(self):
        """
        清空主波形和所有叠加波形
        """

        self.signal_data = None

        self.plot_time = 0.0
        self.performance_record = None

        self.current_curve_key = ""
        self.compare_mode = False
        self.compare_result = None

        if self.overlay is not None:
            self.overlay.clear()

        if self.legend is not None:
            self.legend.clear()

        if self.crosshair is not None:
            self.crosshair.clear_data()

        if self.plot_widget is not None:
            self.plot_widget.clear_plot()

        self.set_title(
            "Waveform"
        )

        self.set_status(
            "Ready"
        )

        self.set_coordinate_status(
            ""
        )

    def has_data(self):
        """
        判断页面是否存在波形数据
        """

        if (
                self.plot_widget is not None
                and
                self.plot_widget.has_data()
        ):
            return True

        if (
                self.overlay is not None
                and
                not self.overlay.is_empty()
        ):
            return True

        return False

    # =====================================================
    # Plot Signals
    # =====================================================

    def on_plot_data_changed(
            self,
            x_data,
            y_data
    ):
        """
        主波形数据发生变化
        """

        if self.crosshair is not None:
            self.crosshair.set_data(
                x_data,
                y_data
            )

        self.set_status(
            "{} Points".format(
                y_data.size
            )
        )

    def on_plot_cleared(self):
        """
        主波形被清空
        """

        if self.crosshair is not None:
            self.crosshair.clear_data()

        self.set_coordinate_status(
            ""
        )

    # =====================================================
    # Overlay Signals
    # =====================================================

    def on_overlay_changed(
            self,
            key
    ):
        """
        叠加曲线发生变化
        """

        self.current_curve_key = str(
            key
        )

        self.update_overlay_status()

    def on_overlay_cleared(self):
        """
        叠加曲线全部清空
        """

        self.current_curve_key = ""

        self.update_overlay_status()

    # =====================================================
    # Export PNG
    # =====================================================

    def export_png(self):
        """
        导出当前波形图片
        """

        if not self.has_data():
            QMessageBox.information(
                self,
                "Export PNG",
                "No waveform data to export."
            )

            return False

        default_path = self.get_default_export_path(
            ".png"
        )

        filepath, selected_filter = (
            QFileDialog.getSaveFileName(
                self,
                "Export Waveform PNG",
                default_path,
                "PNG Image (*.png)"
            )
        )

        if not filepath:
            return False

        return self.exporter.export_png(
            filepath
        )

    # =====================================================
    # Export CSV
    # =====================================================

    def export_csv(self):
        """
        导出当前波形数据
        """

        if not self.has_data():
            QMessageBox.information(
                self,
                "Export CSV",
                "No waveform data to export."
            )

            return False

        default_path = self.get_default_export_path(
            ".csv"
        )

        filepath, selected_filter = (
            QFileDialog.getSaveFileName(
                self,
                "Export Waveform CSV",
                default_path,
                "CSV File (*.csv)"
            )
        )

        if not filepath:
            return False

        metadata = self.build_export_metadata()

        if self.overlay.count() > 0:

            overlay_data = (
                self.overlay.get_all_data()
            )

            if self.plot_widget.has_data():

                primary_key = "primary"

                primary_name = (
                    self.plot_widget.signal_name
                )

                primary_shot = None

                primary_node = (
                    self.plot_widget.node_path
                )

                if self.signal_data is not None:
                    primary_shot = getattr(
                        self.signal_data,
                        "shot",
                        None
                    )

                overlay_data = dict(
                    overlay_data
                )

                overlay_data[
                    primary_key
                ] = {
                    "name": primary_name,
                    "node": primary_node,
                    "shot": primary_shot,
                    "x": self.plot_widget.get_x_data(),
                    "y": self.plot_widget.get_y_data(),
                    "visible": True,
                    "color": getattr(
                        self.config,
                        "foreground",
                        "w"
                    ),
                    "width": 1.5
                }

            return self.exporter.export_overlay_csv(
                filepath=filepath,
                overlay_data=overlay_data,
                x_header=self.get_x_header(),
                metadata=metadata
            )

        return self.exporter.export_csv(
            filepath=filepath,
            x_data=self.plot_widget.get_x_data(),
            y_data=self.plot_widget.get_y_data(),
            x_header=self.get_x_header(),
            y_header=self.get_y_header(),
            metadata=metadata
        )

    # =====================================================
    # Export Metadata
    # =====================================================

    def get_default_export_path(
            self,
            extension
    ):
        """
        获取默认导出路径
        """

        filename = self.get_export_filename(
            extension
        )

        export_path = getattr(
            self.config,
            "export_path",
            ""
        )

        if export_path:
            return os.path.join(
                export_path,
                filename
            )

        return filename

    def get_export_filename(
            self,
            extension
    ):
        """
        生成默认导出文件名
        """

        name = self.title()

        if name == "":
            name = "waveform"

        name = WaveformExport.normalize_filename(
            name
        )

        shot = None

        if self.signal_data is not None:
            shot = getattr(
                self.signal_data,
                "shot",
                None
            )

        if shot is not None:
            name = "{}_Shot_{}".format(
                name,
                shot
            )

        elif self.compare_mode:
            name = "{}_MultiShot".format(
                name
            )

        return WaveformExport.ensure_extension(
            name,
            extension
        )

    def build_export_metadata(self):
        """
        生成导出元数据
        """

        metadata = {
            "Title": self.title()
        }

        if self.compare_mode:

            request = getattr(
                self.compare_result,
                "request",
                None
            )

            node_path = getattr(
                request,
                "node",
                ""
            )

            shots = getattr(
                request,
                "shots",
                []
            )

            if node_path:
                metadata[
                    "Node"
                ] = node_path

            if shots:
                metadata[
                    "Shots"
                ] = ", ".join(
                    str(shot)
                    for shot in shots
                )

            return metadata

        if self.signal_data is None:
            return metadata

        node_path = getattr(
            self.signal_data,
            "node",
            ""
        )

        shot = getattr(
            self.signal_data,
            "shot",
            None
        )

        if node_path:
            metadata[
                "Node"
            ] = node_path

        if shot is not None:
            metadata[
                "Shot"
            ] = shot

        return metadata

    def get_x_header(self):
        """
        返回横坐标导出列名
        """

        if self.signal_data is None:
            return "X"

        x_label = getattr(
            self.signal_data,
            "xlabel",
            None
        )

        if not x_label:
            x_label = getattr(
                self.signal_data,
                "x_label",
                "X"
            )

        x_unit = getattr(
            self.signal_data,
            "x_unit",
            ""
        )

        if x_unit:
            return "{} ({})".format(
                x_label,
                x_unit
            )

        return x_label

    def get_y_header(self):
        """
        返回纵坐标导出列名
        """

        if self.signal_data is None:
            return "Y"

        y_label = getattr(
            self.signal_data,
            "ylabel",
            None
        )

        if not y_label:
            y_label = getattr(
                self.signal_data,
                "y_label",
                self.get_signal_name(
                    self.signal_data
                )
            )

        y_unit = getattr(
            self.signal_data,
            "y_unit",
            ""
        )

        if not y_unit:
            y_unit = getattr(
                self.signal_data,
                "unit",
                ""
            )

        if y_unit:
            return "{} ({})".format(
                y_label,
                y_unit
            )

        return y_label

    # =====================================================
    # Export Signals
    # =====================================================

    def on_export_started(
            self,
            filepath
    ):
        """
        导出开始
        """

        self.set_status(
            "Exporting..."
        )

    def on_export_finished(
            self,
            filepath
    ):
        """
        导出完成
        """

        self.set_status(
            "Exported : {}".format(
                filepath
            )
        )

    def on_export_error(
            self,
            message
    ):
        """
        导出错误
        """

        self.set_status(
            "Export Error"
        )

        QMessageBox.warning(
            self,
            "Export Error",
            str(message)
        )

    # =====================================================
    # Configuration
    # =====================================================

    def apply_config(self):
        """
        应用当前配置
        """

        if self.plot_widget is not None:
            self.plot_widget.apply_config()

        if self.exporter is not None:
            self.exporter.apply_config(
                self.config
            )

        self.apply_dark_plot_style()

        auto_range = bool(
            getattr(
                self.config,
                "auto_range",
                True
            )
        )

        self.plot_widget.set_auto_range_enabled(
            auto_range
        )

        crosshair_enabled = bool(
            getattr(
                self.config,
                "show_crosshair",
                True
            )
        )

        self.btn_crosshair.blockSignals(
            True
        )

        self.btn_crosshair.setChecked(
            crosshair_enabled
        )

        self.btn_crosshair.blockSignals(
            False
        )

        self.set_crosshair_enabled(
            crosshair_enabled
        )

        legend_visible = bool(
            getattr(
                self.config,
                "show_legend",
                True
            )
        )

        self.btn_legend.blockSignals(
            True
        )

        self.btn_legend.setChecked(
            legend_visible
        )

        self.btn_legend.blockSignals(
            False
        )

        self.set_legend_visible(
            legend_visible
        )

    def apply_dark_plot_style(self):
        """
        应用白色背景和黑色前景样式

        config.ini:
        background = w
        foreground = k
        """

        background = getattr(
            self.config,
            "background",
            "w"
        )

        foreground = getattr(
            self.config,
            "foreground",
            "k"
        )

        if self.legend is not None:
            self.legend.set_style(
                background_color=background,
                foreground_color=foreground,
                border_color="808080"
            )

        if self.crosshair is not None:
            self.crosshair.set_line_color(
                "808080"
            )

            self.crosshair.set_point_color(
                "r"
            )

            self.crosshair.set_label_style(
                text_color="k",
                background_color="w",
                border_color="808080"
            )

    # =====================================================
    # Close
    # =====================================================

    def closeEvent(self, event):
        """
        页面关闭时释放绘图模块
        """

        if self.crosshair is not None:
            self.crosshair.remove()

            self.crosshair = None

        if self.overlay is not None:
            self.overlay.remove()

            self.overlay = None

        if self.legend is not None:
            self.legend.remove()

            self.legend = None

        self.exporter = None

        super(WaveformPanel, self).closeEvent(
            event
        )
