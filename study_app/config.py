from __future__ import annotations

import hashlib
import ipaddress
import os
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

import tomli_w

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "config.toml"
LOCAL_CONFIG = ROOT / "config.local.toml"


@dataclass(frozen=True)
class Settings:
    root: Path
    port: int
    server_host: str
    allowed_hosts: tuple[str, ...]
    password_hash: str
    session_days: int
    secure_cookie: bool
    max_upload_mb: int
    max_image_megapixels: int
    setup_nonce: str = ""

    @property
    def data_dir(self) -> Path:
        """The fixed authored-data root beside study.py."""
        return self.root / "data"

    @property
    def built_frontend(self) -> Path:
        return self.root / "frontend" / "dist" / "client"

    @property
    def frontend_public(self) -> Path:
        return self.root / "frontend" / "public"

    @property
    def session_generation(self) -> str:
        """A non-secret identifier that changes whenever authentication is rotated."""
        material = f"study-session-v1\0{self.password_hash}\0{self.setup_nonce}"
        return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _read_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as stream:
        value = tomllib.load(stream)
    if not isinstance(value, dict):
        raise TypeError(f"{path.name} must contain a TOML table")
    study = value.get("study", value)
    if not isinstance(study, dict):
        raise TypeError(f"the study value in {path.name} must be a TOML table")
    return study


def _local_config_for(path: Path) -> Path:
    if path == DEFAULT_CONFIG:
        return LOCAL_CONFIG
    return path.with_name(f"{path.stem}.local{path.suffix}")


def _exact_host(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("allowed_hosts entries must be strings")
    host = str(value).strip().casefold()
    if not host or host == "*" or "*" in host:
        raise ValueError(
            "allowed_hosts must contain exact hostnames or IP addresses, not wildcards"
        )
    if any(character.isspace() for character in host) or "/" in host or "://" in host:
        raise ValueError(f"invalid allowed host: {value!r}")
    if host.startswith("["):
        if not host.endswith("]") or host.count("[") != 1 or host.count("]") != 1:
            raise ValueError(f"invalid allowed host: {value!r}")
        try:
            ipaddress.IPv6Address(host[1:-1])
        except ValueError as exc:
            raise ValueError(f"invalid allowed IPv6 address: {value!r}") from exc
    elif ":" in host:
        raise ValueError("IPv6 addresses in allowed_hosts must use brackets, for example [::1]")
    return host.rstrip(".")


def load_settings(config_path: Path | None = None) -> Settings:
    path = (config_path or DEFAULT_CONFIG).resolve()
    values: dict[str, Any] = {
        "port": 8765,
        "server_host": "0.0.0.0",
        "allowed_hosts": ["127.0.0.1", "localhost", "[::1]"],
        "password_hash": "",
        "session_days": 30,
        "secure_cookie": False,
        "max_upload_mb": 12,
        "max_image_megapixels": 32,
        "setup_nonce": "",
    }
    configured_values = _read_toml(path)
    local_values = _read_toml(_local_config_for(path))
    if "data_dir" in configured_values or "data_dir" in local_values:
        raise ValueError("data_dir is fixed at the data folder beside study.py")
    values.update(configured_values)
    values.update(local_values)

    if not isinstance(values["port"], int) or isinstance(values["port"], bool):
        raise TypeError("port must be an integer")
    port = values["port"]
    if not 1 <= port <= 65535:
        raise ValueError("port must be between 1 and 65535")
    configured_hosts = values["allowed_hosts"]
    if not isinstance(configured_hosts, list):
        raise TypeError("allowed_hosts must be a TOML array")
    allowed = tuple(dict.fromkeys(_exact_host(host) for host in configured_hosts))
    if not allowed:
        raise ValueError("allowed_hosts must contain at least one exact host")
    server_host = str(values["server_host"]).strip()
    if (
        not server_host
        or any(character.isspace() for character in server_host)
        or "://" in server_host
        or "/" in server_host
    ):
        raise ValueError("server_host must be a hostname or bind address, not a URL")
    if ":" in server_host:
        try:
            ipaddress.IPv6Address(server_host)
        except ValueError as exc:
            raise ValueError("server_host must not include a port") from exc

    integer_values: dict[str, int] = {}
    for key in ("session_days", "max_upload_mb", "max_image_megapixels"):
        value = values[key]
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{key} must be an integer")
        integer_values[key] = value
    session_days = integer_values["session_days"]
    max_upload_mb = integer_values["max_upload_mb"]
    max_image_megapixels = integer_values["max_image_megapixels"]
    if not 1 <= session_days <= 365:
        raise ValueError("session_days must be between 1 and 365")
    if not 1 <= max_upload_mb <= 100:
        raise ValueError("max_upload_mb must be between 1 and 100")
    if not 1 <= max_image_megapixels <= 200:
        raise ValueError("max_image_megapixels must be between 1 and 200")
    if not isinstance(values["password_hash"], str):
        raise TypeError("password_hash must be a string")
    if not isinstance(values["setup_nonce"], str) or len(values["setup_nonce"]) > 256:
        raise TypeError("setup_nonce must be a string of at most 256 characters")
    if not isinstance(values["secure_cookie"], bool):
        raise TypeError("secure_cookie must be true or false")

    return Settings(
        root=ROOT,
        port=port,
        server_host=server_host,
        allowed_hosts=allowed,
        password_hash=str(values["password_hash"]).strip(),
        session_days=session_days,
        secure_cookie=bool(values["secure_cookie"]),
        max_upload_mb=max_upload_mb,
        max_image_megapixels=max_image_megapixels,
        setup_nonce=values["setup_nonce"],
    )


def write_password_override(password_hash: str, config_path: Path | None = None) -> Path:
    """Write a local-only password override without touching the tracked config."""
    target = _local_config_for((config_path or DEFAULT_CONFIG).resolve())
    if not isinstance(password_hash, str) or not password_hash:
        raise ValueError("password_hash must be a nonempty string")
    if target.exists():
        with target.open("rb") as stream:
            document = tomllib.load(stream)
        if not isinstance(document, dict):
            raise TypeError(f"{target.name} must contain a TOML table")
    else:
        document = {}

    known_keys = {
        "port",
        "server_host",
        "allowed_hosts",
        "password_hash",
        "session_days",
        "secure_cookie",
        "max_upload_mb",
        "max_image_megapixels",
        "setup_nonce",
    }
    if "study" in document:
        study = document["study"]
        if not isinstance(study, dict):
            raise TypeError(f"the study value in {target.name} must be a TOML table")
    elif any(key in document for key in known_keys):
        # Retain the flat configuration style accepted by load_settings().
        study = document
    else:
        study = {}
        document["study"] = study
    study["password_hash"] = password_hash
    study["setup_nonce"] = secrets.token_hex(16)
    contents = tomli_w.dumps(document)
    temporary = target.with_name(f".{target.name}.{secrets.token_hex(8)}.tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(contents)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
        target.chmod(0o600)
    finally:
        temporary.unlink(missing_ok=True)
    return target
