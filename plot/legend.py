# -*- coding: utf-8 -*-

"""
==========================================================
Project : NNBI_database
File    : legend.py
Author  :
Date    :
Description : Waveform Legend Manager
==========================================================
"""

import pyqtgraph as pg

from PySide2.QtCore import (
    QObject,
    Signal
)


class WaveformLegend(QObject):
    """
    波形图例管理器

    功能：
    1. 创建和管理 PyQtGraph 图例
    2. 添加曲线图例
    3. 删除曲线图例
    4. 更新图例名称
    5. 显示和隐藏图例
    6. 清空全部图例
    7. 根据白色背景应用黑色文字
    """

    visibilityChanged = Signal(bool)

    def __init__(
            self,
            plot_widget,
            parent=None
    ):

        super(WaveformLegend, self).__init__(
            parent
        )

        self.plot_widget = plot_widget

        self.plot_item = None

        self.legend = None

        # 曲线对象与名称的对应关系
        self.items = {}

        # =================================================
        # Style
        # =================================================

        self.background_color = "w"
        self.foreground_color = "k"
        self.border_color = "808080"

        self.visible = True

        self.offset = (
            -10,
            10
        )

        self.init_legend()

    # =====================================================
    # Initialize
    # =====================================================

    def init_legend(self):
        """
        初始化图例
        """

        if self.plot_widget is None:
            return

        self.plot_item = (
            self.plot_widget.getPlotItem()
        )

        if self.plot_item is None:
            return

        # 如果 PlotItem 中已经存在图例，先移除
        old_legend = getattr(
            self.plot_item,
            "legend",
            None
        )

        if old_legend is not None:

            try:

                old_legend.setParentItem(
                    None
                )

            except Exception:

                pass

            self.plot_item.legend = None

        self.legend = pg.LegendItem(
            offset=self.offset
        )

        self.legend.setParentItem(
            self.plot_item.graphicsItem()
        )

        self.plot_item.legend = self.legend

        self.apply_style()

        self.set_visible(
            self.visible
        )

    # =====================================================
    # Style
    # =====================================================

    def apply_style(self):
        """
        应用图例样式

        默认：
        background = k
        foreground = w
        """

        if self.legend is None:
            return

        try:

            self.legend.setBrush(
                pg.mkBrush(
                    255,
                    255,
                    255,
                    220
                )
            )

        except Exception:

            pass

        try:

            self.legend.setPen(
                pg.mkPen(
                    self.border_color,
                    width=1
                )
            )

        except Exception:

            pass

        self.update_label_colors()

    def update_label_colors(self):
        """
        更新所有图例文字颜色
        """

        if self.legend is None:
            return

        for sample, label in self.legend.items:

            if label is None:
                continue

            try:

                label.setText(
                    label.text,
                    color=self.foreground_color
                )

            except Exception:

                try:

                    label.item.setDefaultTextColor(
                        pg.mkColor(
                            self.foreground_color
                        )
                    )

                except Exception:

                    pass

    def set_style(
            self,
            background_color="w",
            foreground_color="k",
            border_color="808080"
    ):
        """
        设置图例颜色
        """

        self.background_color = (
            self.normalize_color(
                background_color,
                "w"
            )
        )

        self.foreground_color = (
            self.normalize_color(
                foreground_color,
                "k"
            )
        )

        self.border_color = (
            self.normalize_color(
                border_color,
                "808080"
            )
        )

        if self.legend is None:
            return

        try:

            if self.background_color == "k":

                self.legend.setBrush(
                    pg.mkBrush(
                        0,
                        0,
                        0,
                        190
                    )
                )

            else:

                self.legend.setBrush(
                    pg.mkBrush(
                        self.background_color
                    )
                )

        except Exception:

            self.legend.setBrush(
                pg.mkBrush(
                    0,
                    0,
                    0,
                    190
                )
            )

        try:

            self.legend.setPen(
                pg.mkPen(
                    self.border_color,
                    width=1
                )
            )

        except Exception:

            self.legend.setPen(
                pg.mkPen(
                    "808080",
                    width=1
                )
            )

        self.update_label_colors()

    @staticmethod
    def normalize_color(
            color,
            default_color
    ):
        """
        颜色名称转换
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

        lower_color = (
            color_text.lower()
        )

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

    # =====================================================
    # Add
    # =====================================================

    def add_curve(
            self,
            curve,
            name
    ):
        """
        添加曲线图例
        """

        if self.legend is None:
            return False

        if curve is None:
            return False

        name = self.normalize_name(
            name
        )

        # 曲线已经存在时，只更新名称
        if curve in self.items:
            self.update_name(
                curve,
                name
            )

            return True

        try:

            self.legend.addItem(
                curve,
                name
            )

            self.items[curve] = name

            self.update_label_colors()

            return True

        except Exception:

            return False

    def add_signal_curve(
            self,
            curve,
            signal_data
    ):
        """
        根据 SignalData 添加图例
        """

        if signal_data is None:
            return self.add_curve(
                curve,
                "Signal"
            )

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

        shot = getattr(
            signal_data,
            "shot",
            None
        )

        if shot is not None:
            name = "{}  [Shot {}]".format(
                name,
                shot
            )

        return self.add_curve(
            curve,
            name
        )

    # =====================================================
    # Remove
    # =====================================================

    def remove_curve(self, curve):
        """
        删除指定曲线图例
        """

        if self.legend is None:
            return False

        if curve is None:
            return False

        if curve not in self.items:
            return False

        try:

            self.legend.removeItem(
                curve
            )

        except Exception:

            # pyqtgraph 0.11.1 中部分情况下
            # removeItem 需要传入曲线名称
            try:

                self.legend.removeItem(
                    self.items[curve]
                )

            except Exception:

                return False

        del self.items[curve]

        return True

    def remove_by_name(self, name):
        """
        根据图例名称删除
        """

        name = self.normalize_name(
            name
        )

        target_curve = None

        for curve, curve_name in self.items.items():

            if curve_name == name:
                target_curve = curve

                break

        if target_curve is None:
            return False

        return self.remove_curve(
            target_curve
        )

    # =====================================================
    # Update
    # =====================================================

    def update_name(
            self,
            curve,
            name
    ):
        """
        更新指定曲线的图例名称
        """

        if curve is None:
            return False

        name = self.normalize_name(
            name
        )

        if curve not in self.items:
            return self.add_curve(
                curve,
                name
            )

        old_name = self.items[
            curve
        ]

        if old_name == name:
            return True

        # PyQtGraph 0.11.1 没有稳定的图例重命名接口，
        # 因此通过删除并重新添加实现
        try:

            self.legend.removeItem(
                curve
            )

        except Exception:

            try:

                self.legend.removeItem(
                    old_name
                )

            except Exception:

                pass

        try:

            self.legend.addItem(
                curve,
                name
            )

            self.items[curve] = name

            self.update_label_colors()

            return True

        except Exception:

            return False

    def update_signal_name(
            self,
            curve,
            signal_data
    ):
        """
        根据 SignalData 更新曲线名称
        """

        if signal_data is None:
            return self.update_name(
                curve,
                "Signal"
            )

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

        shot = getattr(
            signal_data,
            "shot",
            None
        )

        if shot is not None:
            name = "{}  [Shot {}]".format(
                name,
                shot
            )

        return self.update_name(
            curve,
            name
        )

    # =====================================================
    # Visibility
    # =====================================================

    def set_visible(self, visible):
        """
        显示或隐藏图例
        """

        self.visible = bool(
            visible
        )

        if self.legend is None:
            return

        self.legend.setVisible(
            self.visible
        )

        self.visibilityChanged.emit(
            self.visible
        )

    def show(self):
        """
        显示图例
        """

        self.set_visible(
            True
        )

    def hide(self):
        """
        隐藏图例
        """

        self.set_visible(
            False
        )

    def toggle(self):
        """
        切换图例显示状态
        """

        self.set_visible(
            not self.visible
        )

    def is_visible(self):
        """
        返回图例显示状态
        """

        return self.visible

    # =====================================================
    # Position
    # =====================================================

    def set_offset(
            self,
            x_offset=-10,
            y_offset=10
    ):
        """
        设置图例在绘图区中的位置
        """

        self.offset = (
            x_offset,
            y_offset
        )

        if self.legend is None:
            return

        try:

            self.legend.anchor(
                itemPos=(1, 0),
                parentPos=(1, 0),
                offset=self.offset
            )

        except Exception:

            pass

    def set_top_left(self):
        """
        图例放置在左上角
        """

        if self.legend is None:
            return

        try:

            self.legend.anchor(
                itemPos=(0, 0),
                parentPos=(0, 0),
                offset=(10, 10)
            )

        except Exception:

            pass

    def set_top_right(self):
        """
        图例放置在右上角
        """

        if self.legend is None:
            return

        try:

            self.legend.anchor(
                itemPos=(1, 0),
                parentPos=(1, 0),
                offset=(-10, 10)
            )

        except Exception:

            pass

    def set_bottom_left(self):
        """
        图例放置在左下角
        """

        if self.legend is None:
            return

        try:

            self.legend.anchor(
                itemPos=(0, 1),
                parentPos=(0, 1),
                offset=(10, -10)
            )

        except Exception:

            pass

    def set_bottom_right(self):
        """
        图例放置在右下角
        """

        if self.legend is None:
            return

        try:

            self.legend.anchor(
                itemPos=(1, 1),
                parentPos=(1, 1),
                offset=(-10, -10)
            )

        except Exception:

            pass

    # =====================================================
    # Clear
    # =====================================================

    def clear(self):
        """
        清空全部图例项目
        """

        if self.legend is None:
            self.items.clear()

            return

        curves = list(
            self.items.keys()
        )

        for curve in curves:
            self.remove_curve(
                curve
            )

        self.items.clear()

    # =====================================================
    # Query
    # =====================================================

    def contains(self, curve):
        """
        判断曲线是否已经在图例中
        """

        return curve in self.items

    def get_name(self, curve):
        """
        获取曲线对应名称
        """

        return self.items.get(
            curve,
            ""
        )

    def count(self):
        """
        返回图例项目数量
        """

        return len(
            self.items
        )

    def curves(self):
        """
        返回全部曲线对象
        """

        return list(
            self.items.keys()
        )

    def names(self):
        """
        返回全部图例名称
        """

        return list(
            self.items.values()
        )

    @staticmethod
    def normalize_name(name):
        """
        规范化图例名称
        """

        if name is None:
            return "Signal"

        name = str(
            name
        ).strip()

        if name == "":
            return "Signal"

        return name

    # =====================================================
    # Remove Legend
    # =====================================================

    def remove(self):
        """
        从 PlotItem 中彻底移除图例
        """

        self.clear()

        if self.legend is not None:

            try:

                self.legend.setParentItem(
                    None
                )

            except Exception:

                pass

        if self.plot_item is not None:

            try:

                self.plot_item.legend = None

            except Exception:

                pass

        self.legend = None
        self.plot_item = None

        self.items.clear()
