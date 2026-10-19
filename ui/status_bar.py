# -*- coding: utf-8 -*-
"""
-------------------------------------------------
Project : NNBI_database
File    : status_bar.py
Author  :
Date    :
Description : Status Bar
-------------------------------------------------
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QStatusBar,
    QLabel,
)


class StatusBar(QStatusBar):
    """
    Main Status Bar
    """

    def __init__(self, parent=None):
        super(StatusBar, self).__init__(parent)

        self.main_window = parent

        self.lbl_status = None
        self.lbl_tree = None
        self.lbl_shot = None
        self.lbl_node = None

        self.init_ui()

    # =====================================================
    # UI
    # =====================================================

    def init_ui(self):

        self.setSizeGripEnabled(True)

        self.lbl_status = QLabel("Ready")
        self.lbl_tree = QLabel("Tree: --")
        self.lbl_shot = QLabel("Shot: --")
        self.lbl_node = QLabel("Node: --")

        self.lbl_status.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.lbl_tree.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.lbl_shot.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.lbl_node.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.lbl_tree.setMinimumWidth(180)
        self.lbl_shot.setMinimumWidth(120)
        self.lbl_node.setMinimumWidth(350)

        self.addWidget(self.lbl_status, 1)

        self.addPermanentWidget(self.lbl_tree)

        self.addPermanentWidget(self.lbl_shot)

        self.addPermanentWidget(self.lbl_node)

    # =====================================================
    # Status
    # =====================================================

    def showMessage(self, text, timeout=0):

        self.lbl_status.setText(text)

        super(StatusBar, self).showMessage("", timeout)

    def clearMessage(self):

        self.lbl_status.setText("Ready")

        super(StatusBar, self).clearMessage()

    # =====================================================
    # Interface
    # =====================================================

    def set_status(self, text):

        self.lbl_status.setText(text)

    def set_tree(self, tree):

        if tree:
            self.lbl_tree.setText("Tree: {}".format(tree))
        else:
            self.lbl_tree.setText("Tree: --")

    def set_shot(self, shot):

        if shot is None:
            self.lbl_shot.setText("Shot: --")
        else:
            self.lbl_shot.setText("Shot: {}".format(shot))

    def set_node(self, node):

        if node:
            self.lbl_node.setText("Node: {}".format(node))
        else:
            self.lbl_node.setText("Node: --")

    # =====================================================
    # Reset
    # =====================================================

    def reset(self):

        self.set_status("Ready")
        self.set_tree("")
        self.set_shot(None)
        self.set_node("")

    # =====================================================
    # Reserved Interface
    # =====================================================

    def set_connected(self):

        self.set_status("Connected")

    def set_disconnected(self):

        self.set_status("Disconnected")

    def set_busy(self):

        self.set_status("Busy...")

    def set_ready(self):

        self.set_status("Ready")

    def set_message(self, text):

        self.set_status(text)
