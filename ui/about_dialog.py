# -*- coding: utf-8 -*-
"""
-------------------------------------------------
Project : NNBI_database
File    : about_dialog.py
Author  :
Date    :
Description : About Dialog
-------------------------------------------------
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
)


class AboutDialog(QDialog):
    """
    About Dialog
    """

    def __init__(self, config, parent=None):
        super(AboutDialog, self).__init__(parent)

        self.config = config

        self.setWindowTitle("About")
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(420, 260)

        self.init_ui()

    # =====================================================
    # UI
    # =====================================================

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(20, 20, 20, 20)

        main_layout.setSpacing(10)

        title = QLabel(self.config.name)
        title.setAlignment(Qt.AlignCenter)
        font = title.font()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)

        version = QLabel("Version : {}".format(self.config.version))
        version.setAlignment(Qt.AlignCenter)

        python = QLabel("Python : 3.6.6")
        python.setAlignment(Qt.AlignCenter)

        qt = QLabel("GUI : PySide2")
        qt.setAlignment(Qt.AlignCenter)

        description = QLabel(
            "MDSplus Data Visualization Platform"
        )
        description.setAlignment(Qt.AlignCenter)

        # company = QLabel(self.config.ORGANIZATION)
        # company.setAlignment(Qt.AlignCenter)
        #
        # copyright_label = QLabel(
        #     "Copyright © {}".format(self.config.ORGANIZATION)
        # )
        # copyright_label.setAlignment(Qt.AlignCenter)

        main_layout.addStretch()

        main_layout.addWidget(title)
        main_layout.addWidget(version)
        main_layout.addWidget(python)
        main_layout.addWidget(qt)
        main_layout.addWidget(description)
        # main_layout.addWidget(company)
        # main_layout.addWidget(copyright_label)

        main_layout.addStretch()

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        btn_ok = QPushButton("OK")
        btn_ok.setFixedWidth(80)
        btn_ok.clicked.connect(self.accept)

        button_layout.addWidget(btn_ok)

        button_layout.addStretch()

        main_layout.addLayout(button_layout)
