# client/network_auth.py
import socket, msgpack
import config
import ssl

def authenticate(username, password, host=config.HOST, port=config.AUTH_PORT):
    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context(cafile="certs/server.crt")
    s = context.wrap_socket(raw_sock, server_hostname=host)
    s.connect((host, port))
    s.sendall(msgpack.packb({"type":"login","username":username,"password":password}, use_bin_type=True))
    response = msgpack.unpackb(s.recv(1024), raw=False)
    s.close()
    return response

def create_account(char_name, username, password, host=config.HOST, port=config.AUTH_PORT):
    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context(cafile="certs/server.crt")
    s = context.wrap_socket(raw_sock, server_hostname=host)
    s.connect((host, port))
    s.sendall(msgpack.packb({"type":"create","char_name":char_name,"username":username,"password":password}, use_bin_type=True))
    response = msgpack.unpackb(s.recv(1024), raw=False)
    s.close()
    return response

