data_type_table = {
    0xff: 1,
    0x00: 0,
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


def get_bytes(data_type):
    type = int(data_type, 16)
    global data_type_table
    if type in data_type_table:
        return data_type_table[type]
    else:
        return 0xFF