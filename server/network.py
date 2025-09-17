import socket
import msgpack
import config

def create_udp_socket(bind=True, host=config.HOST, port=config.PORT, timeout=config.TIMEOUT):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if bind:
        s.bind((host, port))
    s.settimeout(timeout)
    return s

def send_msg(socket, addr, message):
    socket.sendto(msgpack.packb(message, use_bin_type=True), addr)

def recv_msg(socket, buffer_size=config.BUFFER_SIZE):
    data, addr = socket.recvfrom(buffer_size)
    return msgpack.unpackb(data, raw=False), addr
