from __future__ import annotations

import stat
from pathlib import Path

import pytest

import study_app.config as config_module
from study_app.auth import SessionStore
from study_app.config import load_settings, write_password_override

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


def test_password_rotation_preserves_local_overrides_and_revokes_sessions(
    tmp_path: Path, monkeypatch
):
    monkeypatch.setattr(config_module, "ROOT", tmp_path)
    (tmp_path / "study.py").write_text("", encoding="utf-8")
    (tmp_path / "study_app").mkdir()
    config_path = tmp_path / "custom.toml"
    config_path.write_text(
        """[study]
port = 8765
server_host = "0.0.0.0"
allowed_hosts = ["study.example"]
secure_cookie = false
session_days = 30
max_upload_mb = 12
max_image_megapixels = 32
""",
        encoding="utf-8",
    )
    local_path = tmp_path / "custom.local.toml"
    local_path.write_text(
        """[study]
port = 9443
allowed_hosts = ["notes.example"]
secure_cookie = true
setup_nonce = "old-nonce"

[unrelated]
keep = "this value"
""",
        encoding="utf-8",
    )

    old_settings = load_settings(config_path)
    sessions_path = old_settings.data_dir / "runtime" / "sessions.sqlite3"
    old_store = SessionStore(
        sessions_path, old_settings.session_days, old_settings.session_generation
    )
    session = old_store.create()
    assert old_store.get(session.token) is not None

    written = write_password_override("new-password-hash", config_path)
    assert written == local_path
    with local_path.open("rb") as stream:
        local_document = tomllib.load(stream)
    assert local_document["study"]["port"] == 9443
    assert local_document["study"]["allowed_hosts"] == ["notes.example"]
    assert local_document["study"]["secure_cookie"] is True
    assert local_document["study"]["password_hash"] == "new-password-hash"
    assert local_document["study"]["setup_nonce"] != "old-nonce"
    assert local_document["unrelated"]["keep"] == "this value"
    assert stat.S_IMODE(local_path.stat().st_mode) == 0o600

    new_settings = load_settings(config_path)
    assert new_settings.port == 9443
    assert new_settings.secure_cookie is True
    assert new_settings.allowed_hosts == ("notes.example",)
    new_store = SessionStore(
        sessions_path, new_settings.session_days, new_settings.session_generation
    )
    assert new_store.get(session.token) is None


def test_data_directory_is_fixed_beside_study_launcher(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(config_module, "ROOT", tmp_path)
    (tmp_path / "study.py").write_text("", encoding="utf-8")
    (tmp_path / "study_app").mkdir()
    config_path = tmp_path / "custom.toml"
    config_path.write_text("[study]\nport = 8765\n", encoding="utf-8")

    assert load_settings(config_path).data_dir == tmp_path / "data"

    config_path.write_text(
        '[study]\ndata_dir = "another-library"\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="fixed at the data folder"):
        load_settings(config_path)


def test_explicit_application_root_controls_data_and_shipped_frontend(tmp_path: Path):
    root = tmp_path / "checkout"
    root.mkdir()
    (root / "study.py").write_text("", encoding="utf-8")
    (root / "study_app").mkdir()
    config_path = root / "config.toml"
    config_path.write_text("[study]\nport = 8765\n", encoding="utf-8")

    settings = load_settings(config_path, application_root=root)

    assert settings.root == root.resolve()
    assert settings.data_dir == root.resolve() / "data"


def test_settings_refuse_a_package_directory_that_is_not_a_checkout(
    tmp_path: Path, monkeypatch
):
    package_parent = tmp_path / "site-packages"
    package_parent.mkdir()
    monkeypatch.setattr(config_module, "ROOT", package_parent)

    with pytest.raises(ValueError, match="checkout containing study.py"):
        load_settings()

    assert not (package_parent / "data").exists()


def test_same_session_generation_survives_store_restart(tmp_path: Path):
    path = tmp_path / "runtime" / "sessions.sqlite3"
    first = SessionStore(path, 30, "unchanged")
    session = first.create()
    assert SessionStore(path, 30, "unchanged").get(session.token) is not None
