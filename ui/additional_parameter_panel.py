# -*- coding: utf-8 -*-

"""
==========================================================
Project : NNBI_database
File    : additional_parameter_panel.py
Description : Extensible Additional Parameter Panel
==========================================================
"""

from PySide2.QtCore import Qt

from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QGroupBox,
    QScrollArea,
    QSizePolicy,
)


class AdditionalParameterPanel(QWidget):
    """
    可扩展附加参数窗口。

    该窗口不直接访问MDSplus数据库，只负责显示参数。

    后续增加参数时，可以通过统一接口动态增加：
        add_parameter_group()
        set_parameter()
        remove_parameter()
        clear_parameter_group()
    """

    def __init__(
            self,
            config,
            parent=None
    ):

        super(AdditionalParameterPanel, self).__init__(
            parent
        )

        self.config = config

        self.scroll_area = None
        self.content_widget = None
        self.content_layout = None

        self.current_shot_group = None
        self.lbl_tree_value = None
        self.lbl_shot_value = None

        # {
        #     group_key: {
        #         "box": QGroupBox,
        #         "layout": QGridLayout,
        #         "labels": {
        #             parameter_key: {
        #                 "name": QLabel,
        #                 "value": QLabel
        #             }
        #         }
        #     }
        # }
        self.parameter_groups = {}

        self.init_ui()

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

        self.create_current_shot_group()

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

        layout.addWidget(
            QLabel(
                "Tree:",
                self.current_shot_group
            ),
            0,
            0
        )

        self.lbl_tree_value = self.create_value_label(
            "-"
        )

        layout.addWidget(
            self.lbl_tree_value,
            0,
            1
        )

        layout.addWidget(
            QLabel(
                "Shot:",
                self.current_shot_group
            ),
            1,
            0
        )

        self.lbl_shot_value = self.create_value_label(
            "-"
        )

        layout.addWidget(
            self.lbl_shot_value,
            1,
            1
        )

        layout.setColumnStretch(
            1,
            1
        )

        self.content_layout.addWidget(
            self.current_shot_group
        )

    # =====================================================
    # Current Shot
    # =====================================================

    def set_tree_shot(
            self,
            tree,
            shot
    ):

        self.lbl_tree_value.setText(
            self.format_text(
                tree
            )
        )

        self.lbl_shot_value.setText(
            self.format_text(
                shot
            )
        )

    def clear_tree_shot(self):

        self.set_tree_shot(
            None,
            None
        )

    # =====================================================
    # Parameter Group API
    # =====================================================

    def add_parameter_group(
            self,
            group_key,
            title=None
    ):
        """
        动态增加一个参数分组。

        Example:
            panel.add_parameter_group(
                "vacuum",
                "Vacuum"
            )
        """

        group_key = self.normalize_key(
            group_key
        )

        if group_key == "":
            return None

        if group_key in self.parameter_groups:
            return self.parameter_groups[
                group_key
            ]["box"]

        if title is None:
            title = group_key

        group_box = QGroupBox(
            str(
                title
            ),
            self.content_widget
        )

        layout = QGridLayout(
            group_box
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

        layout.setColumnStretch(
            1,
            1
        )

        # addStretch(1)始终在最后，因此插入到它前面。
        insert_index = max(
            0,
            self.content_layout.count() - 1
        )

        self.content_layout.insertWidget(
            insert_index,
            group_box
        )

        self.parameter_groups[
            group_key
        ] = {
            "box": group_box,
            "layout": layout,
            "labels": {}
        }

        return group_box

    def remove_parameter_group(
            self,
            group_key
    ):

        group_key = self.normalize_key(
            group_key
        )

        group = self.parameter_groups.pop(
            group_key,
            None
        )

        if group is None:
            return False

        box = group[
            "box"
        ]

        self.content_layout.removeWidget(
            box
        )

        box.deleteLater()

        return True

    def clear_parameter_group(
            self,
            group_key
    ):
        """
        保留分组结构，只将分组内参数值清空为“-”。
        """

        group_key = self.normalize_key(
            group_key
        )

        group = self.parameter_groups.get(
            group_key
        )

        if group is None:
            return False

        for item in group[
            "labels"
        ].values():
            item[
                "value"
            ].setText(
                "-"
            )

        return True

    def clear_all_parameters(self):

        for group_key in list(
                self.parameter_groups.keys()
        ):
            self.clear_parameter_group(
                group_key
            )

    # =====================================================
    # Parameter API
    # =====================================================

    def set_parameter(
            self,
            group_key,
            parameter_key,
            title,
            value,
            unit=""
    ):
        """
        增加或更新一个参数。

        如果分组不存在，会自动创建。

        Example:
            panel.set_parameter(
                "vacuum",
                "source_pressure",
                "Source Pressure:",
                2.3e-5,
                "Pa"
            )
        """

        group_key = self.normalize_key(
            group_key
        )

        parameter_key = self.normalize_key(
            parameter_key
        )

        if (
                group_key == ""
                or
                parameter_key == ""
        ):
            return False

        if group_key not in self.parameter_groups:
            self.add_parameter_group(
                group_key,
                group_key
            )

        group = self.parameter_groups[
            group_key
        ]

        labels = group[
            "labels"
        ]

        if parameter_key not in labels:

            row = len(
                labels
            )

            name_label = QLabel(
                str(
                    title
                ),
                group[
                    "box"
                ]
            )

            value_label = self.create_value_label(
                "-"
            )

            group[
                "layout"
            ].addWidget(
                name_label,
                row,
                0
            )

            group[
                "layout"
            ].addWidget(
                value_label,
                row,
                1
            )

            labels[
                parameter_key
            ] = {
                "name": name_label,
                "value": value_label
            }

        else:

            labels[
                parameter_key
            ][
                "name"
            ].setText(
                str(
                    title
                )
            )

        labels[
            parameter_key
        ][
            "value"
        ].setText(
            self.format_parameter_value(
                value,
                unit
            )
        )

        return True

    def remove_parameter(
            self,
            group_key,
            parameter_key
    ):

        group_key = self.normalize_key(
            group_key
        )

        parameter_key = self.normalize_key(
            parameter_key
        )

        group = self.parameter_groups.get(
            group_key
        )

        if group is None:
            return False

        item = group[
            "labels"
        ].pop(
            parameter_key,
            None
        )

        if item is None:
            return False

        for label in (
                item["name"],
                item["value"]
        ):
            group[
                "layout"
            ].removeWidget(
                label
            )

            label.deleteLater()

        self.rebuild_group_rows(
            group
        )

        return True

    def set_parameter_value(
            self,
            group_key,
            parameter_key,
            value,
            unit=""
    ):
        """
        只更新已存在参数的值。
        """

        group_key = self.normalize_key(
            group_key
        )

        parameter_key = self.normalize_key(
            parameter_key
        )

        group = self.parameter_groups.get(
            group_key
        )

        if group is None:
            return False

        item = group[
            "labels"
        ].get(
            parameter_key
        )

        if item is None:
            return False

        item[
            "value"
        ].setText(
            self.format_parameter_value(
                value,
                unit
            )
        )

        return True

    def rebuild_group_rows(
            self,
            group
    ):

        for row, item in enumerate(
                group[
                    "labels"
                ].values()
        ):
            group[
                "layout"
            ].addWidget(
                item[
                    "name"
                ],
                row,
                0
            )

            group[
                "layout"
            ].addWidget(
                item[
                    "value"
                ],
                row,
                1
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
            Qt.AlignLeft |
            Qt.AlignVCenter
        )

        return label

    @staticmethod
    def normalize_key(
            value
    ):

        if value is None:
            return ""

        return str(
            value
        ).strip()

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

        if text == "-":
            return text

        unit = str(
            unit
        ).strip()

        if unit == "":
            return text

        return "{} {}".format(
            text,
            unit
        )
