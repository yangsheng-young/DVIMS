# -*- coding: utf-8 -*-

"""
==========================================================
Project : NNBI_database
File    : overlay.py
Author  :
Date    :
Description : Waveform Overlay Manager
==========================================================
"""

import numpy as np
import pyqtgraph as pg

from PySide2.QtCore import (
    QObject,
    Signal
)


class OverlayCurve(object):
    """
    单条叠加曲线的数据对象
    """

    def __init__(
            self,
            key,
            name,
            curve,
            x_data,
            y_data,
            color,
            width=1.5,
            node_path="",
            shot=None,
            signal_data=None
    ):
        self.key = str(key)
        self.name = str(name)

        self.curve = curve

        self.x_data = x_data
        self.y_data = y_data

        self.color = color
        self.width = float(width)

        self.node_path = str(
            node_path
        ) if node_path is not None else ""

        self.shot = shot
        self.signal_data = signal_data

        self.visible = True

    def point_count(self):
        """
        返回曲线采样点数量
        """

        if self.y_data is None:
            return 0

        return int(
            self.y_data.size
        )

    def has_data(self):
        """
        判断曲线是否存在有效数据
        """

        return self.point_count() > 0


class WaveformOverlay(QObject):
    """
    波形叠加曲线管理器

    功能：
    1. 在同一个 PlotWidget 中添加多条曲线
    2. 更新指定曲线数据
    3. 删除指定曲线
    4. 清空全部曲线
    5. 设置曲线颜色、宽度和显示状态
    6. 管理曲线名称、节点路径和 Shot
    7. 与 WaveformLegend 联动
    """

    curveAdded = Signal(str)
    curveUpdated = Signal(str)
    curveRemoved = Signal(str)
    curveVisibilityChanged = Signal(str, bool)
    overlayCleared = Signal()
    dataChanged = Signal()

    def __init__(
            self,
            plot_widget,
            legend_manager=None,
            parent=None
    ):

        super(WaveformOverlay, self).__init__(
            parent
        )

        self.plot_widget = plot_widget
        self.legend_manager = legend_manager

        self.plot_item = None

        # key -> OverlayCurve
        self.curves = {}

        # =================================================
        # Style
        # =================================================

        self.background_color = "w"
        self.foreground_color = "k"

        self.default_width = 1.5

        # 第一条曲线采用配置文件中的 foreground = k。
        # 后续曲线采用适合白色背景的高对比度颜色。
        self.color_cycle = [
            "r",
            "b",
            "g",
            "m",
            "c",
            "ff8800",
            "800080",
            "008080",
            "aa0000",
            "0066cc",
            "666666"
        ]

        self.color_index = 0

        self.init_overlay()

    # =====================================================
    # Initialize
    # =====================================================

    def init_overlay(self):
        """
        初始化叠加管理器
        """

        if self.plot_widget is None:
            return

        try:

            self.plot_item = (
                self.plot_widget.getPlotItem()
            )

        except Exception:

            self.plot_item = None

    # =====================================================
    # Data Conversion
    # =====================================================

    @staticmethod
    def convert_array(data):
        """
        将输入数据转换为一维浮点数组
        """

        if data is None:
            return np.array(
                [],
                dtype=np.float64
            )

        try:

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

            return array.astype(
                np.float64
            )

        except Exception:

            return np.array(
                [],
                dtype=np.float64
            )

    @classmethod
    def prepare_data(
            cls,
            x_data,
            y_data
    ):
        """
        校验并整理 X、Y 数据
        """

        y_array = cls.convert_array(
            y_data
        )

        if y_array.size == 0:
            return (
                np.array(
                    [],
                    dtype=np.float64
                ),
                np.array(
                    [],
                    dtype=np.float64
                )
            )

        x_array = cls.convert_array(
            x_data
        )

        if x_array.size == 0:
            x_array = np.arange(
                y_array.size,
                dtype=np.float64
            )

        minimum_size = min(
            x_array.size,
            y_array.size
        )

        if minimum_size <= 0:
            return (
                np.array(
                    [],
                    dtype=np.float64
                ),
                np.array(
                    [],
                    dtype=np.float64
                )
            )

        x_array = x_array[
            :minimum_size
        ]

        y_array = y_array[
            :minimum_size
        ]

        valid_mask = (
                np.isfinite(x_array) &
                np.isfinite(y_array)
        )

        x_array = x_array[
            valid_mask
        ]

        y_array = y_array[
            valid_mask
        ]

        return (
            x_array,
            y_array
        )

    # =====================================================
    # Name and Key
    # =====================================================

    @staticmethod
    def normalize_name(name):
        """
        规范化曲线名称
        """

        if name is None:
            return "Signal"

        name = str(
            name
        ).strip()

        if name == "":
            return "Signal"

        return name

    @staticmethod
    def normalize_key(key):
        """
        规范化曲线唯一标识
        """

        if key is None:
            return ""

        return str(
            key
        ).strip()

    def create_key(
            self,
            name="Signal",
            node_path="",
            shot=None
    ):
        """
        根据节点和 Shot 生成曲线唯一标识
        """

        name = self.normalize_name(
            name
        )

        node_path = str(
            node_path
        ).strip() if node_path is not None else ""

        if node_path:
            base_key = node_path
        else:
            base_key = name

        if shot is not None:
            base_key = "{}::{}".format(
                base_key,
                shot
            )

        key = base_key

        suffix = 2

        while key in self.curves:
            key = "{}#{}".format(
                base_key,
                suffix
            )

            suffix += 1

        return key

    def create_signal_key(
            self,
            signal_data
    ):
        """
        根据 SignalData 生成曲线唯一标识
        """

        if signal_data is None:
            return self.create_key(
                "Signal"
            )

        name = getattr(
            signal_data,
            "name",
            ""
        )

        node_path = getattr(
            signal_data,
            "node",
            ""
        )

        shot = getattr(
            signal_data,
            "shot",
            None
        )

        return self.create_key(
            name=name,
            node_path=node_path,
            shot=shot
        )

    # =====================================================
    # Color
    # =====================================================

    @staticmethod
    def normalize_color(
            color,
            default_color="k"
    ):
        """
        规范化曲线颜色
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

        color_text = str(
            color
        ).strip()

        if color_text == "":
            return default_color

        lower_color = color_text.lower()

        if lower_color in color_map:
            return color_map[
                lower_color
            ]

        try:

            pg.mkColor(
                color_text
            )

            return color_text

        except Exception:

            return default_color

    def next_color(self):
        """
        获取下一种曲线颜色
        """

        if not self.color_cycle:
            return self.foreground_color

        color = self.color_cycle[
            self.color_index %
            len(self.color_cycle)
            ]

        self.color_index += 1

        return color

    def reset_color_cycle(self):
        """
        重置曲线颜色序列
        """

        self.color_index = 0

    # =====================================================
    # Add Curve
    # =====================================================

    def add_curve(
            self,
            x_data,
            y_data,
            name="Signal",
            key=None,
            color=None,
            width=None,
            node_path="",
            shot=None,
            signal_data=None,
            replace=False
    ):
        """
        添加一条叠加曲线

        replace=True：
        如果 key 已存在，则更新原曲线。
        """

        if self.plot_item is None:
            return None

        x_array, y_array = self.prepare_data(
            x_data,
            y_data
        )

        if y_array.size == 0:
            return None

        name = self.normalize_name(
            name
        )

        key = self.normalize_key(
            key
        )

        if key == "":
            key = self.create_key(
                name=name,
                node_path=node_path,
                shot=shot
            )

        if key in self.curves:

            if replace:
                self.update_curve(
                    key=key,
                    x_data=x_array,
                    y_data=y_array,
                    name=name,
                    color=color,
                    width=width,
                    node_path=node_path,
                    shot=shot,
                    signal_data=signal_data
                )

                return self.curves.get(
                    key
                )

            key = self.create_key(
                name=name,
                node_path=node_path,
                shot=shot
            )

        if color is None:
            color = self.next_color()

        color = self.normalize_color(
            color,
            self.foreground_color
        )

        if width is None:
            width = self.default_width

        try:

            width = float(
                width
            )

        except Exception:

            width = self.default_width

        if width <= 0:
            width = self.default_width

        try:

            curve = self.plot_item.plot(
                x_array,
                y_array,
                pen=pg.mkPen(
                    color,
                    width=width
                )
            )

        except Exception:

            return None

        overlay_curve = OverlayCurve(
            key=key,
            name=name,
            curve=curve,
            x_data=x_array,
            y_data=y_array,
            color=color,
            width=width,
            node_path=node_path,
            shot=shot,
            signal_data=signal_data
        )

        self.curves[key] = overlay_curve

        if self.legend_manager is not None:
            self.legend_manager.add_curve(
                curve,
                self.build_legend_name(
                    overlay_curve
                )
            )

        self.curveAdded.emit(
            key
        )

        self.dataChanged.emit()

        return overlay_curve

    def add_signal(
            self,
            signal_data,
            key=None,
            color=None,
            width=None,
            replace=False
    ):
        """
        添加 SignalData 曲线
        """

        if signal_data is None:
            return None

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

        node_path = getattr(
            signal_data,
            "node",
            ""
        )

        shot = getattr(
            signal_data,
            "shot",
            None
        )

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

        if key is None:
            key = self.create_signal_key(
                signal_data
            )

        return self.add_curve(
            x_data=x_data,
            y_data=y_data,
            name=name,
            key=key,
            color=color,
            width=width,
            node_path=node_path,
            shot=shot,
            signal_data=signal_data,
            replace=replace
        )

    # =====================================================
    # Update Curve
    # =====================================================

    def update_curve(
            self,
            key,
            x_data=None,
            y_data=None,
            name=None,
            color=None,
            width=None,
            node_path=None,
            shot=None,
            signal_data=None
    ):
        """
        更新指定曲线
        """

        key = self.normalize_key(
            key
        )

        if key not in self.curves:
            return False

        overlay_curve = self.curves[
            key
        ]

        update_data = (
                x_data is not None
                or
                y_data is not None
        )

        if update_data:

            if x_data is None:
                x_data = overlay_curve.x_data

            if y_data is None:
                y_data = overlay_curve.y_data

            x_array, y_array = self.prepare_data(
                x_data,
                y_data
            )

            if y_array.size == 0:
                return False

            overlay_curve.x_data = x_array
            overlay_curve.y_data = y_array

            overlay_curve.curve.setData(
                x_array,
                y_array
            )

        if name is not None:
            overlay_curve.name = (
                self.normalize_name(
                    name
                )
            )

        if node_path is not None:
            overlay_curve.node_path = str(
                node_path
            ).strip()

        if shot is not None:
            overlay_curve.shot = shot

        if signal_data is not None:
            overlay_curve.signal_data = (
                signal_data
            )

        if color is not None:
            overlay_curve.color = (
                self.normalize_color(
                    color,
                    overlay_curve.color
                )
            )

        if width is not None:

            try:

                width = float(
                    width
                )

            except Exception:

                width = overlay_curve.width

            if width > 0:
                overlay_curve.width = width

        overlay_curve.curve.setPen(
            pg.mkPen(
                overlay_curve.color,
                width=overlay_curve.width
            )
        )

        if self.legend_manager is not None:
            self.legend_manager.update_name(
                overlay_curve.curve,
                self.build_legend_name(
                    overlay_curve
                )
            )

        self.curveUpdated.emit(
            key
        )

        self.dataChanged.emit()

        return True

    def update_signal(
            self,
            key,
            signal_data
    ):
        """
        使用新的 SignalData 更新曲线
        """

        if signal_data is None:
            return False

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

        return self.update_curve(
            key=key,
            x_data=getattr(
                signal_data,
                "x",
                None
            ),
            y_data=getattr(
                signal_data,
                "y",
                None
            ),
            name=name,
            node_path=getattr(
                signal_data,
                "node",
                ""
            ),
            shot=getattr(
                signal_data,
                "shot",
                None
            ),
            signal_data=signal_data
        )

    # =====================================================
    # Remove Curve
    # =====================================================

    def remove_curve(self, key):
        """
        删除指定曲线
        """

        key = self.normalize_key(
            key
        )

        if key not in self.curves:
            return False

        overlay_curve = self.curves[
            key
        ]

        if self.legend_manager is not None:
            self.legend_manager.remove_curve(
                overlay_curve.curve
            )

        if self.plot_item is not None:

            try:

                self.plot_item.removeItem(
                    overlay_curve.curve
                )

            except Exception:

                pass

        del self.curves[key]

        self.curveRemoved.emit(
            key
        )

        self.dataChanged.emit()

        return True

    def remove_curve_object(self, curve):
        """
        根据 PyQtGraph 曲线对象删除
        """

        target_key = None

        for key, overlay_curve in self.curves.items():

            if overlay_curve.curve is curve:
                target_key = key

                break

        if target_key is None:
            return False

        return self.remove_curve(
            target_key
        )

    # =====================================================
    # Clear
    # =====================================================

    def clear(self):
        """
        清空全部叠加曲线
        """

        keys = list(
            self.curves.keys()
        )

        for key in keys:
            self.remove_curve(
                key
            )

        self.curves.clear()

        self.reset_color_cycle()

        self.overlayCleared.emit()

        self.dataChanged.emit()

    def clear_compare(self):
        """
        清空多炮号对比曲线。
        """

        self.clear()

        return True

    # =====================================================
    # Compare Shot
    # =====================================================

    def contains_shot(
            self,
            shot
    ):
        """
        判断是否包含指定炮号的曲线。
        """

        target_shot = int(shot)

        for overlay_curve in self.curves.values():

            if int(overlay_curve.shot) == target_shot:
                return True

        return False

    def remove_shot(
            self,
            shot
    ):
        """
        删除指定炮号对应的全部曲线。
        """
        target_shot = int(shot)

        keys = []

        for key, overlay_curve in self.curves.items():

            if int(overlay_curve.shot) == target_shot:
                keys.append(
                    key
                )

        if not keys:
            return False

        for key in keys:
            self.remove_curve(
                key
            )

        return True

    # =====================================================
    # Visibility
    # =====================================================

    def set_curve_visible(
            self,
            key,
            visible
    ):
        """
        设置指定曲线显示状态
        """

        key = self.normalize_key(
            key
        )

        if key not in self.curves:
            return False

        overlay_curve = self.curves[
            key
        ]

        overlay_curve.visible = bool(
            visible
        )

        overlay_curve.curve.setVisible(
            overlay_curve.visible
        )

        self.curveVisibilityChanged.emit(
            key,
            overlay_curve.visible
        )

        return True

    def show_curve(self, key):
        """
        显示指定曲线
        """

        return self.set_curve_visible(
            key,
            True
        )

    def hide_curve(self, key):
        """
        隐藏指定曲线
        """

        return self.set_curve_visible(
            key,
            False
        )

    def toggle_curve(self, key):
        """
        切换指定曲线显示状态
        """

        overlay_curve = self.get_curve(
            key
        )

        if overlay_curve is None:
            return False

        return self.set_curve_visible(
            key,
            not overlay_curve.visible
        )

    def show_all(self):
        """
        显示全部曲线
        """

        for key in self.curves:
            self.set_curve_visible(
                key,
                True
            )

    def hide_all(self):
        """
        隐藏全部曲线
        """

        for key in self.curves:
            self.set_curve_visible(
                key,
                False
            )

    # =====================================================
    # Curve Style
    # =====================================================

    def set_curve_color(
            self,
            key,
            color
    ):
        """
        修改指定曲线颜色
        """

        overlay_curve = self.get_curve(
            key
        )

        if overlay_curve is None:
            return False

        color = self.normalize_color(
            color,
            overlay_curve.color
        )

        overlay_curve.color = color

        overlay_curve.curve.setPen(
            pg.mkPen(
                overlay_curve.color,
                width=overlay_curve.width
            )
        )

        self.curveUpdated.emit(
            overlay_curve.key
        )

        return True

    def set_curve_width(
            self,
            key,
            width
    ):
        """
        修改指定曲线宽度
        """

        overlay_curve = self.get_curve(
            key
        )

        if overlay_curve is None:
            return False

        try:

            width = float(
                width
            )

        except Exception:

            return False

        if width <= 0:
            return False

        overlay_curve.width = width

        overlay_curve.curve.setPen(
            pg.mkPen(
                overlay_curve.color,
                width=overlay_curve.width
            )
        )

        self.curveUpdated.emit(
            overlay_curve.key
        )

        return True

    # =====================================================
    # Legend
    # =====================================================

    @staticmethod
    def build_legend_name(
            overlay_curve
    ):
        """
        生成图例显示名称
        """

        name = overlay_curve.name

        if overlay_curve.shot is not None:
            name = "{}  [Shot {}]".format(
                name,
                overlay_curve.shot
            )

        return name

    def set_legend_manager(
            self,
            legend_manager
    ):
        """
        设置图例管理器
        """

        self.legend_manager = (
            legend_manager
        )

        if self.legend_manager is None:
            return

        for overlay_curve in self.curves.values():
            self.legend_manager.add_curve(
                overlay_curve.curve,
                self.build_legend_name(
                    overlay_curve
                )
            )

    # =====================================================
    # Auto Range
    # =====================================================

    def auto_range(self):
        """
        自动调整全部曲线显示范围
        """

        if self.plot_widget is None:
            return

        if not self.curves:
            return

        try:

            self.plot_widget.enableAutoRange(
                axis="xy",
                enable=True
            )

            self.plot_widget.autoRange(
                padding=0.05
            )

        except Exception:

            try:

                self.plot_item.enableAutoRange(
                    x=True,
                    y=True
                )

            except Exception:

                pass

    # =====================================================
    # Query
    # =====================================================

    def get_curve(self, key):
        """
        获取指定曲线数据对象
        """

        key = self.normalize_key(
            key
        )

        return self.curves.get(
            key
        )

    def get_curve_by_name(self, name):
        """
        根据曲线名称查找
        """

        name = self.normalize_name(
            name
        )

        for overlay_curve in self.curves.values():

            if overlay_curve.name == name:
                return overlay_curve

        return None

    def get_curve_by_shot(self, shot):
        """
        根据 Shot 查找第一条匹配曲线
        """

        for overlay_curve in self.curves.values():

            if overlay_curve.shot == shot:
                return overlay_curve

        return None

    def contains(self, key):
        """
        判断是否包含指定曲线
        """

        key = self.normalize_key(
            key
        )

        return key in self.curves

    def count(self):
        """
        返回曲线数量
        """

        return len(
            self.curves
        )

    def keys(self):
        """
        返回全部曲线标识
        """

        return list(
            self.curves.keys()
        )

    def values(self):
        """
        返回全部 OverlayCurve
        """

        return list(
            self.curves.values()
        )

    def names(self):
        """
        返回全部曲线名称
        """

        return [
            overlay_curve.name
            for overlay_curve
            in self.curves.values()
        ]

    def total_point_count(self):
        """
        返回全部曲线采样点总数
        """

        total = 0

        for overlay_curve in self.curves.values():
            total += (
                overlay_curve.point_count()
            )

        return total

    def visible_curve_count(self):
        """
        返回当前显示的曲线数量
        """

        count = 0

        for overlay_curve in self.curves.values():

            if overlay_curve.visible:
                count += 1

        return count

    def is_empty(self):
        """
        判断是否没有曲线
        """

        return len(
            self.curves
        ) == 0

    # =====================================================
    # Data Interface
    # =====================================================

    def get_data(self, key):
        """
        获取指定曲线的 X、Y 数据副本
        """

        overlay_curve = self.get_curve(
            key
        )

        if overlay_curve is None:
            return (
                np.array(
                    [],
                    dtype=np.float64
                ),
                np.array(
                    [],
                    dtype=np.float64
                )
            )

        return (
            overlay_curve.x_data.copy(),
            overlay_curve.y_data.copy()
        )

    def get_all_data(self):
        """
        获取全部曲线数据

        返回：
        {
            key: {
                "name": ...,
                "node": ...,
                "shot": ...,
                "x": ...,
                "y": ...
            }
        }
        """

        result = {}

        for key, overlay_curve in self.curves.items():
            result[key] = {
                "name": overlay_curve.name,
                "node": overlay_curve.node_path,
                "shot": overlay_curve.shot,
                "x": overlay_curve.x_data.copy(),
                "y": overlay_curve.y_data.copy(),
                "visible": overlay_curve.visible,
                "color": overlay_curve.color,
                "width": overlay_curve.width
            }

        return result

    # =====================================================
    # Remove
    # =====================================================

    def remove(self):
        """
        清空曲线并释放引用
        """

        self.clear()

        self.legend_manager = None
        self.plot_item = None
        self.plot_widget = None
