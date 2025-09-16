import socket
import msgpack

def create_udp_socket(bind=True, host="127.0.0.1", port=50880, timeout=1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if bind:
        s.bind((host, port))
    s.settimeout(timeout)
    return s

def send_msg(socket, addr, message):
    socket.sendto(msgpack.packb(message, use_bin_type=True), addr)

def recv_msg(socket, buffer_size=1024):
    data, addr = socket.recvfrom(buffer_size)
    return msgpack.unpackb(data, raw=False), addr
