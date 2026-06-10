from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = ROOT_DIR / "frontend"
IS_WINDOWS = os.name == "nt"


ProcessEntry = tuple[str, subprocess.Popen[bytes]]


def _npm_command() -> str:
    return "npm.cmd" if IS_WINDOWS else "npm"


def _creation_flags() -> int:
    if IS_WINDOWS:
        return subprocess.CREATE_NEW_PROCESS_GROUP
    return 0


def _backend_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")

    if "DATABASE_URL" not in env and not (ROOT_DIR / ".env").exists():
        env["DATABASE_URL"] = "sqlite:///./dev.db"
        print("[dev] No .env found; using SQLite database at ./dev.db.")

    return env


def _is_port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        if sock.connect_ex(("127.0.0.1", port)) == 0:
            return False

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def _select_backend_port() -> int:
    preferred_port = int(os.environ.get("BACKEND_PORT", "8000"))
    for port in range(preferred_port, preferred_port + 20):
        if _is_port_available(port):
            if port != preferred_port:
                print(f"[dev] Port {preferred_port} is busy; using backend port {port}.")
            return port

    raise RuntimeError(
        f"No available backend port found from {preferred_port} to {preferred_port + 19}.",
    )


def _frontend_env(backend_port: int) -> dict[str, str]:
    env = os.environ.copy()
    env["VITE_API_BASE_URL"] = f"http://127.0.0.1:{backend_port}"
    return env


def _start_process(
    name: str,
    command: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
) -> subprocess.Popen[bytes]:
    print(f"[dev] Starting {name}: {' '.join(command)}")
    return subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        creationflags=_creation_flags(),
    )


def _request_stop(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return

    try:
        if IS_WINDOWS:
            process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            process.terminate()
    except Exception:
        process.terminate()


def _force_stop(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return

    if IS_WINDOWS:
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        process.kill()


def _stop_processes(processes: list[ProcessEntry]) -> None:
    running = [(name, process) for name, process in processes if process.poll() is None]
    if not running:
        return

    for name, process in reversed(running):
        print(f"[dev] Stopping {name}...")
        _request_stop(process)

    deadline = time.monotonic() + 8
    for name, process in reversed(running):
        timeout = max(0.1, deadline - time.monotonic())
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            print(f"[dev] Force stopping {name}...")
            _force_stop(process)
            process.wait()


def main() -> int:
    if not FRONTEND_DIR.exists():
        print(f"[dev] Frontend directory not found: {FRONTEND_DIR}", file=sys.stderr)
        return 1

    backend_port = _select_backend_port()
    backend_command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(backend_port),
        "--reload",
    ]
    frontend_command = [_npm_command(), "run", "dev", "--", "--host", "127.0.0.1"]

    processes: list[ProcessEntry] = []
    try:
        processes.append(
            ("backend", _start_process("backend", backend_command, ROOT_DIR, _backend_env()))
        )
        processes.append(
            (
                "frontend",
                _start_process(
                    "frontend",
                    frontend_command,
                    FRONTEND_DIR,
                    _frontend_env(backend_port),
                ),
            )
        )

        while True:
            for name, process in processes:
                exit_code = process.poll()
                if exit_code is not None:
                    print(f"[dev] {name} exited with code {exit_code}; stopping services.")
                    return exit_code
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[dev] Stopping services...")
        return 0
    finally:
        _stop_processes(processes)


if __name__ == "__main__":
    raise SystemExit(main())
