# -*- coding: utf-8 -*-
"""
-------------------------------------------------
Project : NNBI_database
File    : settings_dialog.py
Author  :
Date    :
Description : Settings Dialog
-------------------------------------------------
"""

from PySide2.QtCore import (
    Qt,
    Signal,
)
from PySide2.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QCheckBox,
    QComboBox,
    QPushButton,
    QGroupBox,
)


class SettingsDialog(QDialog):
    """
    Settings Dialog
    """
    settingsApplied = Signal()

    def __init__(self, config, parent=None):
        super(SettingsDialog, self).__init__(parent)

        self.config = config

        self.setWindowTitle("Settings")
        self.setWindowModality(Qt.ApplicationModal)
        self.resize(520, 560)

        self.init_ui()

    # =====================================================
    # UI
    # =====================================================

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # ==================================================
        # General
        # ==================================================

        group_general = QGroupBox("General")

        general_layout = QGridLayout(group_general)

        general_layout.addWidget(QLabel("Theme"), 0, 0)

        self.cmb_theme = QComboBox()
        self.cmb_theme.addItems(["Light", "Dark"])

        general_layout.addWidget(self.cmb_theme, 0, 1)

        general_layout.addWidget(QLabel("Refresh Interval (ms)"), 1, 0)

        self.spin_refresh = QSpinBox()
        self.spin_refresh.setRange(100, 60000)
        self.spin_refresh.setSingleStep(100)
        self.spin_refresh.setValue(1000)

        general_layout.addWidget(self.spin_refresh, 1, 1)

        # ==================================================
        # MDSplus
        # ==================================================

        group_mds = QGroupBox("MDSplus")

        mds_layout = QGridLayout(group_mds)

        mds_layout.addWidget(QLabel("Server"), 0, 0)

        self.edit_server = QLineEdit()

        mds_layout.addWidget(self.edit_server, 0, 1)

        mds_layout.addWidget(QLabel("Port"), 1, 0)

        self.spin_port = QSpinBox()
        self.spin_port.setRange(1, 65535)

        mds_layout.addWidget(self.spin_port, 1, 1)

        mds_layout.addWidget(QLabel("Default Tree"), 2, 0)

        self.edit_tree = QLineEdit()

        mds_layout.addWidget(self.edit_tree, 2, 1)

        # ==================================================
        # Tree
        # ==================================================

        group_tree = QGroupBox(
            "Tree Browser"
        )

        tree_layout = QGridLayout(
            group_tree
        )

        self.chk_show_full_path = QCheckBox(
            "Show Full Node Path"
        )

        tree_layout.addWidget(
            self.chk_show_full_path,
            0,
            0,
            1,
            2
        )

        # ==================================================
        # Waveform
        # ==================================================

        group_waveform = QGroupBox(
            "Waveform"
        )

        waveform_layout = QGridLayout(
            group_waveform
        )

        self.chk_crosshair = QCheckBox(
            "Show Crosshair"
        )

        self.chk_legend = QCheckBox(
            "Show Legend"
        )

        waveform_layout.addWidget(
            self.chk_crosshair,
            0,
            0,
            1,
            2
        )

        waveform_layout.addWidget(
            self.chk_legend,
            1,
            0,
            1,
            2
        )

        # ==================================================
        # Export
        # ==================================================

        group_export = QGroupBox(
            "Export"
        )

        export_layout = QGridLayout(
            group_export
        )

        export_layout.addWidget(
            QLabel("Export Path"),
            0,
            0
        )

        self.edit_export_path = QLineEdit()

        export_layout.addWidget(
            self.edit_export_path,
            0,
            1
        )

        export_layout.addWidget(
            QLabel("Image Width (px)"),
            1,
            0
        )

        self.spin_image_width = QSpinBox()

        self.spin_image_width.setRange(
            100,
            20000
        )

        self.spin_image_width.setSingleStep(
            100
        )

        self.spin_image_width.setValue(
            1600
        )

        export_layout.addWidget(
            self.spin_image_width,
            1,
            1
        )

        # ==================================================
        # Buttons
        # ==================================================

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        self.btn_ok = QPushButton("OK")

        self.btn_cancel = QPushButton("Cancel")

        self.btn_apply = QPushButton("Apply")

        button_layout.addWidget(self.btn_ok)

        button_layout.addWidget(self.btn_cancel)

        button_layout.addWidget(self.btn_apply)

        # ==================================================
        # Layout
        # ==================================================

        main_layout.addWidget(
            group_general
        )

        main_layout.addWidget(
            group_mds
        )

        main_layout.addWidget(
            group_tree
        )

        main_layout.addWidget(
            group_waveform
        )

        main_layout.addWidget(
            group_export
        )

        main_layout.addStretch()

        main_layout.addLayout(button_layout)

        # ==================================================
        # Signal
        # ==================================================

        self.btn_ok.clicked.connect(self.on_ok)

        self.btn_cancel.clicked.connect(self.reject)

        self.btn_apply.clicked.connect(self.on_apply)

        self.load_settings()

    # =====================================================
    # Interface
    # =====================================================

    def load_settings(self):
        """
        将Config内容加载到设置控件
        """

        self.edit_server.setText(
            self.config.host
        )

        self.edit_tree.setText(
            self.config.tree
        )

        self.spin_refresh.setValue(
            self.config.interval
        )

        self.cmb_theme.setCurrentText(
            self.config.theme
        )

        self.spin_port.setValue(
            self.config.port
        )

        self.chk_show_full_path.setChecked(
            bool(
                getattr(
                    self.config,
                    "show_full_path",
                    False
                )
            )
        )

        self.chk_crosshair.setChecked(
            bool(
                getattr(
                    self.config,
                    "show_crosshair",
                    True
                )
            )
        )

        self.chk_legend.setChecked(
            bool(
                getattr(
                    self.config,
                    "show_legend",
                    True
                )
            )
        )

        self.edit_export_path.setText(
            str(
                getattr(
                    self.config,
                    "export_path",
                    "export"
                )
            )
        )

        image_width = getattr(
            self.config,
            "export_image_width",
            1600
        )

        try:
            image_width = int(
                image_width
            )
        except Exception:
            image_width = 1600

        if image_width < 100:
            image_width = 100

        self.spin_image_width.setValue(
            image_width
        )

    def save_settings(self):
        """
        将设置控件内容写入Config并保存
        """

        self.config.host = (
            self.edit_server.text().strip()
        )

        self.config.port = (
            self.spin_port.value()
        )

        self.config.tree = (
            self.edit_tree.text().strip()
        )

        self.config.theme = (
            self.cmb_theme.currentText()
        )

        self.config.interval = (
            self.spin_refresh.value()
        )

        self.config.show_full_path = (
            self.chk_show_full_path.isChecked()
        )

        self.config.show_crosshair = (
            self.chk_crosshair.isChecked()
        )

        self.config.show_legend = (
            self.chk_legend.isChecked()
        )

        export_path = (
            self.edit_export_path.text().strip()
        )

        if export_path == "":
            export_path = "export"

        self.config.export_path = export_path

        self.config.export_image_width = (
            self.spin_image_width.value()
        )

        self.config.save()

    # =====================================================
    # Slot
    # =====================================================

    def on_ok(self):
        self.save_settings()

        self.accept()

    def on_apply(self):
        """
        保存设置并立即应用
        """

        self.save_settings()

        self.settingsApplied.emit()
