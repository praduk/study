from __future__ import annotations

from pathlib import Path

import pytest

from study_app.config import Settings


@pytest.fixture
def settings_factory(tmp_path: Path):
    def make(**overrides):
        root = tmp_path / f"app-{len(list(tmp_path.iterdir()))}"
        root.mkdir()
        values = {
            "root": root,
            "port": 8765,
            "server_host": "0.0.0.0",
            "allowed_hosts": ("study.test",),
            "password_hash": "",
            "session_days": 30,
            "secure_cookie": False,
            "max_upload_mb": 2,
            "max_image_megapixels": 2,
        }
        values.update(overrides)
        return Settings(**values)

    return make
