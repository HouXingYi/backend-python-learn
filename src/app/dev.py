from __future__ import annotations

import os
import signal
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

    backend_command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--reload",
    ]
    frontend_command = [_npm_command(), "run", "dev", "--", "--host", "127.0.0.1"]

    processes: list[ProcessEntry] = []
    try:
        processes.append(
            ("backend", _start_process("backend", backend_command, ROOT_DIR, _backend_env()))
        )
        processes.append(
            ("frontend", _start_process("frontend", frontend_command, FRONTEND_DIR))
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
