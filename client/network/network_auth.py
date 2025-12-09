# client/network_auth.py
import socket, msgpack
import config

USE_TLS = False   # <-- Add this toggle to match server

def authenticate(username, password, host=config.HOST, port=config.AUTH_PORT):

    # Plain TCP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    s.sendall(msgpack.packb({
        "type": "login",
        "username": username,
        "password": password
    }, use_bin_type=True))

    response = msgpack.unpackb(s.recv(1024), raw=False)
    s.close()
    return response


def create_account(char_name, username, password, class_type="mage", host=config.HOST, port=config.AUTH_PORT):

    # Plain TCP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))

    s.sendall(msgpack.packb({
        "type": "create",
        "char_name": char_name,
        "username": username,
        "password": password,
        "class_type": class_type
    }, use_bin_type=True))

    response = msgpack.unpackb(s.recv(1024), raw=False)
    s.close()
    return response
