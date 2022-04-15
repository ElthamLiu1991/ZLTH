codes = {
    0: "",
    10000: "device {device} not exist",
    10001: "device {device} is offline",
    20000: "simulator {device} not exist",
    20001: "simulator {device} is offline",
    20002: "simulator {device} error: {error}",
    20003: "simulator {device} unreachable",
    30000: "attribute {attribute} not exist",
    40000: "{device} not in any network",
    40001: "{device} already in a network",
    90000: "internal error: {error}",
    90001: "missing mandatory item in payload",
    90002: "unsupported command: {command}",

}


def pack_response(code, data={}, **kwargs):
    if code in codes.keys():
        message = codes[code].format(**kwargs)
    else:
        message = "undefined error"
    return {
        "code": code,
        "message": message,
        "data": data
    }
