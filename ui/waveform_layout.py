# -*- coding: utf-8 -*-

"""
==========================================================
Project : NNBI_database
File    : waveform_layout.py
Author  :
Date    :
Description : Dynamic Waveform Panel Layout
==========================================================
"""

import math

from PySide2.QtCore import (
    Qt,
    QObject,
    QEvent,
    Signal,
)

from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
)

from ui.waveform_panel import WaveformPanel


class PanelMouseFilter(QObject):
    """
    捕获WaveformPanel及其子控件的鼠标点击。

    点击面板中的标题、按钮、绘图区或状态栏时，
    都会将对应WaveformPanel设置为当前活动面板。
    """

    panelClicked = Signal(object)

    def __init__(
            self,
            panel,
            parent=None
    ):
        super(PanelMouseFilter, self).__init__(
            parent
        )

        self.panel = panel

    def eventFilter(
            self,
            watched,
            event
    ):
        if event.type() == QEvent.MouseButtonPress:
            self.panelClicked.emit(
                self.panel
            )

        return False


class WaveformLayout(QWidget):
    """
    动态波形面板布局。

    功能：
    1. 动态增加和删除WaveformPanel；
    2. 支持纵向、横向和自定义行列布局；
    3. 使用嵌套QSplitter调整面板宽度和高度；
    4. 保留布局切换前已经加载的波形数据；
    5. 管理当前活动WaveformPanel；
    6. 支持所有面板恢复平均大小。

    布局说明：
    - vertical：所有面板纵向排列；
    - horizontal：所有面板横向排列；
    - grid：按照rows × columns排列；
    - auto：根据面板数量自动计算接近方形的布局。
    """

    panelAdded = Signal(object)
    panelRemoved = Signal(object)

    activePanelChanged = Signal(object)

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

        super(WaveformLayout, self).__init__(
            parent
        )

        self.config = config

        self.panels = []
        self.active_panel = None

        self.layout_mode = "vertical"
        self.layout_rows = 1
        self.layout_columns = 1

        self.root_splitter = None

        self._mouse_filters = {}

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

    # =====================================================
    # Panel Management
    # =====================================================

    def add_panel(
            self,
            panel=None,
            make_active=True
    ):
        """
        增加一个WaveformPanel。

        Parameters
        ----------
        panel : WaveformPanel or None
            为None时自动创建新面板。
        make_active : bool
            是否将新增面板设为当前活动面板。
        """

        if panel is None:
            panel = WaveformPanel(
                self.config,
                self
            )

        if panel in self.panels:
            return panel

        self.panels.append(
            panel
        )

        self.install_panel_mouse_filter(
            panel
        )

        self.rebuild_layout()

        if make_active:
            self.set_active_panel(
                panel
            )

        self.panelAdded.emit(
            panel
        )

        return panel

    def remove_panel(
            self,
            panel=None,
            delete_widget=True
    ):
        """
        删除指定面板。

        panel为None时删除当前活动面板。
        """

        if panel is None:
            panel = self.active_panel

        if panel is None:
            return False

        if panel not in self.panels:
            return False

        index = self.panels.index(
            panel
        )

        self.uninstall_panel_mouse_filter(
            panel
        )

        self.panels.remove(
            panel
        )

        if self.active_panel is panel:
            self.active_panel = None

        panel.setParent(
            None
        )

        self.rebuild_layout()

        if self.panels:

            next_index = min(
                index,
                len(self.panels) - 1
            )

            self.set_active_panel(
                self.panels[next_index]
            )

        else:

            self.activePanelChanged.emit(
                None
            )

        self.panelRemoved.emit(
            panel
        )

        if delete_widget:
            panel.deleteLater()

        return True

    def clear_panels(
            self,
            delete_widgets=True
    ):
        """
        删除全部面板。
        """

        old_panels = list(
            self.panels
        )

        self.panels = []
        self.active_panel = None

        for panel in old_panels:

            self.uninstall_panel_mouse_filter(
                panel
            )

            panel.setParent(
                None
            )

            self.panelRemoved.emit(
                panel
            )

            if delete_widgets:
                panel.deleteLater()

        self.rebuild_layout()

        self.activePanelChanged.emit(
            None
        )

    def panel_count(self):

        return len(
            self.panels
        )

    def panel_at(
            self,
            index
    ):

        try:
            return self.panels[
                int(index)
            ]
        except (
                IndexError,
                TypeError,
                ValueError
        ):
            return None

    def index_of(
            self,
            panel
    ):

        try:
            return self.panels.index(
                panel
            )
        except ValueError:
            return -1

    def current_panel(self):

        return self.active_panel

    def set_active_panel(
            self,
            panel
    ):
        """
        设置当前活动面板。
        """

        if panel is not None:
            if panel not in self.panels:
                return False

        if self.active_panel is panel:
            self.update_panel_selection_style()

            return True

        self.active_panel = panel

        self.update_panel_selection_style()

        self.activePanelChanged.emit(
            panel
        )

        return True

    def next_panel(self):

        if not self.panels:
            return None

        index = self.index_of(
            self.active_panel
        )

        if index < 0:
            index = 0
        else:
            index = (
                            index + 1
                    ) % len(self.panels)

        panel = self.panels[
            index
        ]

        self.set_active_panel(
            panel
        )

        return panel

    def previous_panel(self):

        if not self.panels:
            return None

        index = self.index_of(
            self.active_panel
        )

        if index < 0:
            index = 0
        else:
            index = (
                            index - 1
                    ) % len(self.panels)

        panel = self.panels[
            index
        ]

        self.set_active_panel(
            panel
        )

        return panel

    # =====================================================
    # Mouse Selection
    # =====================================================

    def install_panel_mouse_filter(
            self,
            panel
    ):
        """
        为面板及其全部子控件安装点击过滤器。
        """

        if panel in self._mouse_filters:
            return

        event_filter = PanelMouseFilter(
            panel,
            self
        )

        event_filter.panelClicked.connect(
            self.set_active_panel
        )

        self._mouse_filters[
            panel
        ] = event_filter

        self.install_filter_recursively(
            panel,
            event_filter
        )

    def uninstall_panel_mouse_filter(
            self,
            panel
    ):

        event_filter = self._mouse_filters.pop(
            panel,
            None
        )

        if event_filter is None:
            return

        self.remove_filter_recursively(
            panel,
            event_filter
        )

        event_filter.deleteLater()

    @staticmethod
    def install_filter_recursively(
            widget,
            event_filter
    ):

        widget.installEventFilter(
            event_filter
        )

        for child in widget.findChildren(
                QWidget
        ):
            child.installEventFilter(
                event_filter
            )

    @staticmethod
    def remove_filter_recursively(
            widget,
            event_filter
    ):

        widget.removeEventFilter(
            event_filter
        )

        for child in widget.findChildren(
                QWidget
        ):
            child.removeEventFilter(
                event_filter
            )

    def refresh_panel_mouse_filter(
            self,
            panel
    ):
        """
        面板运行过程中新增子控件后，可调用该方法重新安装过滤器。
        """

        event_filter = self._mouse_filters.get(
            panel
        )

        if event_filter is None:
            return

        self.install_filter_recursively(
            panel,
            event_filter
        )

    # =====================================================
    # Layout Mode
    # =====================================================

    def set_vertical_layout(self):

        return self.set_layout(
            "vertical"
        )

    def set_horizontal_layout(self):

        return self.set_layout(
            "horizontal"
        )

    def set_grid_layout(
            self,
            rows,
            columns
    ):

        return self.set_layout(
            "grid",
            rows,
            columns
        )

    def set_auto_layout(self):

        return self.set_layout(
            "auto"
        )

    def set_layout(
            self,
            mode,
            rows=None,
            columns=None
    ):
        """
        设置布局方式。

        Parameters
        ----------
        mode : str
            vertical、horizontal、grid或auto。
        rows : int or None
            grid模式行数。
        columns : int or None
            grid模式列数。
        """

        mode = str(
            mode
        ).strip().lower()

        if mode not in (
                "vertical",
                "horizontal",
                "grid",
                "auto"
        ):
            raise ValueError(
                "Unsupported waveform layout mode: {}".format(
                    mode
                )
            )

        if mode == "vertical":

            rows = max(
                1,
                self.panel_count()
            )

            columns = 1

        elif mode == "horizontal":

            rows = 1

            columns = max(
                1,
                self.panel_count()
            )

        elif mode == "auto":

            rows, columns = self.calculate_auto_grid(
                self.panel_count()
            )

        else:

            rows = self.normalize_layout_size(
                rows
            )

            columns = self.normalize_layout_size(
                columns
            )

        self.layout_mode = mode
        self.layout_rows = rows
        self.layout_columns = columns

        self.rebuild_layout()

        self.layoutChanged.emit(
            self.layout_mode,
            self.layout_rows,
            self.layout_columns
        )

        return True

    @staticmethod
    def normalize_layout_size(
            value
    ):

        try:
            value = int(
                value
            )
        except (
                TypeError,
                ValueError
        ):
            value = 1

        return max(
            1,
            value
        )

    @staticmethod
    def calculate_auto_grid(
            panel_count
    ):
        """
        根据面板数量计算接近方形的行列数。
        """

        try:
            panel_count = int(
                panel_count
            )
        except (
                TypeError,
                ValueError
        ):
            panel_count = 0

        if panel_count <= 1:
            return 1, 1

        columns = int(
            math.ceil(
                math.sqrt(
                    panel_count
                )
            )
        )

        rows = int(
            math.ceil(
                float(panel_count)
                /
                float(columns)
            )
        )

        return rows, columns

    def resolved_layout_size(self):
        """
        返回当前面板数量下实际使用的行列数。
        """

        count = self.panel_count()

        if self.layout_mode == "vertical":
            return max(1, count), 1

        if self.layout_mode == "horizontal":
            return 1, max(1, count)

        if self.layout_mode == "auto":
            return self.calculate_auto_grid(
                count
            )

        rows = max(
            1,
            int(self.layout_rows)
        )

        columns = max(
            1,
            int(self.layout_columns)
        )

        if count > rows * columns:
            rows = int(
                math.ceil(
                    float(count)
                    /
                    float(columns)
                )
            )

        return rows, columns

    # =====================================================
    # Layout Build
    # =====================================================

    def rebuild_layout(self):
        """
        根据当前布局模式重新组织所有面板。

        重新布局只改变控件父子关系，不会销毁WaveformPanel，
        因此已经加载的数据、Overlay和显示状态都会保留。
        """

        self.detach_panels()

        self.delete_root_splitter()

        if not self.panels:
            return

        rows, columns = self.resolved_layout_size()

        if rows == 1:

            self.root_splitter = self.build_single_row(
                self.panels
            )

        elif columns == 1:

            self.root_splitter = self.build_single_column(
                self.panels
            )

        else:

            self.root_splitter = self.build_grid(
                rows,
                columns
            )

        self.main_layout.addWidget(
            self.root_splitter
        )

        self.equalize_sizes()

        if self.active_panel not in self.panels:
            self.active_panel = self.panels[0]

        self.update_panel_selection_style()

    def detach_panels(self):

        for panel in self.panels:
            panel.setParent(
                None
            )

    def delete_root_splitter(self):

        if self.root_splitter is None:
            return

        self.main_layout.removeWidget(
            self.root_splitter
        )

        self.root_splitter.setParent(
            None
        )

        self.root_splitter.deleteLater()

        self.root_splitter = None

    def build_single_row(
            self,
            panels
    ):

        splitter = self.create_splitter(
            Qt.Horizontal
        )

        for panel in panels:
            splitter.addWidget(
                panel
            )

        return splitter

    def build_single_column(
            self,
            panels
    ):

        splitter = self.create_splitter(
            Qt.Vertical
        )

        for panel in panels:
            splitter.addWidget(
                panel
            )

        return splitter

    def build_grid(
            self,
            rows,
            columns
    ):
        """
        生成嵌套QSplitter网格。

        外层为垂直Splitter，每一行为水平Splitter。
        """

        root = self.create_splitter(
            Qt.Vertical
        )

        panel_index = 0

        for row_index in range(
                rows
        ):

            if panel_index >= len(self.panels):
                break

            row_splitter = self.create_splitter(
                Qt.Horizontal
            )

            for column_index in range(
                    columns
            ):

                if panel_index >= len(self.panels):
                    break

                panel = self.panels[
                    panel_index
                ]

                row_splitter.addWidget(
                    panel
                )

                panel_index += 1

            root.addWidget(
                row_splitter
            )

        return root

    def create_splitter(
            self,
            orientation
    ):

        splitter = QSplitter(
            orientation,
            self
        )

        splitter.setChildrenCollapsible(
            False
        )

        splitter.setHandleWidth(
            5
        )

        return splitter

    # =====================================================
    # Size Control
    # =====================================================

    def equalize_sizes(self):
        """
        将所有Splitter中的子区域恢复为平均大小。
        """

        if self.root_splitter is None:
            return False

        self.equalize_splitter_recursively(
            self.root_splitter
        )

        return True

    def equalize_splitter_recursively(
            self,
            splitter
    ):

        count = splitter.count()

        if count <= 0:
            return

        splitter.setSizes(
            [1] * count
        )

        for index in range(
                count
        ):

            child = splitter.widget(
                index
            )

            if isinstance(
                    child,
                    QSplitter
            ):
                self.equalize_splitter_recursively(
                    child
                )

    # =====================================================
    # Selection Style
    # =====================================================

    def update_panel_selection_style(self):
        """
        使用边框区分当前活动面板。
        """

        for panel in self.panels:

            if panel is self.active_panel:

                panel.setStyleSheet(
                    "WaveformPanel {"
                    "border: 2px solid #3daee9;"
                    "}"
                )

            else:

                panel.setStyleSheet(
                    ""
                )

    # =====================================================
    # Query
    # =====================================================

    def panels_with_data(self):

        result = []

        for panel in self.panels:

            try:

                has_data = panel.has_data()

            except Exception:

                has_data = False

            if has_data:
                result.append(
                    panel
                )

        return result

    def empty_panels(self):

        result = []

        for panel in self.panels:

            try:

                has_data = panel.has_data()

            except Exception:

                has_data = False

            if not has_data:
                result.append(
                    panel
                )

        return result

    def first_empty_panel(self):

        panels = self.empty_panels()

        if not panels:
            return None

        return panels[0]

    # =====================================================
    # Configuration
    # =====================================================

    def apply_config(self):
        """
        将配置应用到全部WaveformPanel。
        """

        for panel in self.panels:

            try:

                panel.apply_config()

            except Exception:

                pass

    # =====================================================
    # Close
    # =====================================================

    def closeEvent(
            self,
            event
    ):

        for panel in list(
                self.panels
        ):

            try:
                panel.close()
            except Exception:
                pass

        super(WaveformLayout, self).closeEvent(
            event
        )
