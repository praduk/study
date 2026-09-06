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
from .store import LibraryStore, StoreError

PACKAGE_ROOT = Path(__file__).resolve().parent.parent


def _open_when_ready(url: str) -> None:
    for _ in range(100):
        try:
            with urllib.request.urlopen(url + "/healthz", timeout=0.3) as response:
                if response.status == 200:
                    webbrowser.open_new_tab(url)
                    return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.1)


def _set_password(
    config_path: Path | None = None, *, application_root: Path | None = None
) -> None:
    # Validate the effective configuration before replacing its secret overlay.
    load_settings(config_path, application_root=application_root)
    first = getpass.getpass("New Study server password: ")
    second = getpass.getpass("Repeat password: ")
    if first != second:
        raise SystemExit("Passwords did not match.")
    if not first:
        raise SystemExit("Password cannot be empty.")
    target = write_password_override(make_password_hash(first), config_path)
    settings = load_settings(config_path, application_root=application_root)
    SessionStore(
        settings.data_dir / "runtime" / "sessions.sqlite3",
        settings.session_days,
        settings.session_generation,
    ).revoke_all()
    print(
        f"Password hash saved to {target.name}; existing sessions were revoked. "
        "Restart any running Study server to activate the new password."
    )


def _check_data(
    config_path: Path | None = None, *, application_root: Path | None = None
) -> None:
    settings = load_settings(config_path, application_root=application_root)
    try:
        result = LibraryStore(settings.data_dir).check_data()
    except StoreError as exc:
        raise SystemExit(f"Study data check failed: {exc}") from exc
    print(
        "Study data is valid: "
        f"format v{result['version']}, {result['folders']} folders, "
        f"{result['entries']} entries, {result['markdown_files']} Markdown files."
    )


def _checkout_at_or_above(start: Path) -> Path | None:
    start = start.resolve()
    for candidate in (start, *start.parents):
        if (candidate / "study.py").is_file() and (candidate / "study_app").is_dir():
            return candidate
    return None


def _installed_application_root(config_path: Path | None) -> Path:
    starts = [PACKAGE_ROOT]
    if config_path is not None:
        starts.append(config_path.resolve().parent)
    starts.append(Path.cwd())
    for start in starts:
        root = _checkout_at_or_above(start)
        if root is not None:
            return root
    raise SystemExit(
        "Run the installed Study command from a Study checkout, or pass "
        "--config pointing inside one."
    )


def main(application_root: Path | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the Study mathematics application.")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument(
        "--server", action="store_true", help="serve without opening a browser; password required"
    )
    actions.add_argument("--set-password", action="store_true", help="set the server-mode password")
    actions.add_argument(
        "--check-data", action="store_true", help="validate authored Study data and exit"
    )
    parser.add_argument("--config", type=Path, help="use a different TOML configuration file")
    args = parser.parse_args()

    root = (
        application_root.resolve()
        if application_root is not None
        else _installed_application_root(args.config)
    )
    config_path = (args.config or root / "config.toml").resolve()

    if args.set_password:
        _set_password(config_path, application_root=root)
        return
    if args.check_data:
        _check_data(config_path, application_root=root)
        return
    settings = load_settings(config_path, application_root=root)
    local_mode = not args.server
    if args.server and not settings.password_hash:
        raise SystemExit("Server mode requires a password. Run: python study.py --set-password")
    if not settings.frontend_public.joinpath("index.html").is_file():
        raise SystemExit("The Study interface is missing. Reinstall Study.")

    host = "127.0.0.1" if local_mode else settings.server_host
    url = f"http://127.0.0.1:{settings.port}"
    if local_mode:
        threading.Thread(target=_open_when_ready, args=(url,), daemon=True).start()
    else:
        print("Server mode is password-protected. Use HTTPS or a trusted VPN for phone access.")
    uvicorn.run(
        create_app(settings, local_mode=local_mode), host=host, port=settings.port, log_level="info"
    )
