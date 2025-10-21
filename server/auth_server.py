

import socket
import threading
import msgpack
from server import auth_db
import sys
import time
import config
import ssl

HOST = config.HOST
AUTH_PORT = config.AUTH_PORT

auth_db.init_db()

def handle_client(conn, addr):
    try:
        data = conn.recv(1024)
        if not data:
            return
        msg = msgpack.unpackb(data, raw=False)
        response = {"status": "fail"}

        if msg["type"] == "login":
            if auth_db.verify_user(msg["username"], msg["password"]):
                token = auth_db.get_token(msg["username"])
                response = {"status": "ok", "token": token}
                print(f"[AUTH] {msg['username']} logged in")

        elif msg["type"] == "create":
            success = auth_db.create_user(msg["username"], msg["password"])
            if success:
                auth_db.create_character(msg["username"], msg["char_name"])
                token = auth_db.get_token(msg["username"])
                response = {"status": "ok", "token": token}
                print(f"[AUTH] {msg['username']} created")

        conn.sendall(msgpack.packb(response, use_bin_type=True))

    except Exception as e:
        print(f"[AUTH ERROR] {e}")
    finally:
        conn.close()


def token_cleanup_loop():
    while True:
        time.sleep(60)
        removed = auth_db.cleanup_expired_tokens()
        if removed:
            print(f"[AUTH] Removed {removed} expired tokens")


def start_auth_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, AUTH_PORT))
    s.listen()
    s.settimeout(1.0)

    # TLS context
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=f"{config.CERT_DIR}server.crt", keyfile=f"{config.CERT_DIR}server.key")
    print(f"[AUTH] TLS Auth Server running on {HOST}:{AUTH_PORT}")

    # Start token cleanup thread once
    threading.Thread(target=token_cleanup_loop, daemon=True).start()

    try:
        while True:
            try:
                conn, addr = s.accept()
                try:
                    tls_conn = context.wrap_socket(conn, server_side=True)
                    threading.Thread(target=handle_client, args=(tls_conn, addr), daemon=True).start()
                except ssl.SSLError as e:
                    print(f"[TLS ERROR] Failed handshake from {addr}: {e}")
                    conn.close()
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\n[AUTH] Shutting down server...")
    finally:
        s.close()
        sys.exit(0)


if __name__ == "__main__":
    start_auth_server()

