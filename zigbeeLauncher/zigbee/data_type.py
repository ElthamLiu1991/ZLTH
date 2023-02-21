data_type_table = {
    0x08: 1, 0x09: 2, 0x0a: 3, 0x0b: 4, 0x0c: 5, 0x0d: 6, 0x0e: 7, 0x0f: 8,
    0x10: 1,
    0x18: 1, 0x19: 2, 0x1a: 3, 0x1b: 4, 0x1c: 5, 0x1d: 6, 0x1e: 7, 0x1f: 8,
    0x20: 1, 0x21: 2, 0x22: 3, 0x23: 4, 0x24: 5, 0x25: 6, 0x26: 7, 0x27: 8,
    0x28: 1, 0x29: 2, 0x2a: 3, 0x2b: 4, 0x2c: 5, 0x2d: 6, 0x2e: 7, 0x2f: 8,
    0x30: 1, 0x31: 2,
    0x38: 2, 0x39: 4, 0x3a: 8,
    0x41: 0, 0x42: 0, 0x43: 0, 0x44: 0, 0x48: 0, 0x4c: 0, 0x50: 0, 0x51: 0,
    0xe0: 4, 0xe1: 4, 0xe2: 4,
    0xe8: 2, 0xe9: 2, 0xea: 4, 0xf0: 8, 0xf1: 16
}
data_type_value_table = {
    'data8': 0x08, 'data16': 0x09, 'data24': 0x0a, 'data32': 0x0b, 'data40': 0x0c, 'data48': 0x0d, 'data56': 0x0e, 'data64': 0x0f,
    'bool': 0x10,
    'map8': 0x18, 'map16': 0x19, 'map24': 0x1a, 'map32': 0x1b, 'map40': 0x1c, 'map48': 0x1d, 'map56': 0x1e, 'map64': 0x1f,
    'uint8': 0x20, 'uint16': 0x21, 'uint24': 0x22, 'uint32': 0x23, 'uint40': 0x24, 'uint48': 0x25, 'uint56': 0x26, 'uint64': 0x27,
    'int8': 0x28, 'int16': 0x29, 'int24': 0x2a, 'int32': 0x2b, 'int40': 0x2c, 'int48': 0x2d, 'int56': 0x2e, 'int64': 0x2f,
    'enum8': 0x30, 'enum16': 0x31,
    'semi': 0x38, 'single': 0x39, 'double': 0x3a,
    'octstr': 0x41, 'string': 0x42, 'oststr16': 0x43, 'string16': 0x44, 'array': 0x48, 'struct': 0x4c, 'set': 0x50, "bag": 0x51,
    'ToD': 0xe0, 'date': 0xe1, 'UTC': 0xe2,
    'clusterId': 0xe8, 'attribId': 0xe9, 'bacOID': 0xea, 'EUI64': 0xf0, 'key128': 0xf1
}

data_type_name_table = {
    0x08: 'data8', 0x09: 'data16', 0x0a: 'data24', 0x0b: 'data32', 0x0c: 'data40', 0x0d: 'data48', 0x0e: 'data56', 0x0f: 'data64',
    0x10: 'bool',
    0x18: 'map8', 0x19: 'map16', 0x1a: 'map24', 0x1b: 'map32', 0x1c: 'map40', 0x1d: 'map48', 0x1e: 'map56', 0x1f: 'map64',
    0x20: 'uint8', 0x21: 'uint16', 0x22: 'uint24', 0x23: 'uint32', 0x24: 'uint40', 0x25: 'uint48', 0x26: 'uint56', 0x27: 'uint64',
    0x28: 'int8', 0x29: 'int16', 0x2a: 'int24', 0x2b: 'int32', 0x2c: 'int40', 0x2d: 'int48', 0x2e: 'int56', 0x2f: 'int64',
    0x30: 'enum8', 0x31: 'enum16',
    0x38: 'semi', 0x39: 'single', 0x3a: 'double',
    0x41: 'octstr', 0x42: 'string', 0x43: 'octstr16', 0x44: 'string16', 0x48: 'array', 0x4c: 'struct', 0x50: 'set', 0x51: 'bag',
    0xe0: 'ToD', 0xe1: 'date', 0xe2: 'UTC',
    0xe8: 'clusterId', 0xe9: 'attribId', 0xea: 'bacOID', 0xf0: 'EUI64', 0xf1: 'key128'
}

zigbee_data_type_table = {
    (0x08, 'data8', 1),
    (0x09, 'data16', 2),
    (0x0a, 'data24', 3),
    (0x0b, 'data32', 4),
    (0x0c, 'data40', 5),
    (0x0d, 'data48', 6),
    (0x0e, 'data56', 7),
    (0x0f, 'data64', 8),
    (0x10, 'bool', 1),
    (0x18, 'map8', 1),
    (0x19, 'map16', 2),
    (0x1a, 'map24', 3),
    (0x1b, 'map32', 4),
    (0x1c, 'map40', 5),
    (0x1d, 'map48', 6),
    (0x1e, 'map56', 7),
    (0x1f, 'map64', 8),
    (0x20, 'uint8', 1),
    (0x21, 'uint16', 2),
    (0x22, 'uint24', 3),
    (0x23, 'uint32', 4),
    (0x24, 'uint40', 5),
    (0x25, 'uint48', 6),
    (0x26, 'uint56', 7),
    (0x27, 'uint64', 8),
    (0x28, 'int8', 1),
    (0x29, 'int16', 2),
    (0x2a, 'int24', 3),
    (0x2b, 'int32', 4),
    (0x2c, 'int40', 5),
    (0x2d, 'int48', 6),
    (0x2e, 'int56', 7),
    (0x2f, 'int64', 8),
    (0x30, 'enum8', 1),
    (0x31, 'enum16', 2),
    (0x38, 'semi', 2),
    (0x39, 'single', 4),
    (0x3a, 'double', 8),
    (0x41, 'octstr', 0),
    (0x42, 'string', 0),
    (0x43, 'octstr16', 0),
    (0x44, 'string16', 0),
    (0x48, 'array', 0),
    (0x4c, 'struct', 0),
    (0x50, 'set', 0),
    (0x51, 'bag', 0),
    (0xe0, 'ToD', 4),
    (0xe1, 'date', 4),
    (0xe2, 'UTC', 4),
    (0xe8, 'clusterId', 2),
    (0xe9, 'attribId', 2),
    (0xea, 'bacOID', 4),
    (0xf0, 'EUI64', 8),
    (0xf1, 'key128', 16)
}


def get_data_type(id=None, name=None, length=None):
    for item in zigbee_data_type_table:
        if id:
            if id == item[0]:
                return item
        else:
            if name == item[1]:
                return item
    return None


def get_bytes(data_type):
    global data_type_table
    if data_type in data_type_table:
        return data_type_table[data_type]
    else:
        return 0xFF