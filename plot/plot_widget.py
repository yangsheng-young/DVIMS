# -*- coding: utf-8 -*-

"""
==========================================================
Project : NNBI_database
File    : plot_widget.py
Author  :
Date    :
Description : Basic PyQtGraph Waveform Plot Widget
==========================================================
"""

import numpy as np
import pyqtgraph as pg

from PySide2.QtCore import Signal


# 当前工程运行环境：
# Python 3.6.6
# PySide2
# pyqtgraph 0.11.1


class WaveformPlotWidget(pg.PlotWidget):
    """
    基础波形绘图控件

    功能：
    1. 显示单条波形
    2. 设置坐标轴名称和单位
    3. 网格显示
    4. 鼠标缩放和平移
    5. 自动缩放
    6. 清空波形
    7. 动态应用配置
    """

    # 波形数据更新信号
    dataChanged = Signal(object, object)

    # 波形清空信号
    plotCleared = Signal()

    def __init__(self, config=None, parent=None):

        super(WaveformPlotWidget, self).__init__(
            parent=parent
        )

        self.config = config

        # =================================================
        # Current Data
        # =================================================

        self.x_data = np.array(
            [],
            dtype=np.float64
        )

        self.y_data = np.array(
            [],
            dtype=np.float64
        )

        # =================================================
        # Signal Information
        # =================================================

        self.signal_name = "Signal"
        self.node_path = ""

        self.x_label = "Time"
        self.x_unit = ""

        self.y_label = "Value"
        self.y_unit = ""

        # =================================================
        # Plot Item
        # =================================================

        self.plot_item = self.getPlotItem()

        self.view_box = self.plot_item.getViewBox()

        self.curve = None

        # =================================================
        # Config
        # =================================================

        self.background_color = "w"
        self.foreground_color = "k"

        self.show_grid = True
        self.wheel_zoom = True
        self.auto_range_enabled = True

        self.antialias = True

        self.load_config()

        self.init_plot()

    # =====================================================
    # Config
    # =====================================================

    def load_config(self):
        """
        从 Config 中读取绘图配置
        """

        if self.config is None:
            return

        self.background_color = self.normalize_color(
            getattr(
                self.config,
                "background",
                "w"
            ),
            "w"
        )

        self.foreground_color = self.normalize_color(
            getattr(
                self.config,
                "foreground",
                "k"
            ),
            "k"
        )

        self.show_grid = bool(
            getattr(
                self.config,
                "show_grid",
                True
            )
        )

        self.wheel_zoom = bool(
            getattr(
                self.config,
                "wheel_zoom",
                True
            )
        )

        self.auto_range_enabled = bool(
            getattr(
                self.config,
                "auto_range",
                True
            )
        )

        self.antialias = bool(
            getattr(
                self.config,
                "antialias",
                True
            )
        )

    def apply_config(self):
        """
        重新应用当前配置
        """

        self.load_config()

        pg.setConfigOptions(
            antialias=self.antialias
        )

        self.setBackground(
            self.background_color
        )

        self.showGrid(
            x=self.show_grid,
            y=self.show_grid,
            alpha=0.3
        )

        self.setMouseEnabled(
            x=self.wheel_zoom,
            y=self.wheel_zoom
        )

        if self.curve is not None:
            self.curve.setPen(
                pg.mkPen(
                    self.foreground_color,
                    width=1.5
                )
            )

        self.update_axis_style()

        if self.auto_range_enabled:
            self.auto_scale()

    # =====================================================
    # Initialize
    # =====================================================

    def init_plot(self):
        """
        初始化绘图区域
        """

        pg.setConfigOptions(
            antialias=self.antialias
        )

        self.setBackground(
            self.background_color
        )

        self.plot_item.setMenuEnabled(
            True
        )

        self.plot_item.hideButtons()

        self.showGrid(
            x=self.show_grid,
            y=self.show_grid,
            alpha=0.3
        )

        self.setMouseEnabled(
            x=self.wheel_zoom,
            y=self.wheel_zoom
        )

        self.plot_item.setClipToView(
            True
        )

        self.plot_item.setDownsampling(
            auto=True,
            mode="peak"
        )

        self.curve = self.plot_item.plot(
            [],
            [],
            pen=pg.mkPen(
                self.foreground_color,
                width=1.5
            ),
            name=self.signal_name
        )

        self.set_axis_labels(
            self.x_label,
            self.x_unit,
            self.y_label,
            self.y_unit
        )

        self.update_axis_style()

    # =====================================================
    # Color
    # =====================================================

    @staticmethod
    def normalize_color(color, default_color):
        """
        将完整颜色名称转换为 pyqtgraph 0.11.1
        能稳定识别的颜色格式
        """

        color_map = {
            "white": "w",
            "black": "k",
            "red": "r",
            "green": "g",
            "blue": "b",
            "yellow": "y",
            "cyan": "c",
            "magenta": "m",
            "gray": "808080",
            "grey": "808080"
        }

        if color is None:
            return default_color

        color_text = str(color).strip()

        if color_text == "":
            return default_color

        lower_color = color_text.lower()

        if lower_color in color_map:
            return color_map[lower_color]

        try:

            pg.mkColor(color_text)

            return color_text

        except Exception:

            return default_color

    def axis_color(self):
        """
        根据背景颜色选择坐标轴颜色
        """

        light_backgrounds = (
            "w",
            "white",
            "#ffffff",
            "ffffff"
        )

        background = str(
            self.background_color
        ).strip().lower()

        if background in light_backgrounds:
            return "k"

        return "w"

    # =====================================================
    # Axis
    # =====================================================

    def set_axis_labels(
            self,
            x_label="Time",
            x_unit="",
            y_label="Value",
            y_unit=""
    ):
        """
        设置横坐标和纵坐标名称
        """

        self.x_label = str(
            x_label
        ) if x_label is not None else ""

        self.x_unit = str(
            x_unit
        ) if x_unit is not None else ""

        self.y_label = str(
            y_label
        ) if y_label is not None else ""

        self.y_unit = str(
            y_unit
        ) if y_unit is not None else ""

        self.plot_item.setLabel(
            "bottom",
            text=self.x_label,
            units=self.x_unit
        )

        self.plot_item.setLabel(
            "left",
            text=self.y_label,
            units=self.y_unit
        )

        self.update_axis_style()

    def update_axis_style(self):
        """
        更新坐标轴颜色
        """

        color = self.axis_color()

        pen = pg.mkPen(
            color
        )

        text_pen = pg.mkPen(
            color
        )

        bottom_axis = self.plot_item.getAxis(
            "bottom"
        )

        left_axis = self.plot_item.getAxis(
            "left"
        )

        bottom_axis.setPen(
            pen
        )

        bottom_axis.setTextPen(
            text_pen
        )

        left_axis.setPen(
            pen
        )

        left_axis.setTextPen(
            text_pen
        )

    # =====================================================
    # Signal Information
    # =====================================================

    def set_signal_name(self, name):
        """
        设置当前信号名称
        """

        if name is None:
            name = "Signal"

        name = str(name).strip()

        if name == "":
            name = "Signal"

        self.signal_name = name

        if self.curve is not None:
            self.curve.opts["name"] = (
                self.signal_name
            )

    def set_node_path(self, node_path):
        """
        保存当前节点路径
        """

        if node_path is None:
            self.node_path = ""
        else:
            self.node_path = str(
                node_path
            ).strip()

    # =====================================================
    # Data Check
    # =====================================================

    @staticmethod
    def convert_array(data):
        """
        将输入数据转换为一维 numpy 数组
        """

        if data is None:
            return np.array(
                [],
                dtype=np.float64
            )

        array = np.asarray(
            data
        )

        array = np.squeeze(
            array
        )

        if array.ndim == 0:
            array = array.reshape(
                1
            )

        if array.ndim != 1:
            array = array.reshape(
                -1
            )

        try:

            return array.astype(
                np.float64
            )

        except Exception:

            return np.asarray(
                array,
                dtype=np.float64
            )

    @staticmethod
    def remove_invalid_data(x_data, y_data):
        """
        删除 NaN 和无穷大数据
        """

        if x_data.size == 0:
            return x_data, y_data

        if y_data.size == 0:
            return x_data, y_data

        valid_mask = (
                np.isfinite(x_data) &
                np.isfinite(y_data)
        )

        return (
            x_data[valid_mask],
            y_data[valid_mask]
        )

    # =====================================================
    # Plot
    # =====================================================

    def set_data(
            self,
            x_data,
            y_data,
            signal_name=None,
            node_path=None
    ):
        """
        设置并显示波形数据
        """

        y_array = self.convert_array(
            y_data
        )

        if y_array.size == 0:
            self.clear_plot()

            return False

        x_array = self.convert_array(
            x_data
        )

        if x_array.size == 0:
            x_array = np.arange(
                y_array.size,
                dtype=np.float64
            )

        if x_array.size != y_array.size:
            minimum_size = min(
                x_array.size,
                y_array.size
            )

            x_array = x_array[
                :minimum_size
            ]

            y_array = y_array[
                :minimum_size
            ]

        x_array, y_array = (
            self.remove_invalid_data(
                x_array,
                y_array
            )
        )

        if y_array.size == 0:
            self.clear_plot()

            return False

        self.x_data = x_array

        self.y_data = y_array

        if signal_name is not None:
            self.set_signal_name(
                signal_name
            )

        if node_path is not None:
            self.set_node_path(
                node_path
            )

        self.curve.setData(
            self.x_data,
            self.y_data
        )

        if self.auto_range_enabled:
            self.auto_scale()

        self.dataChanged.emit(
            self.x_data,
            self.y_data
        )

        return True

    def load_signal(self, signal_data):
        """
        加载 DataLoader 返回的 SignalData
        """

        if signal_data is None:
            return False

        x_data = getattr(
            signal_data,
            "x",
            None
        )

        y_data = getattr(
            signal_data,
            "y",
            None
        )

        signal_name = getattr(
            signal_data,
            "name",
            "Signal"
        )

        node_path = getattr(
            signal_data,
            "node",
            ""
        )

        x_label = getattr(
            signal_data,
            "x_label",
            "Time"
        )

        x_unit = getattr(
            signal_data,
            "x_unit",
            ""
        )

        y_label = getattr(
            signal_data,
            "y_label",
            signal_name
        )

        y_unit = getattr(
            signal_data,
            "y_unit",
            ""
        )

        self.set_axis_labels(
            x_label,
            x_unit,
            y_label,
            y_unit
        )

        return self.set_data(
            x_data,
            y_data,
            signal_name,
            node_path
        )

    # =====================================================
    # Plot Operation
    # =====================================================

    def auto_scale(self):
        """
        自动调整 X、Y 显示范围
        """

        if self.y_data.size == 0:
            return

        self.enableAutoRange(
            axis="xy",
            enable=True
        )

        self.autoRange(
            padding=0.05
        )

    def clear_plot(self):
        """
        清空当前波形
        """

        self.x_data = np.array(
            [],
            dtype=np.float64
        )

        self.y_data = np.array(
            [],
            dtype=np.float64
        )

        self.signal_name = "Signal"
        self.node_path = ""

        if self.curve is not None:
            self.curve.setData(
                [],
                []
            )

        self.plotCleared.emit()

    def set_grid_visible(self, visible):
        """
        设置网格显示状态
        """

        self.show_grid = bool(
            visible
        )

        self.showGrid(
            x=self.show_grid,
            y=self.show_grid,
            alpha=0.3
        )

    def set_zoom_enabled(self, enabled):
        """
        设置鼠标缩放和平移状态
        """

        self.wheel_zoom = bool(
            enabled
        )

        self.setMouseEnabled(
            x=self.wheel_zoom,
            y=self.wheel_zoom
        )

    def set_auto_range_enabled(self, enabled):
        """
        设置自动范围状态
        """

        self.auto_range_enabled = bool(
            enabled
        )

        if self.auto_range_enabled:
            self.auto_scale()

    def set_curve_color(self, color):
        """
        设置曲线颜色
        """

        color = self.normalize_color(
            color,
            self.foreground_color
        )

        self.foreground_color = color

        if self.curve is not None:
            self.curve.setPen(
                pg.mkPen(
                    self.foreground_color,
                    width=1.5
                )
            )

    def set_curve_width(self, width):
        """
        设置曲线宽度
        """

        try:
            width = float(width)

        except Exception:
            width = 1.5

        if width <= 0:
            width = 1.5

        if self.curve is not None:
            self.curve.setPen(
                pg.mkPen(
                    self.foreground_color,
                    width=width
                )
            )

    # =====================================================
    # Data Interface
    # =====================================================

    def get_x_data(self):
        """
        获取当前 X 数据副本
        """

        return self.x_data.copy()

    def get_y_data(self):
        """
        获取当前 Y 数据副本
        """

        return self.y_data.copy()

    def get_data(self):
        """
        获取当前 X、Y 数据副本
        """

        return (
            self.get_x_data(),
            self.get_y_data()
        )

    def point_count(self):
        """
        返回当前采样点数量
        """

        return int(
            self.y_data.size
        )

    def has_data(self):
        """
        判断当前是否存在波形数据
        """

        return self.y_data.size > 0
