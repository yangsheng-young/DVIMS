# -*- coding: utf-8 -*-
"""
-------------------------------------------------
Project : NNBI_database
File    : main.py
Author  :
Date    :
Description : Program Entry
-------------------------------------------------
"""

import sys
import pyqtgraph as pg

from PySide2.QtGui import QFont

from PySide2.QtWidgets import QApplication

from ui.main_window import MainWindow
from config import Config


def main():
    """
    Program Entry
    """

    app = QApplication(sys.argv)

    config = Config()
    config.load()

    # =====================================================
    # Application Font
    # =====================================================

    font = QFont(
        config.font,
        config.font_size
    )

    app.setFont(font)

    # =====================================================
    # PyQtGraph Global Configuration
    # =====================================================

    pg.setConfigOptions(
        antialias=config.antialias
    )

    # =====================================================
    # Main Window
    # =====================================================

    window = MainWindow(config)

    if config.maximized:
        window.showMaximized()
    else:
        window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
