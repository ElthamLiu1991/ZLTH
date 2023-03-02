from zigbeeLauncher.zigbee.data_type import data_type_value_table, data_type_table, get_data_type


def type_exist(_type):
    if _type in data_type_value_table:
        return True
    else:
        return False


def format_validation(_type, value):
    _len = data_type_table[data_type_value_table[_type]]
    if isinstance(value, int) and _len == 0:
        return False
    if isinstance(value, str) and _len != 0:
        return False
    return True


def value_validation(type, value):
    id, name, length = get_data_type(name=type)
    if length != 0:
        maximum = (1 << 8 * length)
        if 0x28 <= id <= 0x2f:
            if not (-maximum/2) <= value < maximum/2:
                return False
        else:
            if not 0 <= value < maximum:
                return False
    return True

