# -*- coding: utf-8 -*-

"""
==========================================================
Project : NNBI_database
File    : crosshair.py
Author  :
Date    :
Description : Waveform Crosshair Controller
==========================================================
"""

import numpy as np
import pyqtgraph as pg

from PySide2.QtCore import (
    QObject,
    Signal
)


class Crosshair(QObject):
    """
    波形十字光标控制器

    功能：
    1. 显示垂直参考线
    2. 显示水平参考线
    3. 跟踪鼠标坐标
    4. 定位距离鼠标最近的采样点
    5. 显示当前采样点 X、Y 值
    6. 支持动态启用和禁用
    """

    # 当前采样点变化
    pointChanged = Signal(
        float,
        float,
        int
    )

    # 鼠标离开有效绘图区域
    pointCleared = Signal()

    def __init__(
            self,
            plot_widget,
            parent=None
    ):

        super(Crosshair, self).__init__(
            parent
        )

        self.plot_widget = plot_widget

        self.plot_item = None
        self.view_box = None
        self.scene = None

        # =================================================
        # Crosshair Items
        # =================================================

        self.vertical_line = None
        self.horizontal_line = None
        self.value_label = None
        self.point_item = None

        # =================================================
        # Data
        # =================================================

        self.x_data = np.array(
            [],
            dtype=np.float64
        )

        self.y_data = np.array(
            [],
            dtype=np.float64
        )

        self.current_index = -1
        self.current_x = 0.0
        self.current_y = 0.0

        # =================================================
        # State
        # =================================================

        self.enabled = True
        self.snap_to_data = True
        self.show_horizontal_line = True
        self.show_point = True
        self.show_label = True

        # =================================================
        # Mouse Proxy
        # =================================================

        self.mouse_proxy = None

        self.init_crosshair()
        self.create_connections()

    # =====================================================
    # Initialize
    # =====================================================

    def init_crosshair(self):
        """
        初始化十字光标图形对象
        """

        if self.plot_widget is None:
            return

        self.plot_item = (
            self.plot_widget.getPlotItem()
        )

        self.view_box = (
            self.plot_item.getViewBox()
        )

        self.scene = self.plot_widget.scene()

        # =================================================
        # Vertical Line
        # =================================================

        self.vertical_line = pg.InfiniteLine(
            angle=90,
            movable=False,
            pen=pg.mkPen(
                "808080",
                width=1
            )
        )

        self.vertical_line.setZValue(
            1000
        )

        # =================================================
        # Horizontal Line
        # =================================================

        self.horizontal_line = pg.InfiniteLine(
            angle=0,
            movable=False,
            pen=pg.mkPen(
                "808080",
                width=1
            )
        )

        self.horizontal_line.setZValue(
            1000
        )

        # =================================================
        # Current Point
        # =================================================

        self.point_item = pg.ScatterPlotItem(
            size=8,
            pen=pg.mkPen(
                "w",
                width=1
            ),
            brush=pg.mkBrush(
                "y"
            )
        )

        self.point_item.setZValue(
            1001
        )

        # =================================================
        # Value Label
        # =================================================

        self.value_label = pg.TextItem(
            text="",
            anchor=(0, 1),
            border=pg.mkPen(
                "808080"
            ),
            fill=pg.mkBrush(
                0,
                0,
                0,
                200
            )
        )

        self.value_label.setColor(
            "w"
        )

        self.value_label.setZValue(
            1002
        )

        # =================================================
        # Add Items
        # =================================================

        self.plot_item.addItem(
            self.vertical_line,
            ignoreBounds=True
        )

        self.plot_item.addItem(
            self.horizontal_line,
            ignoreBounds=True
        )

        self.plot_item.addItem(
            self.point_item,
            ignoreBounds=True
        )

        self.plot_item.addItem(
            self.value_label,
            ignoreBounds=True
        )

        self.hide()

    # =====================================================
    # Connections
    # =====================================================

    def create_connections(self):
        """
        创建鼠标移动连接
        """

        if self.scene is None:
            return

        self.mouse_proxy = pg.SignalProxy(
            self.scene.sigMouseMoved,
            rateLimit=60,
            slot=self.on_mouse_moved
        )

    # =====================================================
    # Data
    # =====================================================

    def set_data(
            self,
            x_data,
            y_data
    ):
        """
        设置用于十字光标定位的数据
        """

        self.x_data = self.convert_array(
            x_data
        )

        self.y_data = self.convert_array(
            y_data
        )

        if (
                self.x_data.size == 0
                or
                self.y_data.size == 0
        ):
            self.clear_data()

            return False

        minimum_size = min(
            self.x_data.size,
            self.y_data.size
        )

        self.x_data = self.x_data[
            :minimum_size
        ]

        self.y_data = self.y_data[
            :minimum_size
        ]

        valid_mask = (
                np.isfinite(self.x_data) &
                np.isfinite(self.y_data)
        )

        self.x_data = self.x_data[
            valid_mask
        ]

        self.y_data = self.y_data[
            valid_mask
        ]

        if self.x_data.size == 0:
            self.clear_data()

            return False

        self.current_index = -1

        return True

    @staticmethod
    def convert_array(data):
        """
        将数据转换为一维浮点数组
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

            return np.array(
                [],
                dtype=np.float64
            )

    def clear_data(self):
        """
        清空数据
        """

        self.x_data = np.array(
            [],
            dtype=np.float64
        )

        self.y_data = np.array(
            [],
            dtype=np.float64
        )

        self.current_index = -1
        self.current_x = 0.0
        self.current_y = 0.0

        self.hide()

        self.pointCleared.emit()

    # =====================================================
    # Mouse Event
    # =====================================================

    def on_mouse_moved(self, event):
        """
        鼠标移动事件
        """

        if not self.enabled:
            return

        if self.plot_item is None:
            return

        if self.view_box is None:
            return

        if self.x_data.size == 0:
            return

        if isinstance(event, tuple):
            scene_position = event[0]
        else:
            scene_position = event

        if scene_position is None:
            return

        plot_rect = (
            self.plot_item.sceneBoundingRect()
        )

        if not plot_rect.contains(
                scene_position
        ):
            self.hide()

            self.pointCleared.emit()

            return

        mouse_point = (
            self.view_box.mapSceneToView(
                scene_position
            )
        )

        mouse_x = float(
            mouse_point.x()
        )

        mouse_y = float(
            mouse_point.y()
        )

        if self.snap_to_data:

            index = self.find_nearest_index(
                mouse_x
            )

            if index < 0:
                return

            x_value = float(
                self.x_data[index]
            )

            y_value = float(
                self.y_data[index]
            )

        else:

            index = -1
            x_value = mouse_x
            y_value = mouse_y

        self.update_position(
            x_value,
            y_value,
            index
        )

    # =====================================================
    # Nearest Point
    # =====================================================

    def find_nearest_index(self, x_value):
        """
        查找距离当前 X 坐标最近的数据点
        """

        if self.x_data.size == 0:
            return -1

        if self.x_data.size == 1:
            return 0

        # X 轴单调递增时使用 searchsorted，
        # 提高长波形的查询速度
        if np.all(
                np.diff(self.x_data) >= 0
        ):

            index = int(
                np.searchsorted(
                    self.x_data,
                    x_value
                )
            )

            if index <= 0:
                return 0

            if index >= self.x_data.size:
                return self.x_data.size - 1

            left_index = index - 1
            right_index = index

            left_distance = abs(
                x_value -
                self.x_data[left_index]
            )

            right_distance = abs(
                self.x_data[right_index] -
                x_value
            )

            if left_distance <= right_distance:
                return left_index

            return right_index

        # 非单调 X 数据使用全局距离搜索
        return int(
            np.argmin(
                np.abs(
                    self.x_data -
                    x_value
                )
            )
        )

    # =====================================================
    # Position
    # =====================================================

    def update_position(
            self,
            x_value,
            y_value,
            index=-1
    ):
        """
        更新十字光标位置
        """

        self.current_x = float(
            x_value
        )

        self.current_y = float(
            y_value
        )

        self.current_index = int(
            index
        )

        if self.vertical_line is not None:
            self.vertical_line.setPos(
                self.current_x
            )

            self.vertical_line.show()

        if self.horizontal_line is not None:

            if self.show_horizontal_line:

                self.horizontal_line.setPos(
                    self.current_y
                )

                self.horizontal_line.show()

            else:

                self.horizontal_line.hide()

        if self.point_item is not None:

            if self.show_point:

                self.point_item.setData(
                    [
                        self.current_x
                    ],
                    [
                        self.current_y
                    ]
                )

                self.point_item.show()

            else:

                self.point_item.hide()

        if self.value_label is not None:

            if self.show_label:

                self.value_label.setText(
                    self.format_label(
                        self.current_x,
                        self.current_y,
                        self.current_index
                    )
                )

                self.value_label.setPos(
                    self.current_x,
                    self.current_y
                )

                self.value_label.show()

            else:

                self.value_label.hide()

        self.pointChanged.emit(
            self.current_x,
            self.current_y,
            self.current_index
        )

    @staticmethod
    def format_value(value):
        """
        格式化坐标数值
        """

        value = float(
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

    def format_label(
            self,
            x_value,
            y_value,
            index
    ):
        """
        生成坐标标签
        """

        text = "X : {}\nY : {}".format(
            self.format_value(
                x_value
            ),
            self.format_value(
                y_value
            )
        )

        if index >= 0:
            text += "\nIndex : {}".format(
                index
            )

        return text

    # =====================================================
    # Visibility
    # =====================================================

    def show(self):
        """
        显示十字光标
        """

        if not self.enabled:
            return

        if self.vertical_line is not None:
            self.vertical_line.show()

        if (
                self.horizontal_line is not None
                and
                self.show_horizontal_line
        ):
            self.horizontal_line.show()

        if (
                self.point_item is not None
                and
                self.show_point
        ):
            self.point_item.show()

        if (
                self.value_label is not None
                and
                self.show_label
        ):
            self.value_label.show()

    def hide(self):
        """
        隐藏十字光标
        """

        if self.vertical_line is not None:
            self.vertical_line.hide()

        if self.horizontal_line is not None:
            self.horizontal_line.hide()

        if self.point_item is not None:
            self.point_item.hide()

        if self.value_label is not None:
            self.value_label.hide()

    # =====================================================
    # Configuration
    # =====================================================

    def set_enabled(self, enabled):
        """
        启用或禁用十字光标
        """

        self.enabled = bool(
            enabled
        )

        if not self.enabled:
            self.hide()

            self.current_index = -1

            self.pointCleared.emit()

    def is_enabled(self):
        """
        返回十字光标启用状态
        """

        return self.enabled

    def set_snap_to_data(self, enabled):
        """
        设置是否吸附到最近采样点
        """

        self.snap_to_data = bool(
            enabled
        )

    def set_horizontal_line_visible(
            self,
            visible
    ):
        """
        设置水平参考线是否显示
        """

        self.show_horizontal_line = bool(
            visible
        )

        if not self.show_horizontal_line:

            if self.horizontal_line is not None:
                self.horizontal_line.hide()

    def set_point_visible(self, visible):
        """
        设置采样点标记是否显示
        """

        self.show_point = bool(
            visible
        )

        if not self.show_point:

            if self.point_item is not None:
                self.point_item.hide()

    def set_label_visible(self, visible):
        """
        设置坐标标签是否显示
        """

        self.show_label = bool(
            visible
        )

        if not self.show_label:

            if self.value_label is not None:
                self.value_label.hide()

    # =====================================================
    # Style
    # =====================================================

    def set_line_color(self, color):
        """
        设置十字线颜色
        """

        try:

            pen = pg.mkPen(
                color,
                width=1
            )

        except Exception:

            pen = pg.mkPen(
                "808080",
                width=1
            )

        if self.vertical_line is not None:
            self.vertical_line.setPen(
                pen
            )

        if self.horizontal_line is not None:
            self.horizontal_line.setPen(
                pen
            )

    def set_point_color(self, color):
        """
        设置采样点颜色
        """

        try:

            brush = pg.mkBrush(
                color
            )

        except Exception:

            brush = pg.mkBrush(
                "y"
            )

        if self.point_item is not None:
            self.point_item.setBrush(
                brush
            )

    def set_label_style(
            self,
            text_color="k",
            background_color="w",
            border_color="808080"
    ):
        """
        设置坐标标签样式
        """

        if self.value_label is None:
            return

        try:

            self.value_label.setColor(
                text_color
            )

        except Exception:

            self.value_label.setColor(
                "k"
            )

        try:

            self.value_label.fill = pg.mkBrush(
                background_color
            )

        except Exception:

            self.value_label.fill = pg.mkBrush(
                "w"
            )

        try:

            self.value_label.border = pg.mkPen(
                border_color
            )

        except Exception:

            self.value_label.border = pg.mkPen(
                "808080"
            )

        self.value_label.update()

    # =====================================================
    # Current Point Interface
    # =====================================================

    def current_point(self):
        """
        返回当前采样点

        返回：
        (x, y, index)
        """

        if self.current_index < 0:
            return (
                None,
                None,
                -1
            )

        return (
            self.current_x,
            self.current_y,
            self.current_index
        )

    # =====================================================
    # Remove
    # =====================================================

    def remove(self):
        """
        从 PlotItem 中移除十字光标
        """

        self.hide()

        if self.plot_item is not None:

            if self.vertical_line is not None:
                self.plot_item.removeItem(
                    self.vertical_line
                )

            if self.horizontal_line is not None:
                self.plot_item.removeItem(
                    self.horizontal_line
                )

            if self.point_item is not None:
                self.plot_item.removeItem(
                    self.point_item
                )

            if self.value_label is not None:
                self.plot_item.removeItem(
                    self.value_label
                )

        self.vertical_line = None
        self.horizontal_line = None
        self.point_item = None
        self.value_label = None

        self.mouse_proxy = None
