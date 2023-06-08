import my_globals


class SexMap:  # 简单，方便，拓展性强的快速性别映射工具类 支持美利坚现状((
    number_map = {1: "男", 2: "女"}
    default_string = "男"
    default_number = 1

    def to_string(self, number: int) -> str:
        return self.number_map.get(number, self.default_string)

    def to_number(self, string: str) -> int:
        return int(next((k for k, v in self.number_map.items() if v == string), self.default_number))


class ResultMap(SexMap):
    def __init__(self):
        super(ResultMap, self).__init__()
        self.number_map = {-1: "缺考"}
        self.default_string = "缺考"
        self.default_number = -1


def is_number(text) -> bool:
    """
    text是否为整数
    """
    try:
        int(text)
    except ValueError:
        return False
    return True


def is_decimal(text) -> bool:
    """
    text是否为小数
    """
    try:
        float(text)
    except ValueError:
        return False
    return True


def check_permission(permission) -> bool:
    if "*" in my_globals.user_permission or permission in my_globals.user_permission:
        return True
    nodes = permission.split(".")  # 根据.做切割
    node_prefix = ""
    for index, node in enumerate(nodes[:-1]):
        if not node_prefix:
            if f'{node}.*' in my_globals.user_permission:
                return True
            node_prefix = node
        else:
            node_prefix = f'{node_prefix}.{node}'
            if f'{node_prefix}.*' in my_globals.user_permission:
                return True
    return False
