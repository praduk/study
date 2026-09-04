from __future__ import annotations

import argparse
import getpass
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

import uvicorn

from .app import create_app
from .auth import SessionStore, make_password_hash
from .config import load_settings, write_password_override


def _open_when_ready(url: str) -> None:
    for _ in range(100):
        try:
            with urllib.request.urlopen(url + "/healthz", timeout=0.3) as response:
                if response.status == 200:
                    webbrowser.open_new_tab(url)
                    return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.1)


def _set_password(config_path: Path | None = None) -> None:
    # Validate the effective configuration before replacing its secret overlay.
    load_settings(config_path)
    first = getpass.getpass("New Study server password: ")
    second = getpass.getpass("Repeat password: ")
    if first != second:
        raise SystemExit("Passwords did not match.")
    if not first:
        raise SystemExit("Password cannot be empty.")
    target = write_password_override(make_password_hash(first), config_path)
    settings = load_settings(config_path)
    SessionStore(
        settings.data_dir / "runtime" / "sessions.sqlite3",
        settings.session_days,
        settings.session_generation,
    ).revoke_all()
    print(
        f"Password hash saved to {target.name}; existing sessions were revoked. "
        "Restart any running Study server to activate the new password."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Study mathematics application.")
    parser.add_argument(
        "--server", action="store_true", help="serve without opening a browser; password required"
    )
    parser.add_argument("--set-password", action="store_true", help="set the server-mode password")
    parser.add_argument("--config", type=Path, help="use a different TOML configuration file")
    args = parser.parse_args()

    if args.set_password:
        _set_password(args.config)
        return

    settings = load_settings(args.config)
    local_mode = not args.server
    if args.server and not settings.password_hash:
        raise SystemExit("Server mode requires a password. Run: python study.py --set-password")
    if not settings.built_frontend.joinpath("index.html").exists():
        raise SystemExit(
            "The frontend is not built. Run: cd frontend && npm install && npm run build"
        )

    host = "127.0.0.1" if local_mode else settings.server_host
    url = f"http://127.0.0.1:{settings.port}"
    if local_mode:
        threading.Thread(target=_open_when_ready, args=(url,), daemon=True).start()
    else:
        print("Server mode is password-protected. Use HTTPS or a trusted VPN for phone access.")
    uvicorn.run(
        create_app(settings, local_mode=local_mode), host=host, port=settings.port, log_level="info"
    )
