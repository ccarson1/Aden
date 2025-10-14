import subprocess
import sys
import os

auth_proc = None
main_proc = None

def run_servers():
    global auth_proc, main_proc

    # Get the absolute path to the project root
    project_root = os.path.abspath(os.path.dirname(__file__))  # e.g. D:\Python\pygame\Aden
    server_dir = os.path.join(project_root, "server")

    auth_path = os.path.join(server_dir, "auth_server.py")
    main_path = os.path.join(server_dir, "main.py")

    # Environment with PYTHONPATH set to project root
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root

    # Start Auth Server
    auth_proc = subprocess.Popen(
        [sys.executable, auth_path],
        cwd=project_root,
        env=env,
    )
    print(f"[INFO] Auth server started (PID {auth_proc.pid})")

    # Start Main Server
    main_proc = subprocess.Popen(
        [sys.executable, main_path],
        cwd=project_root,
        env=env,
    )
    print(f"[INFO] Main server started (PID {main_proc.pid})")

    return auth_proc, main_proc


def stop_servers():
    global auth_proc, main_proc
    for name, proc in (("Auth", auth_proc), ("Main", main_proc)):
        if proc and proc.poll() is None:
            print(f"[INFO] Stopping {name} server (PID {proc.pid})...")
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                print(f"[WARN] {name} server did not stop gracefully, killing...")
                proc.kill()
