# -*- coding: utf-8 -*-

"""
-------------------------------------------------
Project : NNBI_database
File    : tree_loader.py
Author  :
Date    :
Description : Remote MDSplus Tree Loader
-------------------------------------------------
"""

import numpy as np

# =========================================================
# Tree Browser Node Filter
# =========================================================
#
# 增加或减少TreeBrowser中显示的节点类型，
# 修改该元组。
#
# 匹配时不区分大小写，只判断“节点自己的名称”，
# 不使用完整路径进行匹配。
#
# 例如：
#     SIG_BIAS_I  -> 包含 BIAS，保留
#     BIAS_I      -> 包含 BIAS，保留
#     SIG_ARC_I   -> 不包含任何关键字，整支删除
#
VISIBLE_NODE_KEYWORDS = (
    "RF",
    "ACC",
    "EXT",
    "BIAS",
    "MAG",
    "EG",
)

# GAIN / OFFSET / RAW 是标定辅助节点。
# 它们参与真实数据计算，但不在TreeBrowser中单独显示。
CALIBRATION_NODE_NAMES = (
    "GAIN",
    "OFFSET",
    "RAW",
)


class TreeLoader(object):
    """
    通过远程MDSplus Connection和GETNCI查询Tree结构。
    """

    def __init__(
            self,
            connection
    ):

        self.connection = connection

        self.visited_nids = set()

        self.stop_checker = None

    # =====================================================
    # Public
    # =====================================================

    def load(
            self,
            stop_checker=None
    ):
        """
        加载当前已经打开的MDSplus Tree。

        stop_checker：
        可调用对象，返回True时停止Tree递归读取。
        """

        if self.connection is None:
            raise RuntimeError(
                "MDSplus connection is not available."
            )

        self.stop_checker = stop_checker

        self.visited_nids.clear()

        self.check_stopped()

        root_nid = self.get_nid(
            "\\TOP"
        )

        self.check_stopped()

        tree_data = self.build_node(
            root_nid
        )

        self.check_stopped()

        tree_data = self.filter_tree(
            tree_data,
            is_root=True
        )

        return tree_data

    # =====================================================
    # Stop
    # =====================================================

    def check_stopped(self):
        """
        检查Tree读取是否收到停止请求
        """

        if self.stop_checker is None:
            return

        try:
            stopped = bool(
                self.stop_checker()
            )
        except Exception:
            stopped = False

        if stopped:
            raise RuntimeError(
                "Tree loading cancelled."
            )

    # =====================================================
    # Recursive Build
    # =====================================================

    def build_node(
            self,
            nid
    ):
        """
        根据NID递归构建节点
        """

        self.check_stopped()

        nid = int(nid)

        if nid in self.visited_nids:
            return None

        self.visited_nids.add(
            nid
        )

        item = {
            "name": self.get_node_name(nid),
            "path": self.get_full_path(nid),
            "usage": self.get_usage(nid),
            "nid": nid,
            "children": []
        }

        self.check_stopped()

        child_nids = self.get_child_nids(
            nid
        )

        for child_nid in child_nids:

            self.check_stopped()

            child_item = self.build_node(
                child_nid
            )

            if child_item is not None:
                item["children"].append(
                    child_item
                )

        item["children"].sort(
            key=lambda value: value[
                "name"
            ].upper()
        )

        return item

    # =====================================================
    # Tree Filter
    # =====================================================

    def filter_tree(
            self,
            item,
            is_root=False
    ):
        """
        过滤TreeBrowser最终显示的节点。

        当前规则：

        1. TOP根节点始终保留；

        2. GAIN / OFFSET / RAW 为标定辅助节点，
           不在TreeBrowser中显示；

        3. 对 SIG_* 这一层进行“硬过滤”：
           SIG_* 节点自身名称必须包含
           VISIBLE_NODE_KEYWORDS中的至少一个关键字，
           否则整个SIG分支直接删除，不再保留其任何子节点；

        4. 匹配只检查节点自己的name，
           不再检查完整path，避免：
               \TOP....SIG_BIAS_I:FOO
           因为路径中含BIAS而把FOO错误保留；

        5. TOP、FASTDAQ等普通结构父节点自身可以不匹配，
           只要其下面还有通过过滤的SIG_*分支，就保留该父节点，
           用来维持TreeBrowser的层级结构；

        6. 已进入允许显示的SIG_*分支后，
           其子节点仍按节点自己的name进行关键字过滤。
           因此BIAS_I、ACC_V等真实查询节点会保留，
           GAIN/OFFSET/RAW及其他不匹配节点会隐藏。

        后续增加或减少需要显示的SIG类型，
        只需要修改文件顶部VISIBLE_NODE_KEYWORDS。
        """

        self.check_stopped()

        if not isinstance(
                item,
                dict
        ):
            return None

        name = self.to_text(
            item.get(
                "name",
                ""
            )
        ).strip()

        upper_name = name.upper()

        # -------------------------------------------------
        # 标定辅助节点不显示
        # -------------------------------------------------

        if self.is_calibration_node_name(
                name
        ):
            return None

        # -------------------------------------------------
        # SIG_* 分支硬过滤
        #
        # 这一层如果自身名称不匹配，整个分支直接删除。
        # 例如 SIG_ARC_I 不再因为下面有其他节点而被保留。
        # -------------------------------------------------

        is_signal_branch = upper_name.startswith(
            "SIG_"
        )

        if (
                is_signal_branch
                and
                not self.matches_visible_keyword(
                    item
                )
        ):
            return None

        # -------------------------------------------------
        # 递归过滤子节点
        # -------------------------------------------------

        filtered_children = []

        for child in item.get(
                "children",
                []
        ):

            self.check_stopped()

            filtered_child = self.filter_tree(
                child,
                is_root=False
            )

            if filtered_child is not None:
                filtered_children.append(
                    filtered_child
                )

        item["children"] = filtered_children

        # TOP根节点始终保留
        if is_root:
            return item

        # SIG_* 分支已经在上面通过硬过滤，
        # 因此直接保留。
        if is_signal_branch:
            return item

        # 普通节点自身名称匹配则保留。
        if self.matches_visible_keyword(
                item
        ):
            return item

        # TOP/FASTDAQ等结构层节点本身可以不匹配，
        # 但如果下面还有过滤后的有效节点，则保留层级。
        if filtered_children:
            return item

        return None

    @staticmethod
    def is_calibration_node_name(
            name
    ):
        """
        判断节点是否为GAIN/OFFSET/RAW标定辅助节点。
        """

        text = str(
            name
        ).strip().upper()

        return text in CALIBRATION_NODE_NAMES

    @staticmethod
    def matches_visible_keyword(
            item
    ):
        """
        判断“节点自己的名称”是否包含允许显示的关键字。

        注意：
        这里只检查name，不检查完整path。
        """

        if not isinstance(
                item,
                dict
        ):
            return False

        name = str(
            item.get(
                "name",
                ""
            )
        ).strip().upper()

        for keyword in VISIBLE_NODE_KEYWORDS:

            keyword = str(
                keyword
            ).strip().upper()

            if (
                    keyword != ""
                    and
                    keyword in name
            ):
                return True

        return False

    # =====================================================
    # NID
    # =====================================================

    def get_nid(
            self,
            node_path
    ):

        self.check_stopped()

        expression = (
            'GETNCI({}, "NID_NUMBER")'.format(
                self.quote_path(node_path)
            )
        )

        value = self.execute(
            expression
        )

        value = self.to_scalar(
            value
        )

        if value is None:
            raise RuntimeError(
                "Cannot get NID for node: {}".format(
                    node_path
                )
            )

        return int(value)

    # =====================================================
    # Children
    # =====================================================

    def get_child_nids(
            self,
            nid
    ):
        """
        获取指定节点的直接子节点和成员节点NID。

        优先使用CHILDREN_NIDS、MEMBER_NIDS，并在服务器端
        转换为NID_NUMBER，避免NID对象在客户端取data()时被
        当作节点数据解析。

        如果服务器版本不支持数组形式，则回退到
        CHILD / MEMBER / BROTHER链式遍历。
        """

        self.check_stopped()

        children = self.get_nci_nid_array(
            nid,
            "CHILDREN_NIDS"
        )

        self.check_stopped()

        members = self.get_nci_nid_array(
            nid,
            "MEMBER_NIDS"
        )

        if not children:
            children = self.get_relation_nids(
                nid,
                "CHILD"
            )

        self.check_stopped()

        if not members:
            members = self.get_relation_nids(
                nid,
                "MEMBER"
            )

        result = []
        seen = set()

        for value in children + members:

            self.check_stopped()

            try:
                child_nid = int(
                    value
                )
            except (TypeError, ValueError):
                continue

            if child_nid < 0:
                continue

            if child_nid in seen:
                continue

            seen.add(
                child_nid
            )

            result.append(
                child_nid
            )

        return result

    def get_nci_nid_array(
            self,
            nid,
            item_name
    ):
        """
        获取NID数组，并在MDSplus服务器端转换为整数NID。
        """

        self.check_stopped()

        expression = (
            'GETNCI('
            'GETNCI({}, "{}"), '
            '"NID_NUMBER"'
            ')'
        ).format(
            int(nid),
            item_name
        )

        try:

            value = self.execute(
                expression
            )

        except Exception:

            return []

        return self.to_list(
            value
        )

    def get_relation_nids(
            self,
            nid,
            relation_name
    ):
        """
        通过CHILD或MEMBER取得首节点，再沿BROTHER链遍历。
        """

        self.check_stopped()

        first_nid = self.get_related_nid(
            nid,
            relation_name
        )

        if first_nid is None:
            return []

        result = []
        seen = set()

        current_nid = first_nid

        while current_nid is not None:

            self.check_stopped()

            try:
                current_nid = int(
                    current_nid
                )
            except (TypeError, ValueError):
                break

            if current_nid < 0:
                break

            if current_nid in seen:
                break

            seen.add(
                current_nid
            )

            result.append(
                current_nid
            )

            current_nid = self.get_related_nid(
                current_nid,
                "BROTHER"
            )

        return result

    def get_related_nid(
            self,
            nid,
            item_name
    ):
        """
        获取CHILD、MEMBER或BROTHER对应的整数NID。
        """

        self.check_stopped()

        expression = (
            'GETNCI('
            'GETNCI({}, "{}"), '
            '"NID_NUMBER"'
            ')'
        ).format(
            int(nid),
            item_name
        )

        try:

            value = self.execute(
                expression
            )

        except Exception:

            return None

        value = self.to_scalar(
            value
        )

        if value is None:
            return None

        try:
            return int(
                value
            )
        except (TypeError, ValueError):
            return None

    # =====================================================
    # Node Information
    # =====================================================

    def get_node_name(
            self,
            nid
    ):

        value = self.get_nci_scalar(
            nid,
            "NODE_NAME"
        )

        if value is None:
            return "UNKNOWN"

        return self.to_text(
            value
        ).strip()

    def get_full_path(
            self,
            nid
    ):

        value = self.get_nci_scalar(
            nid,
            "FULLPATH"
        )

        if value is None:
            return ""

        return self.to_text(
            value
        ).strip()

    def get_usage(
            self,
            nid
    ):

        value = self.get_nci_scalar(
            nid,
            "USAGE"
        )

        if value is None:
            return ""

        return self.to_text(
            value
        ).strip()

    # =====================================================
    # GETNCI
    # =====================================================

    def get_nci_scalar(
            self,
            nid,
            item_name
    ):

        self.check_stopped()

        expression = 'GETNCI({}, "{}")'.format(
            int(nid),
            item_name
        )

        try:
            value = self.execute(
                expression
            )
        except Exception:
            return None

        return self.to_scalar(
            value
        )

    def get_nci_array(
            self,
            nid,
            item_name
    ):

        self.check_stopped()

        expression = 'GETNCI({}, "{}")'.format(
            int(nid),
            item_name
        )

        try:
            value = self.execute(
                expression
            )
        except Exception:
            return []

        return self.to_list(
            value
        )

    # =====================================================
    # Execute
    # =====================================================

    def execute(
            self,
            expression
    ):

        self.check_stopped()

        result = self.connection.get(
            expression
        )

        self.check_stopped()

        if result is None:
            return None

        try:
            return result.data()
        except Exception:
            return result

    # =====================================================
    # Data Conversion
    # =====================================================

    @staticmethod
    def to_scalar(value):

        if value is None:
            return None

        if isinstance(value, np.ndarray):

            if value.size == 0:
                return None

            return value.reshape(-1)[0]

        if isinstance(value, (list, tuple)):

            if len(value) == 0:
                return None

            return value[0]

        return value

    @staticmethod
    def to_list(value):

        if value is None:
            return []

        if isinstance(value, np.ndarray):

            if value.size == 0:
                return []

            return value.reshape(-1).tolist()

        if isinstance(value, (list, tuple)):
            return list(value)

        return [value]

    @staticmethod
    def to_text(value):

        if value is None:
            return ""

        if isinstance(value, bytes):

            try:
                return value.decode(
                    "utf-8"
                )
            except UnicodeDecodeError:
                return value.decode(
                    "latin-1",
                    errors="ignore"
                )

        return str(value)

    # =====================================================
    # Utility
    # =====================================================

    @staticmethod
    def quote_path(path):

        text = str(path)

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

    def find(
            self,
            data,
            name
    ):

        if data is None:
            return None

        if data.get("name") == name:
            return data

        for child in data.get(
                "children",
                []
        ):

            result = self.find(
                child,
                name
            )

            if result is not None:
                return result

        return None

    def flatten(
            self,
            data
    ):

        result = []

        if data is not None:
            self._flatten(
                data,
                result
            )

        return result

    def _flatten(
            self,
            data,
            result
    ):

        result.append(
            data
        )

        for child in data.get(
                "children",
                []
        ):
            self._flatten(
                child,
                result
            )

    # =====================================================
    # Reload
    # =====================================================

    def reload(
            self,
            stop_checker=None
    ):

        return self.load(
            stop_checker=stop_checker
        )
