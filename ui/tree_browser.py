# -*- coding: utf-8 -*-
"""
-------------------------------------------------
Project : NNBI_database
File    : tree_browser.py
Author  :
Date    :
Description : Tree Browser
-------------------------------------------------
"""

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QAbstractItemView,
    QLabel,
    QMenu,
    QAction,
)

ROLE_PATH = Qt.UserRole
ROLE_NAME = Qt.UserRole + 1
ROLE_USAGE = Qt.UserRole + 2
ROLE_NID = Qt.UserRole + 3


class TreeBrowser(QWidget):
    """
    Tree Browser
    """

    # 双击节点信号（第二阶段使用）
    nodeOpenRequested = Signal(str)
    # 请求将节点作为叠加波形加载
    overlayRequested = Signal(str)

    def __init__(self, config, parent=None):
        super(TreeBrowser, self).__init__(parent)

        self.config = config

        self.title_label = None
        self.tree = None

        self.init_ui()
        self.create_connections()
        self.init_tree()

    # =====================================================
    # UI
    # =====================================================

    def init_ui(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.title_label = QLabel("Tree Browser")
        layout.addWidget(self.title_label)

        self.tree = QTreeWidget()

        self.tree.setHeaderHidden(True)

        self.tree.setAnimated(True)

        self.tree.setAlternatingRowColors(True)

        self.tree.setSelectionMode(
            QAbstractItemView.SingleSelection
        )

        self.tree.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.tree.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.tree.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        layout.addWidget(self.tree)

    # =====================================================
    # Connections
    # =====================================================

    def create_connections(self):
        """
        创建Tree事件连接
        """

        self.tree.itemDoubleClicked.connect(
            self.on_item_double_clicked
        )

        self.tree.customContextMenuRequested.connect(
            self.on_context_menu
        )

    # =====================================================
    # Default Tree
    # =====================================================

    def init_tree(self):
        """
        初始化未连接状态
        """

        self.show_message(
            "Not Connected"
        )

    # =====================================================
    # Tree Operations
    # =====================================================
    def show_message(
            self,
            message
    ):
        """
        在Tree区域显示状态信息
        """

        self.tree.clear()

        item = QTreeWidgetItem(
            self.tree
        )

        item.setText(
            0,
            str(message)
        )

        item.setData(
            0,
            Qt.UserRole,
            ""
        )

        item.setFlags(
            item.flags()
            & ~Qt.ItemIsSelectable
        )

        return item

    def show_loading(self):
        """
        显示Tree加载状态
        """

        self.show_message(
            "Loading Tree..."
        )

    def show_not_connected(self):
        """
        显示未连接状态
        """

        self.show_message(
            "Not Connected"
        )

    def show_empty(self):
        """
        显示空Tree状态
        """

        self.show_message(
            "Tree is empty"
        )

    def show_tree_closed(self):
        """
        显示Tree关闭状态
        """

        self.show_message(
            "Tree Closed"
        )

    def set_busy(
            self,
            busy
    ):
        """
        设置Tree控件操作状态
        """

        self.tree.setEnabled(
            not bool(busy)
        )

    def clear(self):

        self.tree.clear()

    def expand_all(self):

        self.tree.expandAll()

    def collapse_all(self):

        self.tree.collapseAll()

    def current_item(self):

        return self.tree.currentItem()

    def current_text(self):

        item = self.current_item()

        if item is None:
            return ""

        return item.text(0)

    def current_path(self):
        """
        返回当前选中节点路径
        """

        return self.item_path(
            self.current_item()
        )

    def item_path(
            self,
            item
    ):
        """
        返回指定Tree节点的完整路径
        """

        if item is None:
            return ""

        path = item.data(
            0,
            ROLE_PATH
        )

        if path is None:
            return ""

        return str(
            path
        ).strip()

    def add_root(self, name, path=""):

        item = QTreeWidgetItem(self.tree)

        item.setText(0, name)

        item.setData(
            0,
            ROLE_PATH,
            path
        )

        item.setData(
            0,
            ROLE_NAME,
            name
        )

        item.setData(
            0,
            ROLE_USAGE,
            ""
        )

        item.setData(
            0,
            ROLE_NID,
            None
        )

        return item

    def add_child(self, parent, name, path=""):

        item = QTreeWidgetItem(parent)

        item.setText(0, name)

        item.setData(
            0,
            ROLE_PATH,
            path
        )

        item.setData(
            0,
            ROLE_NAME,
            name
        )

        item.setData(
            0,
            ROLE_USAGE,
            ""
        )

        item.setData(
            0,
            ROLE_NID,
            None
        )

        return item

    # =====================================================
    # Load Tree
    # =====================================================

    def load_tree(
            self,
            tree_data
    ):
        """
        将后台读取完成的Tree数据加载到界面
        """

        self.tree.setUpdatesEnabled(
            False
        )

        try:

            self.tree.clear()

            if tree_data is None:
                self.show_empty()

                return False

            self.build_tree(
                None,
                tree_data
            )

            if self.config.auto_expand:

                self.expand_all()

            else:

                root = self.tree.topLevelItem(
                    0
                )

                if root is not None:
                    root.setExpanded(
                        True
                    )

            return True

        finally:

            self.tree.setUpdatesEnabled(
                True
            )

            self.tree.viewport().update()

    def build_tree(self, parent_item, data):
        """
        根据Tree数据递归创建界面节点
        """

        if not isinstance(
                data,
                dict
        ):
            return None

        item = QTreeWidgetItem()

        name = str(
            data.get(
                "name",
                ""
            )
        ).strip()

        path = str(
            data.get(
                "path",
                ""
            )
        ).strip()

        usage = str(
            data.get(
                "usage",
                ""
            )
        ).strip()

        nid = data.get(
            "nid"
        )

        if getattr(
                self.config,
                "show_full_path",
                False
        ):
            display_text = path or name
        else:
            display_text = name or path

        item.setText(
            0,
            display_text
        )

        item.setData(
            0,
            ROLE_PATH,
            path
        )

        item.setData(
            0,
            ROLE_NAME,
            name
        )

        item.setData(
            0,
            ROLE_USAGE,
            usage
        )

        item.setData(
            0,
            ROLE_NID,
            nid
        )

        if parent_item is None:

            self.tree.addTopLevelItem(
                item
            )

        else:

            parent_item.addChild(
                item
            )

        children = data.get(
            "children",
            []
        )

        if not isinstance(
                children,
                list
        ):
            return item

        for child in children:
            self.build_tree(
                item,
                child
            )

        return item

    def refresh_item_text(
            self,
            item
    ):
        """
        根据show_full_path刷新一个节点及其子节点
        """

        if item is None:
            return

        name = item.data(
            0,
            ROLE_NAME
        )

        path = item.data(
            0,
            ROLE_PATH
        )

        if name is None:
            name = ""

        if path is None:
            path = ""

        if getattr(
                self.config,
                "show_full_path",
                False
        ):
            text = str(path).strip() or str(name).strip()
        else:
            text = str(name).strip() or str(path).strip()

        item.setText(
            0,
            text
        )

        for index in range(
                item.childCount()
        ):
            self.refresh_item_text(
                item.child(
                    index
                )
            )

    def refresh_display_text(self):
        """
        刷新全部节点的显示名称
        """

        for index in range(
                self.tree.topLevelItemCount()
        ):
            self.refresh_item_text(
                self.tree.topLevelItem(
                    index
                )
            )

    # =====================================================
    # Slot
    # =====================================================

    def on_context_menu(
            self,
            position
    ):
        """
        显示Tree节点右键菜单
        """

        item = self.tree.itemAt(
            position
        )

        if item is None:
            return

        path = self.item_path(
            item
        )

        if path == "":
            return

        self.tree.setCurrentItem(
            item
        )

        menu = QMenu(
            self.tree
        )

        action_open = QAction(
            "Open Waveform",
            menu
        )

        action_overlay = QAction(
            "Add to Current Overlay",
            menu
        )

        action_open.triggered.connect(
            lambda checked=False, value=path:
            self.nodeOpenRequested.emit(value)
        )

        action_overlay.triggered.connect(
            lambda checked=False, value=path:
            self.overlayRequested.emit(value)
        )

        menu.addAction(
            action_open
        )

        menu.addAction(
            action_overlay
        )

        menu.exec_(
            self.tree.viewport().mapToGlobal(
                position
            )
        )

    def on_item_double_clicked(
            self,
            item,
            column
    ):

        if not self.config.double_click_open:
            return

        path = item.data(
            0,
            Qt.UserRole
        )

        if path is None:
            return

        path = str(path).strip()

        if path == "":
            return

        self.nodeOpenRequested.emit(
            path
        )

    # =====================================================
    # Reserved Interface
    # =====================================================

    def refresh(self):

        self.tree.viewport().update()

    def expand_tree(self):

        self.expand_all()

    def collapse_tree(self):

        self.collapse_all()

    # =====================================================
    # Config
    # =====================================================

    def apply_config(self):

        self.tree.setUpdatesEnabled(
            False
        )

        try:

            self.refresh_display_text()

            if self.config.auto_expand:

                self.tree.expandAll()

            else:

                self.tree.collapseAll()

                root = self.tree.topLevelItem(
                    0
                )

                if root is not None:
                    root.setExpanded(
                        True
                    )

        finally:

            self.tree.setUpdatesEnabled(
                True
            )

            self.tree.viewport().update()
