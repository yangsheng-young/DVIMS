# -*- coding: utf-8 -*-

"""
==========================================================
Project : NNBI_database
File    : parameter_panel.py
Author  :
Date    :
Description : Runtime Parameter Panel
==========================================================
"""

from PySide2.QtCore import (
    Qt,
    Signal,
)

from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QSpinBox,
    QPushButton,
    QGroupBox,
    QComboBox,
    QScrollArea,
    QSizePolicy,
)


class ParameterPanel(QWidget):
    """
    运行时参数面板。

    当前阶段实现：
    1. 波形查询降频开关；
    2. 单条波形最大读取点数；
    3. 降频模式显示；
    4. 当前活动波形的原始点数、实际点数和采样步长；
    5. 当前Tree和炮号显示；
    6. Apply和Apply and Reload操作；
    7. 为后续高压、电流等当前炮号参数预留统一接口。

    本控件本身不直接访问MDSplus数据库。
    MainWindow在后续阶段将其放入QDockWidget，并负责连接
    MDSController和当前WaveformPanel。
    """

    queryOptionsApplied = Signal(
        bool,
        int
    )

    queryOptionsReloadRequested = Signal(
        bool,
        int
    )

    currentShotRefreshRequested = Signal()

    def __init__(
            self,
            config,
            parent=None
    ):

        super(ParameterPanel, self).__init__(
            parent
        )

        self.config = config

        self.scroll_area = None
        self.content_widget = None
        self.content_layout = None

        self.query_group = None
        self.current_shot_group = None
        self.high_voltage_group = None
        self.current_group = None

        self.check_downsample = None
        self.combo_mode = None
        self.spin_max_points = None

        self.lbl_original_points_value = None
        self.lbl_loaded_points_value = None
        self.lbl_sample_step_value = None
        self.lbl_downsample_state_value = None

        self.btn_apply = None
        self.btn_apply_reload = None

        self.lbl_tree_value = None
        self.lbl_shot_value = None
        self.btn_refresh_shot = None

        self.high_voltage_labels = {}
        self.current_labels = {}

        self.init_ui()
        self.create_connections()
        self.load_config()

    # =====================================================
    # UI
    # =====================================================

    def init_ui(self):

        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(
            0
        )

        self.scroll_area = QScrollArea(
            self
        )

        self.scroll_area.setWidgetResizable(
            True
        )

        self.scroll_area.setFrameShape(
            QScrollArea.NoFrame
        )

        self.content_widget = QWidget(
            self.scroll_area
        )

        self.content_layout = QVBoxLayout(
            self.content_widget
        )

        self.content_layout.setContentsMargins(
            6,
            6,
            6,
            6
        )

        self.content_layout.setSpacing(
            8
        )

        self.create_query_group()
        self.create_current_shot_group()
        self.create_high_voltage_group()
        self.create_current_group()

        self.content_layout.addStretch(
            1
        )

        self.scroll_area.setWidget(
            self.content_widget
        )

        main_layout.addWidget(
            self.scroll_area
        )

        self.setMinimumWidth(
            250
        )

        self.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Expanding
        )

    """
    Enable Downsampling
    勾选：进入降频模式
    取消勾选：全量读取
    """

    def create_query_group(self):

        self.query_group = QGroupBox(
            "Data Query",
            self.content_widget
        )

        layout = QGridLayout(
            self.query_group
        )

        layout.setContentsMargins(
            8,
            12,
            8,
            8
        )

        layout.setHorizontalSpacing(
            8
        )

        layout.setVerticalSpacing(
            7
        )

        self.check_downsample = QCheckBox(
            "Enable Downsampling",
            self.query_group
        )

        layout.addWidget(
            self.check_downsample,
            0,
            0,
            1,
            2
        )

        lbl_mode = QLabel(
            "Mode:",
            self.query_group
        )

        self.combo_mode = QComboBox(
            self.query_group
        )

        self.combo_mode.addItem(
            "Stride",
            "stride"
        )

        self.combo_mode.setEnabled(
            False
        )

        self.combo_mode.setToolTip(
            "Current version supports server-side "
            "equal-interval sampling."
        )

        layout.addWidget(
            lbl_mode,
            1,
            0
        )

        layout.addWidget(
            self.combo_mode,
            1,
            1
        )

        lbl_max_points = QLabel(
            "Maximum Points:",
            self.query_group
        )

        self.spin_max_points = QSpinBox(
            self.query_group
        )

        self.spin_max_points.setRange(
            100,
            2000000
        )

        self.spin_max_points.setSingleStep(
            1000
        )

        self.spin_max_points.setValue(
            10000
        )

        self.spin_max_points.setAccelerated(
            True
        )

        self.spin_max_points.setToolTip(
            "Maximum number of points returned for one waveform."
        )

        layout.addWidget(
            lbl_max_points,
            2,
            0
        )

        layout.addWidget(
            self.spin_max_points,
            2,
            1
        )

        separator = QLabel(
            "Current Waveform",
            self.query_group
        )

        separator.setAlignment(
            Qt.AlignLeft
            |
            Qt.AlignVCenter
        )

        layout.addWidget(
            separator,
            3,
            0,
            1,
            2
        )

        lbl_original = QLabel(
            "Original Points:",
            self.query_group
        )

        self.lbl_original_points_value = self.create_value_label(
            "-"
        )

        layout.addWidget(
            lbl_original,
            4,
            0
        )

        layout.addWidget(
            self.lbl_original_points_value,
            4,
            1
        )

        lbl_loaded = QLabel(
            "Loaded Points:",
            self.query_group
        )

        self.lbl_loaded_points_value = self.create_value_label(
            "-"
        )

        layout.addWidget(
            lbl_loaded,
            5,
            0
        )

        layout.addWidget(
            self.lbl_loaded_points_value,
            5,
            1
        )

        lbl_step = QLabel(
            "Sample Step:",
            self.query_group
        )

        self.lbl_sample_step_value = self.create_value_label(
            "-"
        )

        layout.addWidget(
            lbl_step,
            6,
            0
        )

        layout.addWidget(
            self.lbl_sample_step_value,
            6,
            1
        )

        lbl_state = QLabel(
            "State:",
            self.query_group
        )

        self.lbl_downsample_state_value = self.create_value_label(
            "No Data"
        )

        layout.addWidget(
            lbl_state,
            7,
            0
        )

        layout.addWidget(
            self.lbl_downsample_state_value,
            7,
            1
        )

        button_layout = QHBoxLayout()

        button_layout.setContentsMargins(
            0,
            3,
            0,
            0
        )

        button_layout.setSpacing(
            6
        )

        self.btn_apply = QPushButton(
            "Apply",
            self.query_group
        )

        self.btn_apply_reload = QPushButton(
            "Apply and Reload",
            self.query_group
        )

        self.btn_apply.setToolTip(
            "Apply settings to subsequent queries."
        )

        self.btn_apply_reload.setToolTip(
            "Apply settings and reload the current waveform node."
        )

        button_layout.addWidget(
            self.btn_apply
        )

        button_layout.addWidget(
            self.btn_apply_reload
        )

        layout.addLayout(
            button_layout,
            8,
            0,
            1,
            2
        )

        layout.setColumnStretch(
            1,
            1
        )

        self.content_layout.addWidget(
            self.query_group
        )

    def create_current_shot_group(self):

        self.current_shot_group = QGroupBox(
            "Current Shot",
            self.content_widget
        )

        layout = QGridLayout(
            self.current_shot_group
        )

        layout.setContentsMargins(
            8,
            12,
            8,
            8
        )

        layout.setHorizontalSpacing(
            8
        )

        layout.setVerticalSpacing(
            7
        )

        lbl_tree = QLabel(
            "Tree:",
            self.current_shot_group
        )

        self.lbl_tree_value = self.create_value_label(
            "-"
        )

        layout.addWidget(
            lbl_tree,
            0,
            0
        )

        layout.addWidget(
            self.lbl_tree_value,
            0,
            1
        )

        lbl_shot = QLabel(
            "Shot:",
            self.current_shot_group
        )

        self.lbl_shot_value = self.create_value_label(
            "-"
        )

        layout.addWidget(
            lbl_shot,
            1,
            0
        )

        layout.addWidget(
            self.lbl_shot_value,
            1,
            1
        )

        self.btn_refresh_shot = QPushButton(
            "Refresh Parameters",
            self.current_shot_group
        )

        self.btn_refresh_shot.setToolTip(
            "Refresh parameters for the current tree and shot."
        )

        layout.addWidget(
            self.btn_refresh_shot,
            2,
            0,
            1,
            2
        )

        layout.setColumnStretch(
            1,
            1
        )

        self.content_layout.addWidget(
            self.current_shot_group
        )

    def create_high_voltage_group(self):
        """
        创建高压参数预留区域。

        当前版本仅提供可扩展的键值显示结构，
        后续接入具体MDSplus节点时无需修改ParameterPanel整体布局。
        """

        self.high_voltage_group = QGroupBox(
            "High Voltage",
            self.content_widget
        )

        layout = QGridLayout(
            self.high_voltage_group
        )

        layout.setContentsMargins(
            8,
            12,
            8,
            8
        )

        layout.setHorizontalSpacing(
            8
        )

        layout.setVerticalSpacing(
            7
        )

        self.add_parameter_row(
            layout,
            self.high_voltage_labels,
            "voltage",
            "Voltage:",
            0
        )

        self.add_parameter_row(
            layout,
            self.high_voltage_labels,
            "set_voltage",
            "Set Voltage:",
            1
        )

        self.add_parameter_row(
            layout,
            self.high_voltage_labels,
            "status",
            "Status:",
            2
        )

        layout.setColumnStretch(
            1,
            1
        )

        # TODO 预留参数
        # self.set_group_placeholder_state(
        #     self.high_voltage_labels
        # )

        self.content_layout.addWidget(
            self.high_voltage_group
        )

    def create_current_group(self):
        """
        创建电流参数预留区域。
        """

        self.current_group = QGroupBox(
            "Current",
            self.content_widget
        )

        layout = QGridLayout(
            self.current_group
        )

        layout.setContentsMargins(
            8,
            12,
            8,
            8
        )

        layout.setHorizontalSpacing(
            8
        )

        layout.setVerticalSpacing(
            7
        )

        self.add_parameter_row(
            layout,
            self.current_labels,
            "beam_current",
            "Beam Current:",
            0
        )

        self.add_parameter_row(
            layout,
            self.current_labels,
            "arc_current",
            "Arc Current:",
            1
        )

        self.add_parameter_row(
            layout,
            self.current_labels,
            "filament_current",
            "Filament Current:",
            2
        )

        layout.setColumnStretch(
            1,
            1
        )

        # TODO 预留参数
        # self.set_group_placeholder_state(
        #     self.current_labels
        # )

        self.content_layout.addWidget(
            self.current_group
        )

    # =====================================================
    # Connections
    # =====================================================

    def create_connections(self):

        self.check_downsample.toggled.connect(
            self.on_downsample_toggled
        )

        self.btn_apply.clicked.connect(
            self.emit_apply
        )

        self.btn_apply_reload.clicked.connect(
            self.emit_apply_and_reload
        )

        self.btn_refresh_shot.clicked.connect(
            self.currentShotRefreshRequested
        )

    # =====================================================
    # Query Options
    # =====================================================

    def load_config(self):
        """
        从Config对象读取当前默认参数。

        Config尚未加入这些字段时使用安全默认值。
        """

        enabled = getattr(
            self.config,
            "downsample_enabled",
            True
        )

        max_points = getattr(
            self.config,
            "max_points",
            10000
        )

        self.set_query_options(
            downsample_enabled=enabled,
            max_points=max_points
        )

    def set_query_options(
            self,
            downsample_enabled,
            max_points
    ):

        self.check_downsample.blockSignals(
            True
        )

        self.check_downsample.setChecked(
            bool(
                downsample_enabled
            )
        )

        self.check_downsample.blockSignals(
            False
        )

        try:

            max_points = int(
                max_points
            )

        except Exception:

            max_points = 10000

        max_points = max(
            self.spin_max_points.minimum(),
            min(
                self.spin_max_points.maximum(),
                max_points
            )
        )

        self.spin_max_points.setValue(
            max_points
        )

        self.on_downsample_toggled(
            self.check_downsample.isChecked()
        )

    def query_options(self):

        return {
            "downsample_enabled": (
                self.check_downsample.isChecked()
            ),
            "max_points": self.spin_max_points.value(),
            "downsample_mode": "stride"
        }

    def emit_apply(self):

        options = self.query_options()

        self.queryOptionsApplied.emit(
            options["downsample_enabled"],
            options["max_points"]
        )

    def emit_apply_and_reload(self):

        options = self.query_options()

        self.queryOptionsReloadRequested.emit(
            options["downsample_enabled"],
            options["max_points"]
        )

    def on_downsample_toggled(
            self,
            enabled
    ):

        enabled = bool(
            enabled
        )

        self.spin_max_points.setEnabled(
            enabled
        )

        self.combo_mode.setEnabled(
            False
        )

        if enabled:

            self.spin_max_points.setToolTip(
                "Maximum number of points returned for one waveform."
            )

        else:

            self.spin_max_points.setToolTip(
                "Downsampling is disabled; all waveform points "
                "will be requested."
            )

    # =====================================================
    # Query Result Information
    # =====================================================

    def set_signal_info(
            self,
            signal_data
    ):
        """
        显示当前活动波形的降频读取信息。
        """

        if signal_data is None:
            self.clear_signal_info()

            return

        original_size = self.safe_int(
            getattr(
                signal_data,
                "original_size",
                0
            )
        )

        loaded_size = self.safe_int(
            getattr(
                signal_data,
                "loaded_size",
                0
            )
        )

        sample_step = self.safe_int(
            getattr(
                signal_data,
                "sample_step",
                1
            ),
            default=1
        )

        downsampled = bool(
            getattr(
                signal_data,
                "downsampled",
                False
            )
        )

        self.lbl_original_points_value.setText(
            self.format_count(
                original_size
            )
        )

        self.lbl_loaded_points_value.setText(
            self.format_count(
                loaded_size
            )
        )

        self.lbl_sample_step_value.setText(
            str(
                max(
                    1,
                    sample_step
                )
            )
        )

        if downsampled:

            state = "Downsampled"

        elif loaded_size > 0:

            state = "Full Data"

        else:

            state = "No Data"

        self.lbl_downsample_state_value.setText(
            state
        )

    def clear_signal_info(self):

        self.lbl_original_points_value.setText(
            "-"
        )

        self.lbl_loaded_points_value.setText(
            "-"
        )

        self.lbl_sample_step_value.setText(
            "-"
        )

        self.lbl_downsample_state_value.setText(
            "No Data"
        )

    # =====================================================
    # Current Shot
    # =====================================================

    def set_current_tree(
            self,
            tree
    ):

        self.lbl_tree_value.setText(
            self.format_text(
                tree
            )
        )

    def set_current_shot(
            self,
            shot
    ):

        self.lbl_shot_value.setText(
            self.format_text(
                shot
            )
        )

    def set_tree_shot(
            self,
            tree,
            shot
    ):

        self.set_current_tree(
            tree
        )

        self.set_current_shot(
            shot
        )

    def clear_tree_shot(self):

        self.set_tree_shot(
            None,
            None
        )

    # =====================================================
    # Reserved Parameter Interface
    # =====================================================

    def set_high_voltage_parameter(
            self,
            name,
            value,
            unit=""
    ):

        return self.set_named_parameter(
            self.high_voltage_labels,
            name,
            value,
            unit
        )

    def set_current_parameter(
            self,
            name,
            value,
            unit=""
    ):

        return self.set_named_parameter(
            self.current_labels,
            name,
            value,
            unit
        )

    def set_named_parameter(
            self,
            label_map,
            name,
            value,
            unit=""
    ):

        label = label_map.get(
            str(
                name
            )
        )

        if label is None:
            return False

        text = self.format_parameter_value(
            value,
            unit
        )

        label.setText(
            text
        )

        return True

    def clear_high_voltage_parameters(self):

        self.set_group_placeholder_state(
            self.high_voltage_labels
        )

    def clear_current_parameters(self):

        self.set_group_placeholder_state(
            self.current_labels
        )

    def clear_shot_parameters(self):

        self.clear_high_voltage_parameters()
        self.clear_current_parameters()

    # =====================================================
    # State
    # =====================================================

    def set_busy(
            self,
            busy
    ):
        """
        数据读取期间禁用会触发新查询的按钮。
        """

        busy = bool(
            busy
        )

        self.btn_apply.setEnabled(
            not busy
        )

        self.btn_apply_reload.setEnabled(
            not busy
        )

        self.btn_refresh_shot.setEnabled(
            not busy
        )

    # =====================================================
    # Helpers
    # =====================================================

    def create_value_label(
            self,
            text
    ):

        label = QLabel(
            str(
                text
            ),
            self
        )

        label.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        label.setAlignment(
            Qt.AlignLeft
            |
            Qt.AlignVCenter
        )

        return label

    def add_parameter_row(
            self,
            layout,
            label_map,
            key,
            title,
            row
    ):

        name_label = QLabel(
            title,
            self
        )

        value_label = self.create_value_label(
            "-"
        )

        layout.addWidget(
            name_label,
            row,
            0
        )

        layout.addWidget(
            value_label,
            row,
            1
        )

        label_map[
            key
        ] = value_label

    @staticmethod
    def set_group_placeholder_state(
            label_map
    ):

        for label in label_map.values():
            label.setText(
                "Not Configured"
            )

    @staticmethod
    def safe_int(
            value,
            default=0
    ):

        try:

            return int(
                value
            )

        except Exception:

            return int(
                default
            )

    @staticmethod
    def format_count(
            value
    ):

        try:

            value = int(
                value
            )

        except Exception:

            return "-"

        if value < 0:
            return "-"

        return "{:,}".format(
            value
        )

    @staticmethod
    def format_text(
            value
    ):

        if value is None:
            return "-"

        text = str(
            value
        ).strip()

        if text == "":
            return "-"

        return text

    @classmethod
    def format_parameter_value(
            cls,
            value,
            unit=""
    ):

        text = cls.format_text(
            value
        )

        unit = str(
            unit
        ).strip()

        if text == "-":
            return text

        if unit == "":
            return text

        return "{} {}".format(
            text,
            unit
        )
