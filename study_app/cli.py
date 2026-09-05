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
from .git_ops import GitError, GitRepository
from .store import LibraryStore, StoreError


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


def _check_data(config_path: Path | None = None) -> None:
    settings = load_settings(config_path)
    try:
        result = LibraryStore(settings.data_dir).check_data()
    except StoreError as exc:
        raise SystemExit(f"Study data check failed: {exc}") from exc
    print(
        "Study data is valid: "
        f"format v{result['version']}, {result['folders']} folders, "
        f"{result['entries']} entries, {result['markdown_files']} Markdown files."
    )


def _migrate_storage(config_path: Path | None = None) -> None:
    settings = load_settings(config_path)
    store = LibraryStore(settings.data_dir)
    git = GitRepository(settings.root, settings.data_dir, store.mutation_lock)
    with store.mutation_lock:
        try:
            git.ensure_no_operation_in_progress()
        except GitError as exc:
            raise SystemExit(f"Storage migration requires idle Git state: {exc}") from exc
        status = git.status()
        if not status.get("available"):
            raise SystemExit(
                f"Storage migration requires Git: {status.get('message', 'unavailable')}"
            )
        if status.get("dirty"):
            raise SystemExit("Storage migration requires a clean Git worktree.")
        try:
            result = store.migrate_to_v2()
        except StoreError as exc:
            raise SystemExit(f"Storage migration failed: {exc}") from exc
    print(
        "Storage migration completed and verified: "
        f"{result['folders']} folders, {result['entries']} entries, "
        f"{result['markdown_files']} Markdown files. Review and commit the Git diff."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Study mathematics application.")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument(
        "--server", action="store_true", help="serve without opening a browser; password required"
    )
    actions.add_argument("--set-password", action="store_true", help="set the server-mode password")
    actions.add_argument(
        "--check-data", action="store_true", help="validate authored Study data and exit"
    )
    actions.add_argument(
        "--migrate-storage",
        action="store_true",
        help="explicitly migrate a clean version 1 library to sharded version 2 storage",
    )
    parser.add_argument("--config", type=Path, help="use a different TOML configuration file")
    args = parser.parse_args()

    if args.set_password:
        _set_password(args.config)
        return
    if args.check_data:
        _check_data(args.config)
        return
    if args.migrate_storage:
        _migrate_storage(args.config)
        return

    settings = load_settings(args.config)
    local_mode = not args.server
    if args.server and not settings.password_hash:
        raise SystemExit("Server mode requires a password. Run: python study.py --set-password")
    selected_frontend = (
        settings.built_frontend
        if settings.rich_frontend and settings.built_frontend.joinpath("index.html").is_file()
        else settings.no_build_frontend
    )
    if not selected_frontend.joinpath("index.html").is_file():
        raise SystemExit(
            "The Study interface is missing. Reinstall Study or build the frontend."
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
