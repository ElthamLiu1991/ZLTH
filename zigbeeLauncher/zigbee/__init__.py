from zigbeeLauncher.zigbee.data_type import data_type_value_table, data_type_table


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


def value_validation(_type, value):
    _type = data_type_value_table[_type]
    _len = data_type_table[_type]
    if _len != 0:
        if 0x28 <= _type <= 0x2f:
            maximum = (1 << 8 * _len) / 2
            if not (-maximum) <= value < maximum:
                return False
        else:
            if not 0 <= value < (1 << 8 * _len):
                return False
        return True
    else:
        return True
