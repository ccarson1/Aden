# server/auth_server.py
import socket
import threading
import msgpack
from server import auth_db  # your SQLite auth database module
import sys
import time
import config

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
        time.sleep(60)  # run every 60 seconds
        removed = auth_db.cleanup_expired_tokens()
        if removed:
            print(f"[AUTH] Removed {removed} expired tokens")


def start_auth_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, AUTH_PORT))
    s.listen()
    s.settimeout(1.0)
    print(f"[AUTH] Server running on {HOST}:{AUTH_PORT}")

    try:
        while True:
            try:
                conn, addr = s.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
                threading.Thread(target=token_cleanup_loop, daemon=True).start()
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\n[AUTH] Shutting down server...")
    finally:
        s.close()
        sys.exit(0)


if __name__ == "__main__":
    start_auth_server()
