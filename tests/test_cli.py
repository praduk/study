from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

from study_app import cli
from study_app.config import Settings


def _settings(tmp_path: Path, *, password_hash: str = "", port: int = 8123) -> Settings:
    root = tmp_path / "study"
    (root / "frontend" / "dist" / "client").mkdir(parents=True)
    (root / "frontend" / "dist" / "client" / "index.html").write_text("Study")
    return Settings(
        root=root,
        port=port,
        server_host="0.0.0.0",
        allowed_hosts=("study.test",),
        password_hash=password_hash,
        session_days=30,
        secure_cookie=False,
        max_upload_mb=12,
        max_image_megapixels=32,
    )


def test_set_password_accepts_one_character(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    settings = _settings(tmp_path)
    prompts = iter(["x", "x"])
    written: dict[str, object] = {}

    class FakeSessionStore:
        def __init__(self, path: Path, session_days: int, generation: str):
            written["session_store"] = (path, session_days, generation)

        def revoke_all(self) -> None:
            written["revoked"] = True

    monkeypatch.setattr(cli, "load_settings", lambda _path=None: settings)
    monkeypatch.setattr(cli.getpass, "getpass", lambda _prompt: next(prompts))
    monkeypatch.setattr(cli, "make_password_hash", lambda password: f"hash:{password}")
    monkeypatch.setattr(
        cli,
        "write_password_override",
        lambda password_hash, _path=None: written.update(password_hash=password_hash)
        or tmp_path / "config.local.toml",
    )
    monkeypatch.setattr(cli, "SessionStore", FakeSessionStore)

    cli._set_password()

    assert written["password_hash"] == "hash:x"
    assert written["revoked"] is True


def test_set_password_rejects_empty_password(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    settings = _settings(tmp_path)
    prompts = iter(["", ""])
    monkeypatch.setattr(cli, "load_settings", lambda _path=None: settings)
    monkeypatch.setattr(cli.getpass, "getpass", lambda _prompt: next(prompts))

    with pytest.raises(SystemExit, match="cannot be empty"):
        cli._set_password()


def test_no_arguments_is_loopback_local_mode_and_starts_browser_waiter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    settings = _settings(tmp_path)
    calls: dict[str, Any] = {}

    class FakeThread:
        def __init__(self, *, target: Any, args: tuple[str], daemon: bool):
            calls["thread"] = (target, args, daemon)

        def start(self) -> None:
            calls["thread_started"] = True

    monkeypatch.setattr(sys, "argv", ["study.py"])
    monkeypatch.setattr(cli, "load_settings", lambda _path=None: settings)
    monkeypatch.setattr(cli.threading, "Thread", FakeThread)
    monkeypatch.setattr(
        cli, "create_app", lambda actual, local_mode: (actual, local_mode)
    )
    monkeypatch.setattr(
        cli.uvicorn,
        "run",
        lambda app, **kwargs: calls.update(app=app, uvicorn=kwargs),
    )

    cli.main()

    assert calls["app"] == (settings, True)
    assert calls["uvicorn"]["host"] == "127.0.0.1"
    assert calls["uvicorn"]["port"] == 8123
    assert calls["thread"][1] == ("http://127.0.0.1:8123",)
    assert calls["thread"][2] is True
    assert calls["thread_started"] is True


def test_server_mode_requires_password_and_does_not_start_browser_waiter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    settings = _settings(tmp_path)
    monkeypatch.setattr(sys, "argv", ["study.py", "--server"])
    monkeypatch.setattr(cli, "load_settings", lambda _path=None: settings)
    monkeypatch.setattr(
        cli.threading,
        "Thread",
        lambda **_kwargs: pytest.fail("server mode must not create a browser thread"),
    )
    monkeypatch.setattr(
        cli.uvicorn, "run", lambda *_args, **_kwargs: pytest.fail("server must not start")
    )

    with pytest.raises(SystemExit, match="requires a password"):
        cli.main()


def test_server_mode_uses_configured_bind_and_port_without_browser(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    settings = _settings(tmp_path, password_hash="argon2-hash", port=9443)
    calls: dict[str, Any] = {}
    monkeypatch.setattr(sys, "argv", ["study.py", "--server"])
    monkeypatch.setattr(cli, "load_settings", lambda _path=None: settings)
    monkeypatch.setattr(cli, "create_app", lambda actual, local_mode: (actual, local_mode))
    monkeypatch.setattr(
        cli.threading,
        "Thread",
        lambda **_kwargs: pytest.fail("server mode must not create a browser thread"),
    )
    monkeypatch.setattr(
        cli.uvicorn,
        "run",
        lambda app, **kwargs: calls.update(app=app, uvicorn=kwargs),
    )

    cli.main()

    assert calls["app"] == (settings, False)
    assert calls["uvicorn"]["host"] == "0.0.0.0"
    assert calls["uvicorn"]["port"] == 9443
