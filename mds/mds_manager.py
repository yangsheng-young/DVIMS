# -*- coding: utf-8 -*-

"""
-------------------------------------------------
Project : NNBI_database
File    : mds_manager.py
Author  :
Date    :
Description : MDSplus Manager
-------------------------------------------------
"""
from mds.compare_data import (
    CompareRequest,
    CompareResult,
)

from mds.mds_connection import MDSConnection
from mds.tree_loader import TreeLoader
from mds.data_loader import DataLoader

import numpy as np


class MDSManager(object):
    """
    MDSplus数据库管理器

    整个工程唯一的MDSplus数据访问入口。
    """

    def __init__(
            self,
            timeout=5,
            downsample_enabled=True,
            max_points=10000
    ):

        self._timeout = 5

        self.set_timeout(
            timeout
        )

        self.connection = MDSConnection(
            timeout=self._timeout
        )

        self.current_tree = ""
        self.current_shot = None
        self._current_node = ""

        self.last_error = ""

        self.tree_loader = TreeLoader(
            self.connection
        )

        self.data_loader = DataLoader(
            self,
            downsample_enabled=downsample_enabled,
            max_points=max_points
        )

    # =====================================================
    # Timeout
    # =====================================================

    def set_timeout(
            self,
            timeout
    ):
        """
        设置MDSplus操作超时，单位秒
        """

        try:
            timeout = int(timeout)
        except Exception:
            timeout = 5

        if timeout < 1:
            timeout = 1

        self._timeout = timeout

        connection = getattr(
            self,
            "connection",
            None
        )

        if connection is not None:
            connection.set_timeout(
                timeout
            )

    def timeout(self):
        """
        返回操作超时，单位秒
        """

        return self._timeout

    def timeout_ms(self):
        """
        返回操作超时，单位毫秒
        """

        return self._timeout * 1000

    def invalidate_connection(
            self,
            reason=""
    ):
        """
        将当前连接标记为失效
        """

        self.last_error = str(
            reason
        )

        self.connection.invalidate(
            reason
        )

    # =====================================================
    # Data Query Options
    # =====================================================

    def set_downsample_enabled(
            self,
            enabled
    ):
        """
        设置普通查询和多炮对比的默认降频状态。
        """

        self.data_loader.set_downsample_enabled(
            enabled
        )

    def downsample_enabled(self):

        return self.data_loader.downsample_enabled()

    def set_max_points(
            self,
            max_points
    ):
        """
        设置单条波形默认最大读取点数。
        """

        self.data_loader.set_max_points(
            max_points
        )

    def max_points(self):

        return self.data_loader.max_points()

    def set_query_options(
            self,
            downsample_enabled=None,
            max_points=None
    ):
        """
        设置统一的数据查询参数。
        """

        self.data_loader.set_query_options(
            downsample_enabled=downsample_enabled,
            max_points=max_points
        )

    def query_options(self):
        """
        返回当前默认查询参数的副本。
        """

        return dict(
            self.data_loader.query_options()
        )

    # =====================================================
    # Connection
    # =====================================================

    def connect(
            self,
            host,
            port="8000"
    ):
        """
        连接MDSplus服务器
        """

        self.last_error = ""

        self.connection.set_timeout(
            self._timeout
        )

        try:

            result = self.connection.connect(
                host,
                port
            )

            if not result:
                self.last_error = (
                        self.connection.last_error()
                        or
                        "Failed to connect MDSplus server."
                )

            return bool(
                result
            )

        except Exception as error:

            self.last_error = str(
                error
            )

            return False

    def disconnect(self):
        """
        断开MDSplus服务器
        """

        if self.is_tree_open():

            try:

                self.close_tree()

            except Exception:

                pass

        self._current_node = ""
        self.current_tree = ""
        self.current_shot = None

        self.connection.disconnect()

    def is_connected(self):
        """
        判断服务器是否连接
        """

        return self.connection.is_connected()

    # =====================================================
    # Tree
    # =====================================================

    def switch_shot(
            self,
            tree,
            shot
    ):
        """
        切换Tree炮号。

        返回字典：
        success：新炮号是否打开成功
        restored：失败后是否成功恢复旧Tree
        old_tree：原Tree
        old_shot：原炮号
        tree：当前Tree
        shot：当前炮号
        error：新炮号打开错误
        restore_error：旧Tree恢复错误
        """

        result = {
            "success": False,
            "restored": False,
            "old_tree": self.current_tree,
            "old_shot": self.current_shot,
            "tree": "",
            "shot": None,
            "error": "",
            "restore_error": ""
        }

        old_tree = self.current_tree
        old_shot = self.current_shot

        if self.is_tree_open():

            try:
                self.close_tree()
            except Exception as error:

                result["error"] = str(
                    error
                )

                return result

        opened = self.open_tree(
            tree,
            shot
        )

        if opened:
            result["success"] = True
            result["tree"] = self.current_tree
            result["shot"] = self.current_shot

            return result

        # 保存新炮号打开失败信息，避免恢复旧Tree时被覆盖
        open_error = (
                self.last_error
                or
                "Failed to open shot {}.".format(
                    shot
                )
        )

        result["error"] = open_error

        if (
                old_tree
                and
                old_shot is not None
        ):

            restored = self.open_tree(
                old_tree,
                old_shot
            )

            if restored:

                result["restored"] = True
                result["tree"] = self.current_tree
                result["shot"] = self.current_shot

                # last_error仍保留新炮号失败原因
                self.last_error = open_error

            else:

                result["restore_error"] = (
                        self.last_error
                        or
                        "Failed to restore previous Tree."
                )

                self.current_tree = ""
                self.current_shot = None
                self._current_node = ""

        return result

    def open_tree(
            self,
            tree,
            shot
    ):
        """
        打开Tree
        """

        self.last_error = ""

        if not self.is_connected():
            self.last_error = (
                "MDSplus server is not connected."
            )

            return False

        tree = str(
            tree
        ).strip()

        if tree == "":
            self.last_error = (
                "Tree name is empty."
            )

            return False

        try:

            shot = int(
                shot
            )

        except Exception:

            self.last_error = (
                "Invalid shot number."
            )

            return False

        try:

            self.connection.open_tree(
                tree,
                shot
            )

            self.current_tree = tree
            self.current_shot = shot
            self._current_node = ""

            return True

        except Exception as error:

            self.last_error = str(
                error
            )

            self.current_tree = ""
            self.current_shot = None
            self._current_node = ""

            return False

    def close_tree(self):
        """
        关闭当前Tree
        """

        if not self.is_tree_open():
            return False

        try:

            self.connection.close_tree(
                self.current_tree,
                self.current_shot
            )

        finally:

            self.current_tree = ""
            self.current_shot = None
            self._current_node = ""

        return True

    def reopen_tree(self):
        """
        重新打开当前Tree
        """

        if not self.is_tree_open():
            return False

        tree = self.current_tree
        shot = self.current_shot

        self.close_tree()

        return self.open_tree(
            tree,
            shot
        )

    def is_tree_open(self):
        """
        判断Tree是否打开
        """

        return (
                self.current_tree != ""
                and
                self.current_shot is not None
        )

    def load_tree(
            self,
            stop_checker=None
    ):
        """
        读取当前Tree结构

        stop_checker：
        可调用对象，返回True时终止递归读取。
        """

        self.last_error = ""

        if not self.is_connected():
            raise RuntimeError(
                "MDSplus server is not connected."
            )

        if not self.is_tree_open():
            raise RuntimeError(
                "MDSplus Tree is not open."
            )

        try:

            return self.tree_loader.load(
                stop_checker=stop_checker
            )

        except Exception as error:

            self.last_error = str(
                error
            )

            raise

    # =====================================================
    # Current Information
    # =====================================================

    def tree(self):
        """
        返回当前Tree名称
        """

        return self.current_tree

    def shot(self):
        """
        返回当前炮号
        """

        return self.current_shot

    def set_current_node(
            self,
            node
    ):
        """
        设置当前节点
        """

        if node is None:

            self._current_node = ""

        else:

            self._current_node = str(
                node
            ).strip()

    def current_node(self):
        """
        返回当前节点
        """

        return self._current_node

    # =====================================================
    # TDI
    # =====================================================

    def get(
            self,
            expression
    ):
        """
        执行MDSplus表达式并返回结果
        """

        if not self.is_connected():
            raise RuntimeError(
                "MDSplus server is not connected."
            )

        return self.connection.get(
            expression
        )

    def execute(
            self,
            expression
    ):
        """
        执行MDSplus表达式
        """

        if not self.is_connected():
            raise RuntimeError(
                "MDSplus server is not connected."
            )

        return self.connection.execute(
            expression
        )

    # =====================================================
    # Data
    # =====================================================

    def get_data(
            self,
            node
    ):
        """
        读取节点数据
        """

        self.validate_node(
            node
        )

        return self.connection.get_data(
            node
        )

    def get_dimension(
            self,
            node
    ):
        """
        读取节点维度
        """

        self.validate_node(
            node
        )

        return self.connection.get_dimension(
            node
        )

    def get_signal(
            self,
            node
    ):
        """
        读取原始X、Y数据
        """

        self.validate_node(
            node
        )

        x_data = self.get_dimension(
            node
        )

        y_data = self.get_data(
            node
        )

        return (
            x_data,
            y_data
        )

    # =====================================================
    # Current Shot Parameters
    # =====================================================

    def read_parameter_value(
            self,
            expression,
            value_type="number"
    ):
        """
        读取当前Tree和Shot中的一个参数。

        expression可以是节点路径，也可以是完整TDI表达式。
        数组型结果默认取最后一个有效值。
        """

        expression = str(
            expression
        ).strip()

        if expression == "":
            return None

        result = self.get(
            expression
        )

        try:
            value = result.data()
        except Exception:
            value = result

        if value is None:
            return None

        if value_type == "text":

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

            try:
                array = np.asarray(
                    value
                ).reshape(
                    -1
                )

                if array.size > 0:
                    value = array[-1]
            except Exception:
                pass

            return str(
                value
            ).strip()

        try:

            array = np.asarray(
                value
            ).reshape(
                -1
            )

            if array.size == 0:
                return None

            if np.issubdtype(
                    array.dtype,
                    np.number
            ):

                finite = array[
                    np.isfinite(
                        array
                    )
                ]

                if finite.size == 0:
                    return None

                value = finite[-1]

            else:

                value = array[-1]

        except Exception:

            pass

        try:
            return float(
                value
            )
        except Exception:
            return value

    def load_shot_parameters(
            self,
            parameter_definitions
    ):
        """
        批量读取当前炮号的高压、电流等概要参数。
        """

        if not self.is_connected():
            raise RuntimeError(
                "MDSplus server is not connected."
            )

        if not self.is_tree_open():
            raise RuntimeError(
                "MDSplus tree is not open."
            )

        result = {
            "tree": self.tree(),
            "shot": self.shot(),
            "high_voltage": {},
            "current": {},
            "errors": {}
        }

        for name, definition in (
                parameter_definitions
                or
                {}
        ).items():

            definition = definition or {}

            expression = str(
                definition.get(
                    "expression",
                    ""
                )
            ).strip()

            group = str(
                definition.get(
                    "group",
                    ""
                )
            ).strip()

            unit = str(
                definition.get(
                    "unit",
                    ""
                )
            ).strip()

            value_type = str(
                definition.get(
                    "value_type",
                    "number"
                )
            ).strip().lower()

            item = {
                "value": None,
                "unit": unit,
                "expression": expression,
                "configured": expression != ""
            }

            if expression != "":

                try:

                    item["value"] = self.read_parameter_value(
                        expression,
                        value_type=value_type
                    )

                except Exception as error:

                    result["errors"][
                        name
                    ] = str(
                        error
                    )

            if group in result:
                result[group][
                    name
                ] = item

        return result

    # =====================================================
    # Multi-shot Compare
    # =====================================================

    def capture_tree_state(self):
        """
        保存当前数据库Tree状态。

        多炮号读取完成后，用于恢复进入对比任务前的Tree和Shot。
        """

        return {
            "tree": self.current_tree,
            "shot": self.current_shot,
            "node": self._current_node,
            "tree_open": self.is_tree_open()
        }

    def restore_tree_state(
            self,
            state
    ):
        """
        恢复数据库Tree状态。

        Parameters
        ----------
        state : dict
            capture_tree_state()返回的状态。

        Returns
        -------
        tuple
            (是否恢复成功, 错误信息)
        """

        if not isinstance(
                state,
                dict
        ):
            return (
                False,
                "Invalid Tree state."
            )

        old_tree = str(
            state.get(
                "tree",
                ""
            )
        ).strip()

        old_shot = state.get(
            "shot"
        )

        old_node = str(
            state.get(
                "node",
                ""
            )
        ).strip()

        was_open = bool(
            state.get(
                "tree_open",
                False
            )
        )

        try:

            if self.is_tree_open():
                self.close_tree()

            if not was_open:
                self._current_node = ""

                return (
                    True,
                    ""
                )

            if old_tree == "":
                return (
                    False,
                    "Previous Tree name is empty."
                )

            if old_shot is None:
                return (
                    False,
                    "Previous shot is invalid."
                )

            opened = self.open_tree(
                old_tree,
                old_shot
            )

            if not opened:
                return (
                    False,
                    self.last_error
                    or
                    "Failed to restore previous Tree."
                )

            self._current_node = old_node

            return (
                True,
                ""
            )

        except Exception as error:

            return (
                False,
                str(error)
            )

    def prepare_compare_shot(
            self,
            tree,
            shot
    ):
        """
        为多炮号任务打开指定炮号。

        本函数只负责切换到目标炮号，不恢复原Tree。
        原Tree应在整个批量任务结束后统一恢复。
        """

        self.last_error = ""

        if not self.is_connected():
            self.last_error = (
                "MDSplus server is not connected."
            )

            return False

        tree = str(
            tree
        ).strip()

        if tree == "":
            self.last_error = (
                "Tree name is empty."
            )

            return False

        try:

            shot = int(
                shot
            )

        except Exception:

            self.last_error = (
                "Invalid shot number."
            )

            return False

        if (
                self.is_tree_open()
                and
                self.current_tree == tree
                and
                self.current_shot == shot
        ):
            return True

        if self.is_tree_open():

            try:

                self.close_tree()

            except Exception as error:

                self.last_error = str(
                    error
                )

                return False

        return self.open_tree(
            tree,
            shot
        )

    def load_compare_signal(
            self,
            tree,
            shot,
            node,
            downsample_enabled=None,
            max_points=None
    ):
        """
        读取指定Tree、Shot和Node的SignalData。

        注意：
        本函数是同步数据库接口，只能由后台Worker调用，
        不得由主界面线程直接调用。
        """

        node = self.normalize_node(
            node
        )

        if node == "":
            raise RuntimeError(
                "Node is empty."
            )

        opened = self.prepare_compare_shot(
            tree,
            shot
        )

        if not opened:
            raise RuntimeError(
                self.last_error
                or
                "Failed to open shot {}.".format(
                    shot
                )
            )

        signal_data = self.load_signal(
            node,
            downsample_enabled=downsample_enabled,
            max_points=max_points
        )

        # 明确写入本次读取信息
        signal_data.tree = str(
            tree
        ).strip()

        signal_data.shot = int(
            shot
        )

        signal_data.node = node

        return signal_data

    def load_signal(
            self,
            node=None,
            downsample_enabled=None,
            max_points=None
    ):
        """
        统一读取SignalData。

        所有数据库读取由DataWorker调用本函数完成。
        不再提前调用is_signal()读取数据。
        """

        self.last_error = ""

        if not self.is_connected():
            raise RuntimeError(
                "MDSplus server is not connected."
            )

        if not self.is_tree_open():
            raise RuntimeError(
                "MDSplus Tree is not open."
            )

        if node is None:
            node = self.current_node()

        node = self.normalize_node(
            node
        )

        if node == "":
            raise RuntimeError(
                "Node is empty."
            )

        try:

            signal_data = self.data_loader.load_signal(
                node,
                downsample_enabled=downsample_enabled,
                max_points=max_points
            )

            if signal_data is None:
                raise RuntimeError(
                    "Signal loading returned no data."
                )

            if self.data_loader.is_empty(
                    signal_data
            ):
                raise RuntimeError(
                    "Signal data is empty: {}".format(
                        node
                    )
                )

            self.set_current_node(
                node
            )

            return signal_data

        except Exception as error:

            self.last_error = str(
                error
            )

            raise

    # =====================================================
    # Node
    # =====================================================

    def get_node(
            self,
            node
    ):
        """
        获取节点对象
        """

        self.validate_node(
            node
        )

        return self.connection.get_node(
            node
        )

    def is_signal(
            self,
            node
    ):
        """
        判断节点是否为Signal节点
        """

        node = self.normalize_node(
            node
        )

        if node == "":
            return False

        if not self.is_tree_open():
            return False

        try:

            self.get_dimension(
                node
            )

            self.get_data(
                node
            )

            return True

        except Exception:

            return False

    def node_exists(
            self,
            node
    ):
        """
        判断节点是否存在
        """

        node = self.normalize_node(
            node
        )

        if node == "":
            return False

        try:

            self.get(
                node
            )

            return True

        except Exception:

            return False

    # =====================================================
    # Validation
    # =====================================================

    @staticmethod
    def normalize_node(
            node
    ):
        """
        规范化节点路径
        """

        if node is None:
            return ""

        return str(
            node
        ).strip()

    def validate_node(
            self,
            node
    ):
        """
        校验节点读取条件
        """

        if not self.is_connected():
            raise RuntimeError(
                "MDSplus server is not connected."
            )

        if not self.is_tree_open():
            raise RuntimeError(
                "MDSplus Tree is not open."
            )

        node = self.normalize_node(
            node
        )

        if node == "":
            raise RuntimeError(
                "Node is empty."
            )

        return node

    # =====================================================
    # Server
    # =====================================================

    def server(self):
        """
        返回服务器地址
        """

        return self.connection.server()

    def port(self):
        """
        返回服务器端口
        """

        return self.connection.port()

    def address(self):
        """
        返回完整服务器地址
        """

        return self.connection.address()

    # =====================================================
    # Ping
    # =====================================================

    def ping(self):
        """
        测试服务器连接
        """

        return self.connection.ping()
