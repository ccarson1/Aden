import socket
import msgpack

def create_udp_socket(timeout=1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    return s

def send_msg(sock, addr, message):
    sock.sendto(msgpack.packb(message, use_bin_type=True), addr)

def recv_msg(sock, buffer_size=4096):
    data, _ = sock.recvfrom(buffer_size)
    return msgpack.unpackb(data, raw=False)
