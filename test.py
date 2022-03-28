import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ret = s.connect_ex(('localhost', 5001))
print(ret)
if ret == 0:
    print("5000 in used")
    exit(-1)
else:
    print("good")