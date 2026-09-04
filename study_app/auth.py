from __future__ import annotations

import hashlib
import secrets
import sqlite3
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pwdlib import PasswordHash
from pwdlib.exceptions import PwdlibError

COOKIE_NAME = "study_session"
CSRF_HEADER = "x-study-csrf"


@dataclass(frozen=True)
class Session:
    token: str
    csrf: str
    expires_at: datetime


class SessionStore:
    def __init__(self, path: Path, ttl_days: int, generation: str = ""):
        self.path = path
        self.ttl_days = ttl_days
        self.generation = generation
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.path.parent.chmod(0o700)
        except OSError:
            pass
        if self.path.is_symlink():
            raise ValueError("the session database cannot be a symbolic link")
        self._lock = threading.RLock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY,
                    csrf TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)"
            )
            connection.execute(
                "CREATE TABLE IF NOT EXISTS session_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
            )
            stored_generation = connection.execute(
                "SELECT value FROM session_metadata WHERE key = 'generation'"
            ).fetchone()
            if stored_generation is None or stored_generation[0] != self.generation:
                connection.execute("DELETE FROM sessions")
                connection.execute(
                    "INSERT OR REPLACE INTO session_metadata(key, value) VALUES ('generation', ?)",
                    (self.generation,),
                )
        try:
            self.path.chmod(0o600)
        except OSError:
            pass

    @staticmethod
    def _hash(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def create(self) -> Session:
        token = secrets.token_urlsafe(32)
        csrf = secrets.token_urlsafe(24)
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=self.ttl_days)
        with self._lock, self._connect() as connection:
            connection.execute("DELETE FROM sessions WHERE expires_at <= ?", (now.isoformat(),))
            connection.execute(
                "INSERT INTO sessions(token_hash, csrf, created_at, last_seen_at, expires_at) VALUES (?, ?, ?, ?, ?)",
                (self._hash(token), csrf, now.isoformat(), now.isoformat(), expires.isoformat()),
            )
        return Session(token=token, csrf=csrf, expires_at=expires)

    def get(self, token: str | None) -> Session | None:
        # Cookie values are attacker-controlled. Bound work before hashing or querying.
        if not token or len(token) > 128 or not token.isascii():
            return None
        now = datetime.now(timezone.utc)
        token_hash = self._hash(token)
        with self._lock, self._connect() as connection:
            row = connection.execute(
                "SELECT csrf, expires_at FROM sessions WHERE token_hash = ?", (token_hash,)
            ).fetchone()
            if row is None:
                return None
            expires = datetime.fromisoformat(row["expires_at"])
            if expires <= now:
                connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
                return None
            connection.execute(
                "UPDATE sessions SET last_seen_at = ? WHERE token_hash = ?",
                (now.isoformat(), token_hash),
            )
        return Session(token=token, csrf=row["csrf"], expires_at=expires)

    def revoke(self, token: str | None) -> None:
        if not token or len(token) > 128 or not token.isascii():
            return
        with self._lock, self._connect() as connection:
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (self._hash(token),))

    def revoke_all(self) -> None:
        with self._lock, self._connect() as connection:
            connection.execute("DELETE FROM sessions")


class LoginThrottle:
    def __init__(self, limit: int = 5, window_seconds: int = 300):
        self.limit = limit
        self.window_seconds = window_seconds
        self._attempts: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            attempts = self._attempts[key]
            while attempts and attempts[0] <= now - self.window_seconds:
                attempts.popleft()
            return len(attempts) < self.limit

    def fail(self, key: str) -> None:
        with self._lock:
            self._attempts[key].append(time.monotonic())

    def succeed(self, key: str) -> None:
        with self._lock:
            self._attempts.pop(key, None)


password_hash = PasswordHash.recommended()


def verify_password(plain: str, encoded: str) -> bool:
    try:
        return password_hash.verify(plain, encoded)
    except (PwdlibError, ValueError):
        return False


def make_password_hash(plain: str) -> str:
    return password_hash.hash(plain)
