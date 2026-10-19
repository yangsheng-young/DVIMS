# -*- coding: utf-8 -*-

"""
-------------------------------------------------
Project : NNBI_database
File    : mds_connection.py
Author  :
Date    :
Description : MDSplus Connection
-------------------------------------------------
"""

import sys

# MDSplus安装目录
sys.path.append(
    r"C:\Program Files\MDSplus\python"
)

from MDSplus import Connection


class MDSConnection(object):
    """
    MDSplus Connection

    timeout单位：秒。

    注意：
    当前MDSplus Connection接口没有直接暴露单次get调用的
    Python级timeout参数，因此timeout主要由上层Worker负责监控。
    """

    def __init__(
            self,
            timeout=5
    ):

        self._connection = None

        self._host = ""
        self._port = ""

        self._connected = False
        self._invalid = False

        self._timeout = 5
        self._last_error = ""

        self.set_timeout(
            timeout
        )

    # =====================================================
    # Timeout
    # =====================================================

    def set_timeout(
            self,
            timeout
    ):
        """
        设置操作超时时间，单位秒
        """

        try:
            timeout = int(timeout)
        except Exception:
            timeout = 5

        if timeout < 1:
            timeout = 1

        self._timeout = timeout

    def timeout(self):
        """
        返回超时时间，单位秒
        """

        return self._timeout

    def timeout_ms(self):
        """
        返回超时时间，单位毫秒
        """

        return self._timeout * 1000

    # =====================================================
    # Connect
    # =====================================================

    def connect(
            self,
            host,
            port="8000"
    ):
        """
        连接MDSplus服务器
        """

        self.disconnect()

        self._host = str(
            host
        ).strip()

        self._port = str(
            port
        ).strip()

        self._last_error = ""
        self._invalid = False

        if self._host == "":
            self._last_error = (
                "MDSplus host is empty."
            )

            return False

        if self._port == "":
            self._last_error = (
                "MDSplus port is empty."
            )

            return False

        address = "{}:{}".format(
            self._host,
            self._port
        )

        try:

            self._connection = Connection(
                address
            )

            self._connection.get(
                "1"
            )

            self._connected = True
            self._invalid = False

            return True

        except Exception as error:

            self._last_error = str(
                error
            )

            self._connection = None
            self._connected = False
            self._invalid = False

            return False

    # =====================================================
    # Disconnect
    # =====================================================

    def disconnect(self):
        """
        断开连接
        """

        self._connection = None

        self._connected = False
        self._invalid = False

    def invalidate(
            self,
            reason=""
    ):
        """
        将当前连接标记为不可继续使用

        Worker发生超时后调用此接口。
        """

        self._invalid = True

        if reason:
            self._last_error = str(
                reason
            )

    def is_invalid(self):
        """
        返回连接是否已经失效
        """

        return self._invalid

    # =====================================================
    # Status
    # =====================================================

    def is_connected(self):
        """
        判断连接是否可用
        """

        return (
                self._connected
                and
                self._connection is not None
                and
                not self._invalid
        )

    def connection(self):

        return self._connection

    def address(self):

        if self._host == "":
            return ""

        return "{}:{}".format(
            self._host,
            self._port
        )

    def last_error(self):

        return self._last_error

    # =====================================================
    # Validation
    # =====================================================

    def validate_connection(self):
        """
        校验连接状态
        """

        if self._invalid:
            raise RuntimeError(
                "MDSplus connection is invalid. "
                "Please reconnect."
            )

        if not self._connected:
            raise RuntimeError(
                "MDSplus is not connected."
            )

        if self._connection is None:
            raise RuntimeError(
                "MDSplus connection object is empty."
            )

    # =====================================================
    # Tree
    # =====================================================

    def open_tree(
            self,
            tree,
            shot
    ):
        """
        打开Tree
        """

        self.validate_connection()

        self._connection.openTree(
            tree,
            int(shot)
        )

    def close_tree(
            self,
            tree,
            shot
    ):
        """
        关闭Tree
        """

        if self._connection is None:
            return

        try:

            self._connection.closeTree(
                tree,
                int(shot)
            )

        except Exception:

            pass

    # =====================================================
    # TDI
    # =====================================================

    def get(
            self,
            expression
    ):
        """
        执行TDI表达式
        """

        self.validate_connection()

        try:

            return self._connection.get(
                expression
            )

        except Exception as error:

            self._last_error = str(
                error
            )

            raise

    def execute(
            self,
            expression
    ):

        return self.get(
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

        data = self.get(
            node
        )

        return data.data()

    def get_dimension(
            self,
            node
    ):
        """
        读取节点维度
        """

        dim = self.get(
            "DIM_OF({})".format(
                node
            )
        )

        return dim.data()

    # =====================================================
    # Node
    # =====================================================

    def get_node(
            self,
            node
    ):

        return self.get(
            node
        )

    # =====================================================
    # Test
    # =====================================================

    def ping(self):
        """
        测试连接
        """

        if not self.is_connected():
            return False

        try:

            self.get(
                "1"
            )

            return True

        except Exception:

            self.invalidate(
                "MDSplus ping failed."
            )

            return False

    # =====================================================
    # Info
    # =====================================================

    def server(self):

        return self._host

    def port(self):

        return self._port

    # =====================================================
    # Reset
    # =====================================================

    def reset(self):

        self.disconnect()

        self._host = ""
        self._port = ""
        self._last_error = ""

    # =====================================================
    # Destructor
    # =====================================================

    def __del__(self):

        self.disconnect()
