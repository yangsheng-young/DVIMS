# -*- coding: utf-8 -*-

"""
==========================================================
Project : NNBI_database
File    : compare_data.py
Author  :
Date    :
Description : Multi-shot comparison data model
==========================================================
"""


class CompareRequest(object):
    """
    多炮号对比请求。

    保存一次多炮号对比任务所需要的输入参数。
    """

    def __init__(
            self,
            tree="",
            node="",
            shots=None
    ):

        self.tree = ""
        self.node = ""
        self.shots = []

        self.set_tree(
            tree
        )

        self.set_node(
            node
        )

        self.set_shots(
            shots
        )

    # =====================================================
    # Tree
    # =====================================================

    def set_tree(
            self,
            tree
    ):

        if tree is None:
            tree = ""

        self.tree = str(
            tree
        ).strip()

    # =====================================================
    # Node
    # =====================================================

    def set_node(
            self,
            node
    ):

        if node is None:
            node = ""

        self.node = str(
            node
        ).strip()

    # =====================================================
    # Shots
    # =====================================================

    def set_shots(
            self,
            shots
    ):
        """
        设置炮号列表。

        自动完成：
        1. 转换为整数
        2. 去除重复炮号
        3. 保留原始输入顺序
        4. 忽略无效值
        """

        self.shots = []

        if shots is None:
            return

        if isinstance(
                shots,
                str
        ):
            shots = self.parse_shot_text(
                shots
            )

        try:
            iterator = iter(
                shots
            )
        except TypeError:
            iterator = iter(
                [shots]
            )

        used = set()

        for value in iterator:

            try:

                shot = int(
                    value
                )

            except Exception:

                continue

            if shot in used:
                continue

            used.add(
                shot
            )

            self.shots.append(
                shot
            )

    @staticmethod
    def parse_shot_text(
            text
    ):
        """
        解析炮号文本。

        支持：
        49050,49051,49052
        49050 49051 49052
        49050;49051;49052
        49050
        49051
        """

        if text is None:
            return []

        text = str(
            text
        )

        for separator in (
                ",",
                ";",
                "\n",
                "\t"
        ):
            text = text.replace(
                separator,
                " "
            )

        values = []

        for part in text.split():

            part = part.strip()

            if part == "":
                continue

            values.append(
                part
            )

        return values

    # =====================================================
    # Validation
    # =====================================================

    def validate(self):
        """
        校验请求。

        Returns
        -------
        tuple
            (是否有效, 错误信息)
        """

        if self.tree == "":
            return (
                False,
                "Tree name is empty."
            )

        if self.node == "":
            return (
                False,
                "Node path is empty."
            )

        if len(
                self.shots
        ) == 0:
            return (
                False,
                "Shot list is empty."
            )

        return (
            True,
            ""
        )

    def is_valid(self):

        valid, _ = self.validate()

        return valid

    # =====================================================
    # Information
    # =====================================================

    def shot_count(self):

        return len(
            self.shots
        )

    def copy(self):

        return CompareRequest(
            tree=self.tree,
            node=self.node,
            shots=list(
                self.shots
            )
        )


class CompareShotResult(object):
    """
    单个炮号的读取结果。

    一个对象只对应一个炮号。
    """

    def __init__(
            self,
            tree="",
            shot=None,
            node=""
    ):

        self.tree = str(
            tree
        ).strip()

        self.shot = shot

        self.node = str(
            node
        ).strip()

        self.success = False

        self.signal_data = None

        self.error = ""

    # =====================================================
    # Result
    # =====================================================

    def set_success(
            self,
            signal_data
    ):

        self.signal_data = signal_data

        self.success = (
                signal_data is not None
        )

        self.error = ""

    def set_error(
            self,
            error
    ):

        self.success = False

        self.signal_data = None

        if error is None:
            error = ""

        self.error = str(
            error
        ).strip()

    # =====================================================
    # Information
    # =====================================================

    def key(self):
        """
        返回曲线唯一键。

        用于Overlay避免重复添加同一个炮号和节点。
        """

        return "{}::{}::{}".format(
            self.tree,
            self.shot,
            self.node
        )

    def display_name(self):
        """
        返回图例显示名称。
        """

        node_name = self.node.split(
            ":"
        )[-1]

        return "{} [Shot {}]".format(
            node_name,
            self.shot
        )

    def point_count(self):

        if not self.success:
            return 0

        if self.signal_data is None:
            return 0

        y_data = getattr(
            self.signal_data,
            "y",
            None
        )

        if y_data is None:
            return 0

        try:

            return int(
                y_data.size
            )

        except Exception:

            try:

                return len(
                    y_data
                )

            except Exception:

                return 0


class CompareResult(object):
    """
    一次完整多炮号对比任务的结果集合。
    """

    def __init__(
            self,
            request=None
    ):

        if request is None:
            request = CompareRequest()

        self.request = request.copy()

        self.items = []

        self.cancelled = False

        self.restore_success = True
        self.restore_error = ""

    # =====================================================
    # Item
    # =====================================================

    def add_item(
            self,
            item
    ):

        if not isinstance(
                item,
                CompareShotResult
        ):
            raise TypeError(
                "item must be CompareShotResult."
            )

        self.items.append(
            item
        )

    def add_success(
            self,
            shot,
            signal_data
    ):

        item = CompareShotResult(
            tree=self.request.tree,
            shot=shot,
            node=self.request.node
        )

        item.set_success(
            signal_data
        )

        self.add_item(
            item
        )

        return item

    def add_error(
            self,
            shot,
            error
    ):

        item = CompareShotResult(
            tree=self.request.tree,
            shot=shot,
            node=self.request.node
        )

        item.set_error(
            error
        )

        self.add_item(
            item
        )

        return item

    # =====================================================
    # Query
    # =====================================================

    def success_items(self):

        return [
            item
            for item in self.items
            if item.success
        ]

    def failed_items(self):

        return [
            item
            for item in self.items
            if not item.success
        ]

    def signal_list(self):

        return [
            item.signal_data
            for item in self.success_items()
        ]

    def item_by_shot(
            self,
            shot
    ):

        try:

            shot = int(
                shot
            )

        except Exception:

            return None

        for item in self.items:

            if item.shot == shot:
                return item

        return None

    # =====================================================
    # Count
    # =====================================================

    def total_count(self):

        return len(
            self.request.shots
        )

    def completed_count(self):

        return len(
            self.items
        )

    def success_count(self):

        return len(
            self.success_items()
        )

    def failed_count(self):

        return len(
            self.failed_items()
        )

    def is_complete(self):

        return (
                self.completed_count()
                >=
                self.total_count()
        )

    # =====================================================
    # Restore
    # =====================================================

    def set_restore_error(
            self,
            error
    ):

        self.restore_success = False

        if error is None:
            error = ""

        self.restore_error = str(
            error
        ).strip()

    # =====================================================
    # Summary
    # =====================================================

    def summary(self):

        return {
            "tree": self.request.tree,
            "node": self.request.node,
            "shots": list(
                self.request.shots
            ),
            "total": self.total_count(),
            "completed": self.completed_count(),
            "success": self.success_count(),
            "failed": self.failed_count(),
            "cancelled": self.cancelled,
            "restore_success": self.restore_success,
            "restore_error": self.restore_error
        }
