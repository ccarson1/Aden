# import socket
# import msgpack
# import config

# def create_udp_socket(timeout=config.TIMEOUT):
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     s.settimeout(timeout)
#     return s

# def send_msg(sock, addr, message):
#     sock.sendto(msgpack.packb(message, use_bin_type=True), addr)

# def recv_msg(sock, buffer_size=config.BUFFER_SIZE):
#     data, _ = sock.recvfrom(buffer_size)
#     return msgpack.unpackb(data, raw=False)


import socket
import msgpack
import config

class NetworkClient:
    def __init__(self):
        self.sock = None
        self.server_addr = None
        self.create_socket()

    def create_socket(self):
        if self.sock:
            self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(config.TIMEOUT)
        self.server_addr = (config.HOST, config.PORT)

    def reconnect(self, host, port):
        config.save_network_settings(host, port)
        # Update the current HOST/PORT variables
        global HOST, PORT
        HOST = host
        PORT = port
        self.create_socket()  # recreate socket with new address

    def send_msg(self, msg):
        self.sock.sendto(msgpack.packb(msg, use_bin_type=True), self.server_addr)

    def recv_msg(self):
        data, _ = self.sock.recvfrom(config.BUFFER_SIZE)
        return msgpack.unpackb(data, raw=False)
