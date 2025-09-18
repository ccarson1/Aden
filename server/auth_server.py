import socket
import threading
import msgpack
import uuid
import auth_db  # your SQLite auth database module
import sys

HOST = "127.0.0.1"
AUTH_PORT = 50900

auth_db.init_db()
active_tokens = {}  # token -> username

def handle_client(conn, addr):
    print(f"[AUTH] Connection from {addr}")
    try:
        data = conn.recv(1024)
        if not data:
            return
        msg = msgpack.unpackb(data, raw=False)

        response = {"status": "fail"}
        if msg["type"] == "login":
            if auth_db.verify_user(msg["username"], msg["password"]):
                token = str(uuid.uuid4())
                active_tokens[token] = msg["username"]
                response = {"status": "ok", "token": token}
        elif msg["type"] == "create":
            success = auth_db.create_user(msg["username"], msg["password"])
            if success:
                auth_db.create_character(msg["username"], msg["char_name"])
                token = str(uuid.uuid4())
                active_tokens[token] = msg["username"]
                response = {"status": "ok", "token": token}
            else:
                response = {"status": "fail", "reason": "username_taken"}
        else:
            response = {"status": "fail", "reason": "unknown_request"}

        conn.sendall(msgpack.packb(response, use_bin_type=True))
    except Exception as e:
        print(f"[AUTH ERROR] {e}")
    finally:
        conn.close()

def start_auth_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, AUTH_PORT))
    s.listen()
    s.settimeout(1.0)  # <-- check every second
    print(f"[AUTH] Server running on {HOST}:{AUTH_PORT}")

    try:
        while True:
            try:
                conn, addr = s.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
            except socket.timeout:
                continue  # loop back, allow KeyboardInterrupt to be raised
    except KeyboardInterrupt:
        print("\n[AUTH] Shutting down server...")
    finally:
        s.close()
        sys.exit(0)

if __name__ == "__main__":
    start_auth_server()
