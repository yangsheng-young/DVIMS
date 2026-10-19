# -*- coding: utf-8 -*-

"""
==========================================================
Project : NNBI_database
File    : export.py
Author  :
Date    :
Description : Waveform Export Manager
==========================================================
"""

import csv
import os

import numpy as np
import pyqtgraph.exporters

from PySide2.QtCore import (
    QObject,
    Signal
)


class WaveformExport(QObject):
    """
    波形导出管理器

    功能：
    1. 导出当前波形图片 PNG
    2. 导出单条波形 CSV
    3. 导出多条叠加波形 CSV
    4. 自动创建导出目录
    5. 自动补全文件扩展名
    6. 规范化文件名
    """

    exportStarted = Signal(str)
    exportFinished = Signal(str)
    exportError = Signal(str)

    def __init__(
            self,
            plot_widget=None,
            overlay_manager=None,
            parent=None
    ):

        super(WaveformExport, self).__init__(
            parent
        )

        self.plot_widget = plot_widget
        self.overlay_manager = overlay_manager

        self.default_directory = ""

        self.image_width = 1600
        self.csv_encoding = "utf-8-sig"

    # =====================================================
    # Plot Widget
    # =====================================================

    def set_plot_widget(
            self,
            plot_widget
    ):
        """
        设置需要导出的绘图控件
        """

        self.plot_widget = plot_widget

    def set_overlay_manager(
            self,
            overlay_manager
    ):
        """
        设置多曲线管理器
        """

        self.overlay_manager = (
            overlay_manager
        )

    # =====================================================
    # Directory
    # =====================================================

    def set_default_directory(
            self,
            directory
    ):
        """
        设置默认导出目录
        """

        if directory is None:
            self.default_directory = ""

            return

        self.default_directory = str(
            directory
        ).strip()

    @staticmethod
    def ensure_directory(filepath):
        """
        创建文件所在目录
        """

        directory = os.path.dirname(
            os.path.abspath(
                filepath
            )
        )

        if not os.path.exists(
                directory
        ):
            os.makedirs(
                directory
            )

    # =====================================================
    # File Path
    # =====================================================

    @staticmethod
    def normalize_filename(name):
        """
        清理不能用于 Windows 文件名的字符
        """

        if name is None:
            return "waveform"

        name = str(
            name
        ).strip()

        if name == "":
            return "waveform"

        invalid_chars = (
            "\\",
            "/",
            ":",
            "*",
            "?",
            "\"",
            "<",
            ">",
            "|"
        )

        for char in invalid_chars:
            name = name.replace(
                char,
                "_"
            )

        name = name.strip(
            " ."
        )

        if name == "":
            return "waveform"

        return name

    @staticmethod
    def ensure_extension(
            filepath,
            extension
    ):
        """
        自动补全文件扩展名
        """

        if filepath is None:
            return ""

        filepath = str(
            filepath
        ).strip()

        if filepath == "":
            return ""

        extension = str(
            extension
        ).strip()

        if not extension.startswith(
                "."
        ):
            extension = "." + extension

        if not filepath.lower().endswith(
                extension.lower()
        ):
            filepath += extension

        return filepath

    def build_filepath(
            self,
            filename,
            extension
    ):
        """
        根据默认目录生成完整路径
        """

        filename = self.normalize_filename(
            filename
        )

        filename = self.ensure_extension(
            filename,
            extension
        )

        if self.default_directory:
            return os.path.join(
                self.default_directory,
                filename
            )

        return os.path.abspath(
            filename
        )

    # =====================================================
    # Image Export
    # =====================================================

    def export_png(
            self,
            filepath,
            width=None
    ):
        """
        导出当前 PlotWidget 为 PNG
        """

        filepath = self.ensure_extension(
            filepath,
            ".png"
        )

        if filepath == "":
            self.exportError.emit(
                "PNG export path is empty."
            )

            return False

        if self.plot_widget is None:
            self.exportError.emit(
                "Plot widget is not available."
            )

            return False

        try:

            self.exportStarted.emit(
                filepath
            )

            self.ensure_directory(
                filepath
            )

            plot_item = (
                self.plot_widget.getPlotItem()
            )

            exporter = (
                pyqtgraph.exporters.ImageExporter(
                    plot_item
                )
            )

            if width is None:
                width = self.image_width

            try:

                width = int(
                    width
                )

            except Exception:

                width = self.image_width

            if width <= 0:
                width = self.image_width

            exporter.parameters()[
                "width"
            ] = width

            exporter.export(
                filepath
            )

            self.exportFinished.emit(
                filepath
            )

            return True

        except Exception as error:

            self.exportError.emit(
                str(error)
            )

            return False

    def export_default_png(
            self,
            filename="waveform.png",
            width=None
    ):
        """
        导出到默认目录
        """

        filepath = self.build_filepath(
            filename,
            ".png"
        )

        return self.export_png(
            filepath,
            width
        )

    # =====================================================
    # Single Curve CSV
    # =====================================================

    def export_csv(
            self,
            filepath,
            x_data=None,
            y_data=None,
            x_header="X",
            y_header="Y",
            metadata=None
    ):
        """
        导出单条波形数据为 CSV
        """

        filepath = self.ensure_extension(
            filepath,
            ".csv"
        )

        if filepath == "":
            self.exportError.emit(
                "CSV export path is empty."
            )

            return False

        if x_data is None or y_data is None:
            x_data, y_data = (
                self.get_plot_data()
            )

        x_array, y_array = (
            self.prepare_xy_data(
                x_data,
                y_data
            )
        )

        if y_array.size == 0:
            self.exportError.emit(
                "No waveform data to export."
            )

            return False

        x_header = self.normalize_header(
            x_header,
            "X"
        )

        y_header = self.normalize_header(
            y_header,
            "Y"
        )

        try:

            self.exportStarted.emit(
                filepath
            )

            self.ensure_directory(
                filepath
            )

            with open(
                    filepath,
                    "w",
                    newline="",
                    encoding=self.csv_encoding
            ) as csv_file:

                writer = csv.writer(
                    csv_file
                )

                self.write_metadata(
                    writer,
                    metadata
                )

                writer.writerow(
                    [
                        x_header,
                        y_header
                    ]
                )

                for index in range(
                        y_array.size
                ):
                    writer.writerow(
                        [
                            self.csv_value(
                                x_array[index]
                            ),
                            self.csv_value(
                                y_array[index]
                            )
                        ]
                    )

            self.exportFinished.emit(
                filepath
            )

            return True

        except Exception as error:

            self.exportError.emit(
                str(error)
            )

            return False

    def export_default_csv(
            self,
            filename="waveform.csv",
            x_data=None,
            y_data=None,
            x_header="X",
            y_header="Y",
            metadata=None
    ):
        """
        将单条波形导出到默认目录
        """

        filepath = self.build_filepath(
            filename,
            ".csv"
        )

        return self.export_csv(
            filepath=filepath,
            x_data=x_data,
            y_data=y_data,
            x_header=x_header,
            y_header=y_header,
            metadata=metadata
        )

    # =====================================================
    # Overlay CSV
    # =====================================================

    def export_overlay_csv(
            self,
            filepath,
            overlay_data=None,
            x_header="X",
            metadata=None
    ):
        """
        导出多条叠加曲线

        CSV 格式：
        X_1, Curve_1, X_2, Curve_2, ...
        """

        filepath = self.ensure_extension(
            filepath,
            ".csv"
        )

        if filepath == "":
            self.exportError.emit(
                "CSV export path is empty."
            )

            return False

        if overlay_data is None:

            if self.overlay_manager is None:
                self.exportError.emit(
                    "Overlay manager is not available."
                )

                return False

            overlay_data = (
                self.overlay_manager.get_all_data()
            )

        if not overlay_data:
            self.exportError.emit(
                "No overlay data to export."
            )

            return False

        prepared_curves = []

        for key, curve_data in overlay_data.items():

            if curve_data is None:
                continue

            x_array, y_array = (
                self.prepare_xy_data(
                    curve_data.get(
                        "x"
                    ),
                    curve_data.get(
                        "y"
                    )
                )
            )

            if y_array.size == 0:
                continue

            name = curve_data.get(
                "name",
                key
            )

            shot = curve_data.get(
                "shot"
            )

            node_path = curve_data.get(
                "node",
                ""
            )

            legend_name = self.build_curve_name(
                name,
                shot
            )

            prepared_curves.append(
                {
                    "key": key,
                    "name": legend_name,
                    "node": node_path,
                    "x": x_array,
                    "y": y_array
                }
            )

        if not prepared_curves:
            self.exportError.emit(
                "No valid overlay data to export."
            )

            return False

        maximum_size = max(
            curve["y"].size
            for curve in prepared_curves
        )

        try:

            self.exportStarted.emit(
                filepath
            )

            self.ensure_directory(
                filepath
            )

            with open(
                    filepath,
                    "w",
                    newline="",
                    encoding=self.csv_encoding
            ) as csv_file:

                writer = csv.writer(
                    csv_file
                )

                self.write_metadata(
                    writer,
                    metadata
                )

                headers = []

                for curve in prepared_curves:
                    curve_name = (
                        self.normalize_header(
                            curve["name"],
                            "Signal"
                        )
                    )

                    headers.extend(
                        [
                            "{}_{}".format(
                                x_header,
                                curve_name
                            ),
                            curve_name
                        ]
                    )

                writer.writerow(
                    headers
                )

                for row_index in range(
                        maximum_size
                ):

                    row = []

                    for curve in prepared_curves:

                        x_array = curve["x"]
                        y_array = curve["y"]

                        if row_index < y_array.size:

                            row.extend(
                                [
                                    self.csv_value(
                                        x_array[
                                            row_index
                                        ]
                                    ),
                                    self.csv_value(
                                        y_array[
                                            row_index
                                        ]
                                    )
                                ]
                            )

                        else:

                            row.extend(
                                [
                                    "",
                                    ""
                                ]
                            )

                    writer.writerow(
                        row
                    )

            self.exportFinished.emit(
                filepath
            )

            return True

        except Exception as error:

            self.exportError.emit(
                str(error)
            )

            return False

    def export_default_overlay_csv(
            self,
            filename="overlay.csv",
            overlay_data=None,
            x_header="X",
            metadata=None
    ):
        """
        将叠加曲线导出到默认目录
        """

        filepath = self.build_filepath(
            filename,
            ".csv"
        )

        return self.export_overlay_csv(
            filepath=filepath,
            overlay_data=overlay_data,
            x_header=x_header,
            metadata=metadata
        )

    # =====================================================
    # Data
    # =====================================================

    def get_plot_data(self):
        """
        从 WaveformPlotWidget 获取当前数据
        """

        if self.plot_widget is None:
            return (
                np.array(
                    [],
                    dtype=np.float64
                ),
                np.array(
                    [],
                    dtype=np.float64
                )
            )

        if hasattr(
                self.plot_widget,
                "get_data"
        ):

            try:

                return (
                    self.plot_widget.get_data()
                )

            except Exception:

                pass

        x_data = getattr(
            self.plot_widget,
            "x_data",
            None
        )

        y_data = getattr(
            self.plot_widget,
            "y_data",
            None
        )

        return self.prepare_xy_data(
            x_data,
            y_data
        )

    @staticmethod
    def convert_array(data):
        """
        将输入数据转换为一维浮点数组
        """

        if data is None:
            return np.array(
                [],
                dtype=np.float64
            )

        try:

            array = np.asarray(
                data
            )

            array = np.squeeze(
                array
            )

            if array.ndim == 0:
                array = array.reshape(
                    1
                )

            if array.ndim != 1:
                array = array.reshape(
                    -1
                )

            return array.astype(
                np.float64
            )

        except Exception:

            return np.array(
                [],
                dtype=np.float64
            )

    @classmethod
    def prepare_xy_data(
            cls,
            x_data,
            y_data
    ):
        """
        整理并过滤 X、Y 数据
        """

        y_array = cls.convert_array(
            y_data
        )

        if y_array.size == 0:
            return (
                np.array(
                    [],
                    dtype=np.float64
                ),
                np.array(
                    [],
                    dtype=np.float64
                )
            )

        x_array = cls.convert_array(
            x_data
        )

        if x_array.size == 0:
            x_array = np.arange(
                y_array.size,
                dtype=np.float64
            )

        minimum_size = min(
            x_array.size,
            y_array.size
        )

        if minimum_size <= 0:
            return (
                np.array(
                    [],
                    dtype=np.float64
                ),
                np.array(
                    [],
                    dtype=np.float64
                )
            )

        x_array = x_array[
            :minimum_size
        ]

        y_array = y_array[
            :minimum_size
        ]

        valid_mask = (
                np.isfinite(x_array) &
                np.isfinite(y_array)
        )

        return (
            x_array[valid_mask],
            y_array[valid_mask]
        )

    # =====================================================
    # Metadata
    # =====================================================

    @staticmethod
    def write_metadata(
            writer,
            metadata
    ):
        """
        将元数据写入 CSV 文件头
        """

        if not metadata:
            return

        if isinstance(
                metadata,
                dict
        ):

            for key, value in metadata.items():
                writer.writerow(
                    [
                        "# {}".format(
                            key
                        ),
                        value
                    ]
                )

            writer.writerow(
                []
            )

            return

        writer.writerow(
            [
                "# Metadata",
                str(metadata)
            ]
        )

        writer.writerow(
            []
        )

    @staticmethod
    def build_curve_name(
            name,
            shot=None
    ):
        """
        生成导出列名
        """

        if name is None:
            name = "Signal"

        name = str(
            name
        ).strip()

        if name == "":
            name = "Signal"

        if shot is not None:
            return "{}_Shot_{}".format(
                name,
                shot
            )

        return name

    @staticmethod
    def normalize_header(
            header,
            default_header
    ):
        """
        规范化 CSV 列名
        """

        if header is None:
            return default_header

        header = str(
            header
        ).strip()

        if header == "":
            return default_header

        header = header.replace(
            ",",
            "_"
        )

        header = header.replace(
            "\r",
            " "
        )

        header = header.replace(
            "\n",
            " "
        )

        return header

    @staticmethod
    def csv_value(value):
        """
        将 numpy 数值转换为 CSV 可写类型
        """

        if value is None:
            return ""

        try:

            if not np.isfinite(
                    value
            ):
                return ""

        except Exception:

            pass

        try:

            return float(
                value
            )

        except Exception:

            return str(
                value
            )

    # =====================================================
    # Configuration
    # =====================================================

    def apply_config(self, config):
        """
        应用 Config 中的导出配置
        """

        if config is None:
            return

        export_path = getattr(
            config,
            "export_path",
            ""
        )

        if export_path:
            self.set_default_directory(
                export_path
            )

        image_width = getattr(
            config,
            "export_image_width",
            None
        )

        if image_width is not None:

            try:

                image_width = int(
                    image_width
                )

                if image_width > 0:
                    self.image_width = (
                        image_width
                    )

            except Exception:

                pass
