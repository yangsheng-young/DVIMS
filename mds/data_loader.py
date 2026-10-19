# -*- coding: utf-8 -*-
"""
-------------------------------------------------
Project : NNBI_database
File    : data_loader.py
Author  :
Date    :
Description : Data Loader
-------------------------------------------------
"""

import math
import time

import numpy as np


class SignalData(object):
    """
    Signal Data
    """

    def __init__(self):
        self.tree = ""
        self.shot = 0
        self.name = ""
        self.node = ""

        self.x = None
        self.y = None

        self.xlabel = "Time"
        self.ylabel = "Value"

        self.x_unit = ""
        self.y_unit = ""

        # 兼容旧代码，unit代表Y轴单位
        self.unit = ""

        # 降频读取信息
        self.original_size = 0
        self.loaded_size = 0
        self.sample_step = 1
        self.downsampled = False

        # 性能测试信息
        self.query_time = 0.0
        self.max_points = 0
        self.query_mode = ""

        # 标定信息
        self.calibrated = False
        self.gain = None
        self.offset = None
        self.raw_node = ""
        self.gain_node = ""
        self.offset_node = ""

    def clear(self):
        self.tree = ""
        self.shot = 0
        self.name = ""
        self.node = ""

        self.x = None
        self.y = None

        self.xlabel = "Time"
        self.ylabel = "Value"

        self.x_unit = ""
        self.y_unit = ""

        self.unit = ""

        self.original_size = 0
        self.loaded_size = 0
        self.sample_step = 1
        self.downsampled = False

        self.query_time = 0.0
        self.max_points = 0
        self.query_mode = ""

        self.calibrated = False
        self.gain = None
        self.offset = None
        self.raw_node = ""
        self.gain_node = ""
        self.offset_node = ""


