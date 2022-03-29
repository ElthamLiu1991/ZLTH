codes = {
    0: "",
    10000: "device {device} not exist",
    10001: "device {device} is offline",
    20000: "simulator {device} not exist",
    20001: "simulator {device} is offline",
    20002: "simulator {device} error: {error}",
    20003: "simulator {device} unreachable",
    90000: "internal error: {error}"
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
