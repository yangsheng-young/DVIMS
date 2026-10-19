# -*- coding: utf-8 -*-

"""
==========================================================
Project : NNBI_database
File    : waveform_area.py
Author  :
Date    :
Description : Multi-Tab and Multi-Panel Waveform Area
==========================================================
"""

from PySide2.QtCore import (
    Qt,
    Signal,
)

from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
)

from ui.waveform_tab import WaveformTab


class WaveformArea(QWidget):
    """
    多Tab、多Panel波形区域。

    设计规则：
    1. WaveformArea管理多个WaveformTab；
    2. 每个WaveformTab管理多个WaveformPanel；
    3. config.new_tab=True时，同一炮号的不同节点进入同一个Tab；
    4. 不同炮号默认进入不同Tab；
    5. config.new_tab=False时，所有普通节点进入当前Tab；
    6. 相同炮号、相同节点已存在时，更新并激活原Panel；
    7. Compare仍使用独立Tab，并显示在当前活动Panel；
    8. Overlay、导出和刷新默认作用于当前活动Panel。
    """

    currentTabChanged = Signal(object)
    currentPanelChanged = Signal(object)

    tabAdded = Signal(object)
    tabClosed = Signal(int)

    panelAdded = Signal(object)
    panelRemoved = Signal(object)

    def __init__(
            self,
            config,
            parent=None
    ):

        super(WaveformArea, self).__init__(
            parent
        )

        self.config = config

        self.main_layout = None
        self.tab_widget = None

        self.init_ui()
        self.create_connections()
        self.create_default_tab()

    # =====================================================
    # UI
    # =====================================================

    def init_ui(self):

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

        self.tab_widget = QTabWidget(
            self
        )

        self.tab_widget.setTabsClosable(
            True
        )

        self.tab_widget.setMovable(
            True
        )

        self.tab_widget.setDocumentMode(
            True
        )

        self.tab_widget.setElideMode(
            Qt.ElideRight
        )

        self.main_layout.addWidget(
            self.tab_widget
        )

    # =====================================================
    # Connections
    # =====================================================

    def create_connections(self):

        self.tab_widget.tabCloseRequested.connect(
            self.close_tab
        )

        self.tab_widget.currentChanged.connect(
            self.on_current_changed
        )

    def register_tab(
            self,
            tab
    ):
        """
        将WaveformTab内部的Panel信号转发到WaveformArea。
        """

        if tab is None:
            return

        tab.activePanelChanged.connect(
            self.on_active_panel_changed
        )

        tab.panelAdded.connect(
            self.panelAdded
        )

        tab.panelRemoved.connect(
            self.panelRemoved
        )

    # =====================================================
    # Default Tab
    # =====================================================

    def create_default_tab(self):

        if self.tab_widget.count() > 0:
            return self.tab_widget.widget(
                0
            )

        tab = self.create_waveform_tab()

        index = self.tab_widget.addTab(
            tab,
            "Welcome"
        )

        self.tab_widget.setCurrentIndex(
            index
        )

        self.tabAdded.emit(
            tab
        )

        return tab

    def create_waveform_tab(self):
        """
        创建并注册一个WaveformTab。
        """

        tab = WaveformTab(
            self.config,
            self
        )

        self.register_tab(
            tab
        )

        return tab

    # =====================================================
    # Tab Creation
    # =====================================================

    def add_empty_tab(
            self,
            title="New Tab"
    ):

        title = self.normalize_title(
            title
        )

        tab = self.create_waveform_tab()

        index = self.tab_widget.addTab(
            tab,
            title
        )

        self.tab_widget.setCurrentIndex(
            index
        )

        self.tabAdded.emit(
            tab
        )

        return tab

    def add_tab(
            self,
            widget,
            title
    ):

        if widget is None:
            return -1

        title = self.normalize_title(
            title
        )

        if isinstance(
                widget,
                WaveformTab
        ):
            self.register_tab(
                widget
            )

        index = self.tab_widget.addTab(
            widget,
            title
        )

        self.tab_widget.setCurrentIndex(
            index
        )

        self.tabAdded.emit(
            widget
        )

        return index

    # =====================================================
    # Tab Closing
    # =====================================================

    def close_tab(
            self,
            index
    ):

        if index < 0:
            return False

        if index >= self.tab_widget.count():
            return False

        if self.tab_widget.count() <= 1:

            tab = self.tab_widget.widget(
                index
            )

            if tab is not None:
                tab.clear_all_panels(
                    keep_one=True
                )

                self.tab_widget.setTabText(
                    index,
                    "Welcome"
                )

            return False

        widget = self.tab_widget.widget(
            index
        )

        self.tab_widget.removeTab(
            index
        )

        if widget is not None:
            widget.close()
            widget.deleteLater()

        self.tabClosed.emit(
            index
        )

        return True

    def close_current_tab(self):

        return self.close_tab(
            self.current_index()
        )

    def close_all_tabs(self):

        while self.tab_widget.count() > 1:
            self.close_tab(
                self.tab_widget.count() - 1
            )

        if self.tab_widget.count() == 0:
            self.create_default_tab()

        tab = self.current_tab()

        if tab is not None:
            tab.clear_all_panels(
                keep_one=True
            )

        self.tab_widget.setCurrentIndex(
            0
        )

        self.tab_widget.setTabText(
            0,
            "Welcome"
        )

    # =====================================================
    # Current Tab and Panel
    # =====================================================

    def current_tab(self):

        if self.tab_widget is None:
            return None

        return self.tab_widget.currentWidget()

    def current_panel(self):

        tab = self.current_tab()

        if tab is None:
            return None

        if not hasattr(
                tab,
                "current_panel"
        ):
            return None

        return tab.current_panel()

    def current_index(self):

        if self.tab_widget is None:
            return -1

        return self.tab_widget.currentIndex()

    def current_title(self):

        index = self.current_index()

        if index < 0:
            return ""

        return self.tab_widget.tabText(
            index
        )

    def set_current_title(
            self,
            title
    ):

        index = self.current_index()

        if index < 0:
            return

        self.tab_widget.setTabText(
            index,
            self.normalize_title(
                title
            )
        )

    def tab_count(self):

        if self.tab_widget is None:
            return 0

        return self.tab_widget.count()

    def tab_at(
            self,
            index
    ):

        if index < 0:
            return None

        if index >= self.tab_widget.count():
            return None

        return self.tab_widget.widget(
            index
        )

    def set_current_tab(
            self,
            tab
    ):

        if tab is None:
            return False

        index = self.tab_widget.indexOf(
            tab
        )

        if index < 0:
            return False

        self.tab_widget.setCurrentIndex(
            index
        )

        return True

    def set_current_panel(
            self,
            panel
    ):

        tab = self.current_tab()

        if tab is None:
            return False

        return tab.set_active_panel(
            panel
        )

    # =====================================================
    # Tab and Panel Search
    # =====================================================

    def find_panel_by_node(
            self,
            node_path,
            shot=None
    ):
        """
        在全部Tab中根据节点和炮号查找Panel。

        返回：
        (tab_index, tab, panel)
        """

        node_path = self.normalize_node(
            node_path
        )

        normalized_shot = self.normalize_shot(
            shot
        )

        if node_path == "":
            return (
                -1,
                None,
                None
            )

        for index in range(
                self.tab_widget.count()
        ):

            tab = self.tab_widget.widget(
                index
            )

            if tab is None:
                continue

            for panel in tab.panels():

                signal_data = getattr(
                    panel,
                    "signal_data",
                    None
                )

                if signal_data is None:
                    continue

                panel_node = self.normalize_node(
                    getattr(
                        signal_data,
                        "node",
                        ""
                    )
                )

                if panel_node != node_path:
                    continue

                if normalized_shot is not None:

                    panel_shot = self.normalize_shot(
                        getattr(
                            signal_data,
                            "shot",
                            None
                        )
                    )

                    if panel_shot != normalized_shot:
                        continue

                return (
                    index,
                    tab,
                    panel
                )

        return (
            -1,
            None,
            None
        )

    def find_tab_by_node(
            self,
            node_path,
            shot=None
    ):
        """
        兼容旧接口，根据节点查找所在Tab。
        """

        index, tab, panel = self.find_panel_by_node(
            node_path,
            shot
        )

        return (
            index,
            tab
        )

    def find_tab_by_signal(
            self,
            signal_data
    ):

        if signal_data is None:
            return (
                -1,
                None
            )

        node = getattr(
            signal_data,
            "node",
            ""
        )

        shot = getattr(
            signal_data,
            "shot",
            None
        )

        return self.find_tab_by_node(
            node,
            shot
        )

    def find_tab_by_shot(
            self,
            shot
    ):
        """
        根据普通主波形的炮号查找Tab。
        """

        target_shot = self.normalize_shot(
            shot
        )

        if target_shot is None:
            return (
                -1,
                None
            )

        for index in range(
                self.tab_widget.count()
        ):

            tab = self.tab_widget.widget(
                index
            )

            if tab is None:
                continue

            for panel in tab.panels():

                signal_data = getattr(
                    panel,
                    "signal_data",
                    None
                )

                if signal_data is None:
                    continue

                panel_shot = self.normalize_shot(
                    getattr(
                        signal_data,
                        "shot",
                        None
                    )
                )

                if panel_shot == target_shot:
                    return (
                        index,
                        tab
                    )

        return (
            -1,
            None
        )

    def find_tab_by_title(
            self,
            title
    ):

        title = self.normalize_title(
            title
        )

        for index in range(
                self.tab_widget.count()
        ):

            if (
                    self.tab_widget.tabText(
                        index
                    )
                    ==
                    title
            ):
                return (
                    index,
                    self.tab_widget.widget(
                        index
                    )
                )

        return (
            -1,
            None
        )

    # =====================================================
    # Waveform
    # =====================================================

    def open_waveform(
            self,
            signal_data
    ):
        """
        打开普通单炮号波形。

        config.new_tab=True：
        - 同一炮号复用同一个Tab；
        - 不同节点加载到该Tab的不同Panel；
        - 不同炮号新建不同Tab。

        config.new_tab=False：
        - 复用当前Tab；
        - 不同节点加载到当前Tab的不同Panel。
        """

        if signal_data is None:
            return None

        new_tab = bool(
            getattr(
                self.config,
                "new_tab",
                True
            )
        )

        shot = getattr(
            signal_data,
            "shot",
            None
        )

        if new_tab:

            index, tab = self.find_tab_by_shot(
                shot
            )

            if tab is None:

                tab = self.reuse_welcome_or_add_tab(
                    self.get_shot_title(
                        shot
                    )
                )

            else:

                self.tab_widget.setCurrentIndex(
                    index
                )

        else:

            tab = self.current_tab()

            if tab is None:
                tab = self.reuse_welcome_or_add_tab(
                    self.get_shot_title(
                        shot
                    )
                )

        panel = tab.load_signal_to_empty_panel(
            signal_data
        )

        if panel is None:
            return None

        self.update_tab_title(
            tab
        )

        self.set_current_tab(
            tab
        )

        tab.set_active_panel(
            panel
        )

        return tab

    def open_or_activate_waveform(
            self,
            signal_data
    ):
        """
        相同炮号、相同节点存在时更新原Panel；
        否则按open_waveform()规则打开。
        """

        if signal_data is None:
            return None

        node = getattr(
            signal_data,
            "node",
            ""
        )

        shot = getattr(
            signal_data,
            "shot",
            None
        )

        index, tab, panel = self.find_panel_by_node(
            node,
            shot
        )

        if panel is not None:
            panel.load_signal(
                signal_data
            )

            self.tab_widget.setCurrentIndex(
                index
            )

            tab.set_active_panel(
                panel
            )

            self.update_tab_title(
                tab
            )

            return tab

        return self.open_waveform(
            signal_data
        )

    def reuse_welcome_or_add_tab(
            self,
            title
    ):
        """
        当前仅有空Welcome Tab时直接复用，否则新建Tab。
        """

        if self.tab_widget.count() == 1:

            tab = self.tab_widget.widget(
                0
            )

            if (
                    tab is not None
                    and
                    not tab.has_data()
            ):
                self.tab_widget.setTabText(
                    0,
                    self.normalize_title(
                        title
                    )
                )

                self.tab_widget.setCurrentIndex(
                    0
                )

                return tab

        return self.add_empty_tab(
            title
        )

    def add_overlay_signal(
            self,
            signal_data,
            key=None,
            color=None,
            width=None,
            replace=False
    ):

        tab = self.current_tab()

        if tab is None:
            return None

        return tab.add_overlay_signal(
            signal_data=signal_data,
            key=key,
            color=color,
            width=width,
            replace=replace
        )

    # =====================================================
    # Panel Operations
    # =====================================================

    def add_panel_to_current_tab(self):

        tab = self.current_tab()

        if tab is None:
            tab = self.add_empty_tab(
                "New Tab"
            )

        panel = tab.add_panel(
            make_active=True
        )

        self.update_tab_title(
            tab
        )

        return panel

    def remove_current_panel(self):

        tab = self.current_tab()

        if tab is None:
            return False

        result = tab.remove_active_panel()

        self.update_tab_title(
            tab
        )

        return result

    def clear_current_panel(self):

        tab = self.current_tab()

        if tab is None:
            return False

        result = tab.clear_active_panel()

        self.update_tab_title(
            tab
        )

        return result

    def set_current_tab_vertical_layout(self):

        tab = self.current_tab()

        if tab is None:
            return False

        return tab.set_vertical_layout()

    def set_current_tab_horizontal_layout(self):

        tab = self.current_tab()

        if tab is None:
            return False

        return tab.set_horizontal_layout()

    def set_current_tab_auto_layout(self):

        tab = self.current_tab()

        if tab is None:
            return False

        return tab.set_auto_layout()

    def set_current_tab_grid_layout(
            self,
            rows,
            columns
    ):

        tab = self.current_tab()

        if tab is None:
            return False

        return tab.set_grid_layout(
            rows,
            columns
        )

    def equalize_current_tab_panels(self):

        tab = self.current_tab()

        if tab is None:
            return False

        return tab.equalize_panel_sizes()

    # =====================================================
    # Multi-shot Compare
    # =====================================================

    def show_compare_result(
            self,
            result
    ):

        if result is None:
            return None

        success_items = result.success_items()

        if not success_items:
            return None

        title = self.get_compare_title(
            result
        )

        tab = self.add_empty_tab(
            title
        )

        success = tab.display_compare(
            result
        )

        if not success:

            index = self.tab_widget.indexOf(
                tab
            )

            if index >= 0:
                self.close_tab(
                    index
                )

            return None

        index = self.tab_widget.indexOf(
            tab
        )

        if index >= 0:
            self.tab_widget.setTabText(
                index,
                title
            )

            self.tab_widget.setCurrentIndex(
                index
            )

        return tab

    # =====================================================
    # Refresh
    # =====================================================

    def refresh(self):
        """
        刷新当前活动Panel。
        """

        tab = self.current_tab()

        if tab is None:
            return False

        return tab.refresh()

    def refresh_current_tab(self):

        return self.refresh()

    def refresh_current_tab_all_panels(self):

        tab = self.current_tab()

        if tab is None:
            return False

        return tab.refresh_all()

    def refresh_all_tabs(self):

        result = True

        for index in range(
                self.tab_widget.count()
        ):

            tab = self.tab_widget.widget(
                index
            )

            if tab is None:
                continue

            tab_result = tab.refresh_all()

            if tab_result is False:
                result = False

        return result

    # =====================================================
    # Clear
    # =====================================================

    def clear_current_tab(self):

        tab = self.current_tab()

        if tab is None:
            return False

        tab.clear()

        self.update_tab_title(
            tab
        )

        return True

    def clear(self):

        self.close_all_tabs()

    def clear_overlay(self):

        tab = self.current_tab()

        if tab is None:
            return False

        tab.clear_overlay()

        return True

    # =====================================================
    # Export
    # =====================================================

    def export_png(self):

        tab = self.current_tab()

        if tab is None:
            return False

        return tab.export_png()

    def export_csv(self):

        tab = self.current_tab()

        if tab is None:
            return False

        return tab.export_csv()

    # =====================================================
    # Config
    # =====================================================

    def apply_config(self):

        if self.tab_widget is None:
            return

        for index in range(
                self.tab_widget.count()
        ):

            tab = self.tab_widget.widget(
                index
            )

            if tab is not None:
                tab.apply_config()

    # =====================================================
    # Data Query
    # =====================================================

    def current_signal_data(self):
        """
        返回当前活动Panel的SignalData。
        """

        panel = self.current_panel()

        if panel is None:
            return None

        return getattr(
            panel,
            "signal_data",
            None
        )

    def current_node(self):
        """
        返回当前活动Panel的节点路径。
        """

        panel = self.current_panel()

        if panel is None:
            return ""

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

            return self.normalize_node(
                getattr(
                    request,
                    "node",
                    ""
                )
            )

        signal_data = getattr(
            panel,
            "signal_data",
            None
        )

        if signal_data is None:
            return ""

        return self.normalize_node(
            getattr(
                signal_data,
                "node",
                ""
            )
        )

    def current_has_data(self):

        tab = self.current_tab()

        if tab is None:
            return False

        return tab.has_data()

    def current_panel_has_data(self):

        panel = self.current_panel()

        if panel is None:
            return False

        return panel.has_data()

    def current_overlay_count(self):

        tab = self.current_tab()

        if tab is None:
            return 0

        return tab.overlay_count()

    def current_panel_count(self):

        tab = self.current_tab()

        if tab is None:
            return 0

        return tab.panel_count()

    # =====================================================
    # Slots
    # =====================================================

    def on_current_changed(
            self,
            index
    ):

        tab = self.tab_at(
            index
        )

        self.currentTabChanged.emit(
            tab
        )

        if tab is None:

            self.currentPanelChanged.emit(
                None
            )

        else:

            self.currentPanelChanged.emit(
                tab.current_panel()
            )

    def on_active_panel_changed(
            self,
            panel
    ):

        sender_tab = self.sender()

        if sender_tab is not self.current_tab():
            return

        self.currentPanelChanged.emit(
            panel
        )

    # =====================================================
    # Tab Title
    # =====================================================

    def update_tab_title(
            self,
            tab
    ):
        """
        根据Tab中面板的数据更新标题。
        """

        if tab is None:
            return

        index = self.tab_widget.indexOf(
            tab
        )

        if index < 0:
            return

        data_panels = []

        for panel in tab.panels():

            if panel.has_data():
                data_panels.append(
                    panel
                )

        if not data_panels:
            self.tab_widget.setTabText(
                index,
                "Welcome"
            )

            return

        first_signal = getattr(
            data_panels[0],
            "signal_data",
            None
        )

        first_shot = getattr(
            first_signal,
            "shot",
            None
        )

        if len(data_panels) == 1:

            title = self.get_signal_title(
                first_signal
            )

        else:

            title = "{} [{} Plots]".format(
                self.get_shot_title(
                    first_shot
                ),
                len(data_panels)
            )

        self.tab_widget.setTabText(
            index,
            self.normalize_title(
                title
            )
        )

    # =====================================================
    # Helper
    # =====================================================

    @staticmethod
    def normalize_title(
            title
    ):

        if title is None:
            return "Waveform"

        title = str(
            title
        ).strip()

        if title == "":
            return "Waveform"

        return title

    @staticmethod
    def normalize_node(
            node_path
    ):

        if node_path is None:
            return ""

        return str(
            node_path
        ).strip().upper()

    @staticmethod
    def normalize_shot(
            shot
    ):

        if shot is None:
            return None

        try:
            return int(
                shot
            )
        except (
                TypeError,
                ValueError
        ):
            return str(
                shot
            ).strip()

    @classmethod
    def get_signal_title(
            cls,
            signal_data
    ):

        if signal_data is None:
            return "Waveform"

        title = getattr(
            signal_data,
            "name",
            ""
        )

        if not title:
            title = getattr(
                signal_data,
                "node",
                "Waveform"
            )

        title = cls.normalize_title(
            title
        )

        shot = getattr(
            signal_data,
            "shot",
            None
        )

        if shot is not None:
            title = "{} [Shot {}]".format(
                title,
                shot
            )

        return title

    @classmethod
    def get_shot_title(
            cls,
            shot
    ):

        if shot is None:
            return "Waveform"

        return "Shot {}".format(
            shot
        )

    @classmethod
    def get_compare_title(
            cls,
            result
    ):

        request = getattr(
            result,
            "request",
            None
        )

        node = cls.normalize_node(
            getattr(
                request,
                "node",
                ""
            )
        )

        if node == "":
            return "Compare"

        title = node

        if ":" in title:

            title = title.rsplit(
                ":",
                1
            )[-1]

        elif "." in title:

            title = title.rsplit(
                ".",
                1
            )[-1]

        title = title.lstrip(
            "\\"
        ).strip()

        if title == "":
            title = "Waveform"

        return "{} Compare".format(
            title
        )
