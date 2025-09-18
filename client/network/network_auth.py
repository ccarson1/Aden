# client/network_auth.py
import socket, msgpack

def authenticate(username, password, host="127.0.0.1", port=50900):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(msgpack.packb({"type":"login","username":username,"password":password}, use_bin_type=True))
    response = msgpack.unpackb(s.recv(1024), raw=False)
    s.close()
    return response

def create_account(char_name, username, password, host="127.0.0.1", port=50900):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(msgpack.packb({"type":"create","char_name":char_name,"username":username,"password":password}, use_bin_type=True))
    response = msgpack.unpackb(s.recv(1024), raw=False)
    s.close()
    return response