class DataLoader(object):
    """
    MDSplus Data Loader

    支持服务器端等间隔降频读取。

    服务器端降频的含义：
    不先把全部节点数据传输到Python后再切片，而是在MDSplus
    服务器端通过TDI下标表达式选择数据，只返回需要的采样点。

    当前第一版支持stride模式：
    根据原始点数和max_points计算等间隔采样步长。
    """

    DEFAULT_MAX_POINTS = 10000
    MIN_MAX_POINTS = 100

    def __init__(
            self,
            manager,
            downsample_enabled=True,
            max_points=DEFAULT_MAX_POINTS
    ):

        self.manager = manager

        self._downsample_enabled = True
        self._max_points = self.DEFAULT_MAX_POINTS

        self.set_downsample_enabled(
            downsample_enabled
        )

        self.set_max_points(
            max_points
        )

    # =====================================================
    # Downsample Configuration
    # =====================================================

    def set_downsample_enabled(
            self,
            enabled
    ):
        """
        设置是否启用服务器端降频。
        """

        self._downsample_enabled = bool(
            enabled
        )

    def downsample_enabled(self):

        return self._downsample_enabled

    def set_max_points(
            self,
            max_points
    ):
        """
        设置单条波形最多读取的点数。

        最小值限制为100，避免参数误设为0或负数。
        """

        try:

            max_points = int(
                max_points
            )

        except Exception:

            max_points = self.DEFAULT_MAX_POINTS

        max_points = max(
            self.MIN_MAX_POINTS,
            max_points
        )

        self._max_points = max_points

    def max_points(self):

        return self._max_points

    def set_query_options(
            self,
            downsample_enabled=None,
            max_points=None
    ):
        """
        一次设置查询参数。

        后续ParameterPanel、MDSManager和Controller可以直接调用。
        """

        if downsample_enabled is not None:
            self.set_downsample_enabled(
                downsample_enabled
            )

        if max_points is not None:
            self.set_max_points(
                max_points
            )

    def query_options(self):

        return {
            "downsample_enabled": self.downsample_enabled(),
            "max_points": self.max_points()
        }

    # =====================================================
    # Public
    # =====================================================

    def load_signal(
            self,
            node,
            downsample_enabled=None,
            max_points=None
    ):
        """
        一次性读取Signal。

        当所选节点旁边同时存在GAIN、OFFSET、RAW三个兄弟节点时，
        自动按以下关系读取真实数据：

            y = k * x + b

        其中：
            k = GAIN
            b = OFFSET
            x = RAW
            y = 当前双击查询节点的真实数据

        RAW波形仍然使用服务器端降频，因此不会为了标定而把
        全部RAW数据先传输到客户端。

        如果没有找到完整的GAIN/OFFSET/RAW结构，则保持原来的
        普通节点读取方式。
        """

        query_start_time = time.perf_counter()

        node = self.normalize_node(
            node
        )

        if node == "":
            raise RuntimeError(
                "Node is empty."
            )

        use_downsample = self.resolve_downsample_enabled(
            downsample_enabled
        )

        point_limit = self.resolve_max_points(
            max_points
        )

        signal = SignalData()

        signal.max_points = int(
            point_limit
        )

        signal.tree = self.manager.tree()
        signal.shot = self.manager.shot()

        signal.node = node

        signal.name = node.split(
            ":"
        )[-1]

        calibration = self.resolve_calibration_nodes(
            node
        )

        if calibration is not None:

            data_node = calibration[
                "raw_node"
            ]

            signal.calibrated = True
            signal.raw_node = calibration[
                "raw_node"
            ]
            signal.gain_node = calibration[
                "gain_node"
            ]
            signal.offset_node = calibration[
                "offset_node"
            ]

            signal.gain = self.read_scalar_node(
                signal.gain_node,
                "GAIN"
            )

            signal.offset = self.read_scalar_node(
                signal.offset_node,
                "OFFSET"
            )

        else:

            data_node = node

        original_size = self.read_original_size(
            data_node
        )

        signal.original_size = original_size

        sample_step = self.calculate_sample_step(
            original_size=original_size,
            max_points=point_limit,
            enabled=use_downsample
        )

        signal.sample_step = sample_step
        signal.downsampled = (
                sample_step > 1
        )

        if use_downsample:
            signal.query_mode = "Stride"
        else:
            signal.query_mode = "Full"

        if signal.calibrated:

            y_data = self.read_calibrated_data(
                raw_node=signal.raw_node,
                gain=signal.gain,
                offset=signal.offset,
                original_size=original_size,
                sample_step=sample_step
            )

        elif signal.downsampled:

            y_data = self.read_downsampled_data(
                node=node,
                original_size=original_size,
                sample_step=sample_step
            )

        else:

            y_data = self.manager.get_data(
                node
            )

        signal.y = self.to_numpy(
            y_data
        ).reshape(
            -1
        )

        if signal.y.size == 0:
            raise RuntimeError(
                "Node contains no data: {}".format(
                    node
                )
            )

        try:

            if signal.downsampled:

                x_data = self.read_downsampled_dimension(
                    node=data_node,
                    original_size=original_size,
                    sample_step=sample_step
                )

            else:

                x_data = self.manager.get_dimension(
                    data_node
                )

            signal.x = self.to_numpy(
                x_data
            ).reshape(
                -1
            )

        except Exception:

            signal.x = self.create_fallback_dimension(
                original_size=original_size,
                loaded_size=signal.y.size,
                sample_step=sample_step
            )

        # DIM_OF成功但返回长度异常时，也使用备用索引轴，
        # 避免把正常Y数据截断成1个点。
        if (
                signal.y.size > 1
                and
                signal.x.size <= 1
        ):
            signal.x = self.create_fallback_dimension(
                original_size=original_size,
                loaded_size=signal.y.size,
                sample_step=sample_step
            )

        minimum_size = min(
            signal.x.size,
            signal.y.size
        )

        if minimum_size <= 0:
            raise RuntimeError(
                "Invalid signal dimension: {}".format(
                    node
                )
            )

        signal.x = signal.x[
            :minimum_size
        ]

        signal.y = signal.y[
            :minimum_size
        ]

        signal.loaded_size = int(
            minimum_size
        )

        if signal.original_size <= 0:
            signal.original_size = signal.loaded_size
            signal.sample_step = 1
            signal.downsampled = False

        self.load_units(
            signal,
            node,
            dimension_node=data_node
        )

        query_end_time = time.perf_counter()

        signal.query_time = (
                query_end_time
                - query_start_time
        )

        return signal

    # =====================================================
    # Calibration
    # =====================================================

    def resolve_calibration_nodes(
            self,
            node
    ):
        """
        根据当前真实节点路径推导同级GAIN/OFFSET/RAW节点。

        例如：
            \\TOP.SIG_BIAS_I:BIAS_I
        会优先检查：
            \\TOP.SIG_BIAS_I:GAIN
            \\TOP.SIG_BIAS_I:OFFSET
            \\TOP.SIG_BIAS_I:RAW

        同时兼容成员节点(:)和结构子节点(.)。
        """

        node = self.normalize_node(
            node
        )

        if node == "":
            return None

        leaf_name = self.node_leaf_name(
            node
        ).upper()

        if leaf_name in (
                "GAIN",
                "OFFSET",
                "RAW"
        ):
            return None

        parent_path = self.node_parent_path(
            node
        )

        if parent_path == "":
            return None

        preferred_separator = self.node_leaf_separator(
            node
        )

        separators = []

        for separator in (
                preferred_separator,
                ":",
                "."
        ):

            if (
                    separator
                    and
                    separator not in separators
            ):
                separators.append(
                    separator
                )

        for separator in separators:

            gain_node = "{}{}GAIN".format(
                parent_path,
                separator
            )

            offset_node = "{}{}OFFSET".format(
                parent_path,
                separator
            )

            raw_node = "{}{}RAW".format(
                parent_path,
                separator
            )

            if (
                    self.node_exists_by_nci(
                        gain_node
                    )
                    and
                    self.node_exists_by_nci(
                        offset_node
                    )
                    and
                    self.node_exists_by_nci(
                        raw_node
                    )
            ):
                return {
                    "gain_node": gain_node,
                    "offset_node": offset_node,
                    "raw_node": raw_node
                }

        return None

    def node_exists_by_nci(
            self,
            node
    ):
        """
        只通过GETNCI检查节点是否存在，不读取节点数据。
        """

        expression = 'GETNCI({}, "NID_NUMBER")'.format(
            self.quote_tdi_path(
                node
            )
        )

        try:

            result = self.manager.get(
                expression
            )

            value = self.extract_data(
                result
            )

            array = np.asarray(
                value
            ).reshape(
                -1
            )

            return array.size > 0

        except Exception:

            return False

    def read_scalar_node(
            self,
            node,
            title
    ):
        """
        读取GAIN/OFFSET标量。
        """

        result = self.manager.get(
            "DATA({})".format(
                node
            )
        )

        value = self.extract_data(
            result
        )

        array = np.asarray(
            value
        ).reshape(
            -1
        )

        if array.size == 0:
            raise RuntimeError(
                "{} node contains no data: {}".format(
                    title,
                    node
                )
            )

        try:

            return float(
                array[0]
            )

        except Exception:

            raise RuntimeError(
                "{} is not a numeric scalar: {}".format(
                    title,
                    node
                )
            )

    def read_calibrated_data(
            self,
            raw_node,
            gain,
            offset,
            original_size,
            sample_step
    ):
        """
        在MDSplus服务器端读取RAW并完成y=GAIN*RAW+OFFSET。

        即使关闭降频，也是在服务器端完成线性换算后再把结果
        返回Python客户端。
        """

        raw_expression = "DATA({})".format(
            raw_node
        )

        if (
                int(
                    sample_step
                ) > 1
                and
                int(
                    original_size
                ) > 0
        ):
            raw_expression = self.build_slice_expression(
                raw_expression,
                original_size,
                sample_step
            )

        expression = "(({}) * ({!r})) + ({!r})".format(
            raw_expression,
            float(
                gain
            ),
            float(
                offset
            )
        )

        return self.read_expression_data(
            expression
        )

    @staticmethod
    def node_leaf_separator(
            node
    ):

        text = str(
            node
        ).strip()

        colon_index = text.rfind(
            ":"
        )

        dot_index = text.rfind(
            "."
        )

        index = max(
            colon_index,
            dot_index
        )

        if index < 0:
            return ""

        return text[
            index
        ]

    @staticmethod
    def node_parent_path(
            node
    ):

        text = str(
            node
        ).strip()

        colon_index = text.rfind(
            ":"
        )

        dot_index = text.rfind(
            "."
        )

        index = max(
            colon_index,
            dot_index
        )

        if index <= 0:
            return ""

        return text[
            :index
        ]

    @staticmethod
    def node_leaf_name(
            node
    ):

        text = str(
            node
        ).strip()

        colon_index = text.rfind(
            ":"
        )

        dot_index = text.rfind(
            "."
        )

        index = max(
            colon_index,
            dot_index
        )

        if index < 0:
            return text

        return text[
            index + 1:
        ]

    @staticmethod
    def quote_tdi_path(
            path
    ):

        text = str(
            path
        )

        text = text.replace(
            "\\",
            "\\\\"
        )

        text = text.replace(
            '"',
            '\\"'
        )

        return '"{}"'.format(
            text
        )

    # =====================================================
    # Server-side Downsample
    # =====================================================

    def read_original_size(
            self,
            node
    ):
        """
        在服务器端读取节点原始点数。

        SIZE(DATA(node))只返回一个标量，不传输完整波形。
        """

        expression = "SIZE(DATA({}))".format(
            node
        )

        try:

            result = self.manager.get(
                expression
            )

            value = self.extract_data(
                result
            )

            array = np.asarray(
                value
            ).reshape(
                -1
            )

            if array.size == 0:
                return 0

            size = int(
                array[0]
            )

            return max(
                0,
                size
            )

        except Exception:

            return 0

    @staticmethod
    def calculate_sample_step(
            original_size,
            max_points,
            enabled=True
    ):
        """
        根据原始点数计算等间隔采样步长。

        使用ceil保证返回点数不会明显超过max_points。
        """

        try:
            original_size = int(
                original_size
            )
        except Exception:
            original_size = 0

        try:
            max_points = int(
                max_points
            )
        except Exception:
            max_points = DataLoader.DEFAULT_MAX_POINTS

        if not enabled:
            return 1

        if original_size <= 0:
            return 1

        if max_points <= 0:
            return 1

        if original_size <= max_points:
            return 1

        return max(
            1,
            int(
                math.ceil(
                    float(original_size)
                    /
                    float(max_points)
                )
            )
        )

    def read_downsampled_data(
            self,
            node,
            original_size,
            sample_step
    ):
        """
        在MDSplus服务器端读取降频后的Y数据。
        """

        expression = self.build_slice_expression(
            "DATA({})".format(
                node
            ),
            original_size,
            sample_step
        )

        return self.read_expression_data(
            expression
        )

    def read_downsampled_dimension(
            self,
            node,
            original_size,
            sample_step
    ):
        """
        在MDSplus服务器端读取与Y数据相同步长的X维度。
        """

        expression = self.build_slice_expression(
            "DIM_OF({})".format(
                node
            ),
            original_size,
            sample_step
        )

        return self.read_expression_data(
            expression
        )

    @staticmethod
    def build_slice_expression(
            base_expression,
            original_size,
            sample_step
    ):
        """
        构造TDI数组下标表达式。

        示例：
        DATA(\\TOP:SIGNAL)[0:999999:100]
        DIM_OF(\\TOP:SIGNAL)[0:999999:100]
        """

        original_size = int(
            original_size
        )

        sample_step = max(
            1,
            int(
                sample_step
            )
        )

        if original_size <= 0:
            raise RuntimeError(
                "Invalid original signal size."
            )

        last_index = original_size - 1

        return "{}[0:{}:{}]".format(
            base_expression,
            last_index,
            sample_step
        )

    def read_expression_data(
            self,
            expression
    ):
        """
        执行TDI表达式并返回其中的数据。
        """

        result = self.manager.get(
            expression
        )

        return self.extract_data(
            result
        )

    @staticmethod
    def extract_data(
            result
    ):
        """
        兼容MDSplus对象、numpy数组和普通Python标量。
        """

        if result is None:
            return None

        try:

            return result.data()

        except Exception:

            return result

    @staticmethod
    def create_fallback_dimension(
            original_size,
            loaded_size,
            sample_step
    ):
        """
        DIM_OF读取失败时生成索引X轴。

        降频状态下保留原始索引位置，例如：
        0, 100, 200, 300...
        """

        try:
            loaded_size = int(
                loaded_size
            )
        except Exception:
            loaded_size = 0

        try:
            sample_step = max(
                1,
                int(
                    sample_step
                )
            )
        except Exception:
            sample_step = 1

        if loaded_size <= 0:
            return np.array(
                [],
                dtype=np.float64
            )

        x_data = np.arange(
            loaded_size,
            dtype=np.float64
        ) * float(
            sample_step
        )

        try:
            original_size = int(
                original_size
            )
        except Exception:
            original_size = 0

        if original_size > 0:
            x_data = x_data[
                x_data < original_size
                ]

        return x_data

    # =====================================================
    # Query Option Resolution
    # =====================================================

    def resolve_downsample_enabled(
            self,
            value
    ):

        if value is None:
            return self.downsample_enabled()

        return bool(
            value
        )

    def resolve_max_points(
            self,
            value
    ):

        if value is None:
            return self.max_points()

        try:

            value = int(
                value
            )

        except Exception:

            value = self.max_points()

        return max(
            self.MIN_MAX_POINTS,
            value
        )

    @staticmethod
    def normalize_node(
            node
    ):

        if node is None:
            return ""

        return str(
            node
        ).strip()

    # =====================================================
    # Units
    # =====================================================

    def load_units(
            self,
            signal,
            node,
            dimension_node=None
    ):
        """
        读取X轴和Y轴单位
        """

        if dimension_node is None:
            dimension_node = node

        signal.x_unit = self.read_unit(
            "UNITS(DIM_OF({}))".format(
                dimension_node
            )
        )

        signal.y_unit = self.read_unit(
            "UNITS({})".format(
                node
            )
        )

        # 保留旧字段兼容已有代码
        signal.unit = signal.y_unit

    def read_unit(
            self,
            expression
    ):
        """
        安全读取单位字符串
        """

        try:

            result = self.manager.get(
                expression
            )

            value = self.extract_data(
                result
            )

            if value is None:
                return ""

            if isinstance(
                    value,
                    bytes
            ):

                try:

                    return value.decode(
                        "utf-8"
                    ).strip()

                except UnicodeDecodeError:

                    return value.decode(
                        "latin-1",
                        errors="ignore"
                    ).strip()

            return str(
                value
            ).strip()

        except Exception:

            return ""

    # =====================================================
    # Utility
    # =====================================================

    def to_numpy(
            self,
            data
    ):

        if data is None:
            return np.array([])

        if isinstance(
                data,
                np.ndarray
        ):
            return data

        try:

            return np.asarray(
                data
            )

        except Exception:

            return np.array([])

    # =====================================================
    # Information
    # =====================================================

    def signal_length(
            self,
            signal
    ):

        if signal.y is None:
            return 0

        return len(
            signal.y
        )

    def is_empty(
            self,
            signal
    ):

        return self.signal_length(
            signal
        ) == 0

    # =====================================================
    # Reserved Interface
    # =====================================================

    def load_history(
            self,
            tree,
            shot_list,
            node
    ):
        """
        多炮号读取
        """
        pass
