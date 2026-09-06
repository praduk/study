from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
import threading
import time
import uuid
from bisect import bisect_left
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from itertools import pairwise
from pathlib import Path
from types import TracebackType
from typing import Any, BinaryIO

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows uses msvcrt below.
    fcntl = None  # type: ignore[assignment]

try:
    import msvcrt
except ImportError:  # pragma: no cover - POSIX uses fcntl above.
    msvcrt = None  # type: ignore[assignment]

from .library_validation import (
    COMMUTATIVE_PATH_RE,
    EXCALIDRAW_PATH_RE,
    MEDIA_PATH_RE,
    LibraryValidationError,
    validate_library,
)
from .search_index import LibrarySearchIndex, SearchIndexError

SLUG_RE = re.compile(r"^[a-z][a-z0-9-]*$")
KINDS = {"ax", "df", "rk", "th", "pb"}
ALT_KINDS = {"ax", "df", "th"}
SUPPLEMENT_BY_ENTRY = {"th": "pf", "pb": "sl"}
REVIEW_MODES_BY_KIND = {
    "ax": {"statement"},
    "df": {"statement"},
    "rk": {"statement"},
    "th": {"statement", "proof-plan"},
    "pb": {"solve"},
}
SUPPLEMENT_REVIEW_MODE = {"th": "proof-plan", "pb": "solve"}
SEARCH_STALENESS_SECONDS = 0.25
V2_LIBRARY_ROOT = "library"
V2_ROOT_METADATA = "_library.json"
V2_DEEP_DIRECTORY = "_deep"
V2_FOLDER_METADATA = "_folder.json"
V2_ITEMS_DIRECTORY = "_items"
V2_ENTRY_METADATA = "_entry.json"
V2_ASSETS_DIRECTORY = "assets"
V2_WRITE_JOURNAL = "library-write-journal.tmp"
V2_RANK_GAP = 1 << 32
V2_MAX_RANK = (1 << 63) - 1
V2_MAX_RELATIVE_PATH = 768
V2_ENTRY_PATH_RESERVE = len("/_items/th/") + 80 + 1 + len("formulation.") + 128 + len(".md")


class StoreError(ValueError):
    pass


class _SharedFileLockState:
    def __init__(self) -> None:
        self.thread_lock = threading.RLock()
        self.depth = 0
        self.stream: BinaryIO | None = None


_FILE_LOCK_STATES_GUARD = threading.Lock()
_FILE_LOCK_STATES: dict[Path, _SharedFileLockState] = {}


class _InterprocessRLock:
    """Reentrant in-process lock backed by one advisory lock per data root."""

    def __init__(self, path: Path):
        self.path = path
        key = path.resolve()
        with _FILE_LOCK_STATES_GUARD:
            self._state = _FILE_LOCK_STATES.setdefault(key, _SharedFileLockState())

    def _open_lock_file(self) -> BinaryIO:
        flags = os.O_CREAT | os.O_RDWR
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if os.name != "nt" and os.open in os.supports_dir_fd:
                parent_flags = os.O_RDONLY
                if hasattr(os, "O_DIRECTORY"):
                    parent_flags |= os.O_DIRECTORY
                if hasattr(os, "O_NOFOLLOW"):
                    parent_flags |= os.O_NOFOLLOW
                parent_descriptor = os.open(self.path.parent, parent_flags)
                try:
                    descriptor = os.open(
                        self.path.name,
                        flags,
                        0o600,
                        dir_fd=parent_descriptor,
                    )
                finally:
                    os.close(parent_descriptor)
            else:  # pragma: no cover - POSIX exercises the dirfd-safe path.
                if self.path.parent.is_symlink():
                    raise OSError("authored-data runtime directory is a symbolic link")
                descriptor = os.open(self.path, flags, 0o600)
        except OSError as exc:
            raise StoreError("cannot open the authored-data mutation lock") from exc
        return os.fdopen(descriptor, "r+b", buffering=0)

    @staticmethod
    def _acquire_file(stream: BinaryIO) -> None:
        if fcntl is not None:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            return
        if msvcrt is not None:  # pragma: no cover - exercised on Windows.
            if os.fstat(stream.fileno()).st_size == 0:
                stream.write(b"\0")
                stream.flush()
            stream.seek(0)
            while True:
                try:
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                    return
                except OSError:
                    time.sleep(0.05)
        raise StoreError("this platform cannot lock authored data safely")

    @staticmethod
    def _release_file(stream: BinaryIO) -> None:
        if fcntl is not None:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
        elif msvcrt is not None:  # pragma: no cover - exercised on Windows.
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)

    def __enter__(self):
        state = self._state
        state.thread_lock.acquire()
        try:
            if state.depth == 0:
                stream = self._open_lock_file()
                try:
                    self._acquire_file(stream)
                except BaseException:
                    stream.close()
                    raise
                state.stream = stream
            state.depth += 1
            return self
        except BaseException:
            state.thread_lock.release()
            raise

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        state = self._state
        try:
            state.depth -= 1
            if state.depth == 0:
                stream = state.stream
                state.stream = None
                if stream is not None:
                    try:
                        self._release_file(stream)
                    finally:
                        stream.close()
        finally:
            state.thread_lock.release()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _atomic_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _fsync_directory(path: Path) -> None:
    """Durably record directory-entry changes where directory fsync is supported."""
    if os.name == "nt":  # pragma: no cover - Windows cannot open directories this way.
        return
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_json(path: Path, value: Any) -> None:
    _atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def _slug(value: str, label: str = "slug") -> str:
    value = value.strip().lower()
    if not SLUG_RE.fullmatch(value):
        raise StoreError(
            f"{label} must start with a letter and use lowercase letters, digits, or hyphens"
        )
    return value


class LibraryStore:
    """Git-friendly content store with atomic metadata and Markdown writes."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir.resolve()
        self.library_path = self.data_dir / "library.json"
        self.macros_path = self.data_dir / "macros.json"
        self.legacy_content_dir = self.data_dir / "content"
        self.library_dir = self.data_dir / V2_LIBRARY_ROOT
        self.media_dir = self.data_dir / "media"
        self.diagram_dir = self.data_dir / "diagrams"
        self.templates_dir = self.data_dir / "excalidraw" / "templates"
        self.exports_dir = self.data_dir / "exports"
        self.runtime_dir = self.data_dir / "runtime"
        self._lock = _InterprocessRLock(self.runtime_dir / "library-lock.tmp")
        self._search_index: LibrarySearchIndex | None = None
        self._search_signatures: dict[Path, tuple[int, int, int, int, int] | None] = {}
        self._next_search_staleness_check = 0.0
        self._search_build_count = 0
        self._search_content_read_count = 0
        self._library_cache: dict[str, Any] | None = None
        self._library_signatures: dict[
            Path, tuple[int, int, int, int, int] | None
        ] = {}
        self._v2_folder_paths: dict[str, Path] = {}
        self._v2_entry_paths: dict[str, Path] = {}
        self._v2_folder_ranks: dict[str, int] = {}
        self._v2_entry_ranks: dict[str, int] = {}
        self._v2_signature_paths: set[Path] = set()
        self._v2_transaction_depth = 0
        with self._lock:
            self._ensure_layout()

    def _format_version(self) -> int:
        if not self.library_path.exists():
            return 1
        try:
            with self.library_path.open(encoding="utf-8") as stream:
                value = json.load(stream)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
            raise StoreError("library.json is unreadable or invalid") from exc
        if not isinstance(value, dict) or value.get("version") not in {1, 2}:
            raise StoreError("unsupported library version")
        if value["version"] == 2 and value != {"version": 2, "root": V2_LIBRARY_ROOT}:
            raise StoreError("library.json has an invalid version 2 marker")
        return int(value["version"])

    @property
    def content_dir(self) -> Path:
        return self.library_dir if self._format_version() == 2 else self.legacy_content_dir

    @property
    def format_version(self) -> int:
        return self._format_version()

    @property
    def mutation_lock(self) -> Any:
        """Application-wide lock shared with review and Git mutations."""
        return self._lock

    def _ensure_layout(self) -> None:
        root = self.data_dir.resolve()
        common_directories = (
            self.data_dir,
            self.media_dir,
            self.diagram_dir,
            self.templates_dir,
            self.exports_dir,
            self.runtime_dir,
        )
        for directory in common_directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                raise StoreError(f"cannot create data directory: {directory.name}") from exc
            resolved = directory.resolve()
            if not resolved.is_dir() or (
                directory != self.data_dir and root not in resolved.parents
            ):
                raise StoreError(
                    f"data directory escapes the configured data root: {directory.name}"
                )
        for metadata in (self.library_path, self.macros_path):
            if metadata.is_symlink():
                raise StoreError(f"{metadata.name} cannot be a symbolic link")
        if not self.library_path.exists():
            if self.legacy_content_dir.exists():
                raise StoreError(
                    "library.json is missing while the legacy content directory exists"
                )
            if self.library_dir.is_symlink():
                raise StoreError("version 2 library root cannot be a symbolic link")
            try:
                self.library_dir.mkdir(parents=False, exist_ok=True)
                children = list(self.library_dir.iterdir())
            except OSError as exc:
                raise StoreError("cannot initialize the version 2 library root") from exc
            root_metadata = self.library_dir / V2_ROOT_METADATA
            if children:
                if children != [root_metadata] or self._read_json_object(
                    root_metadata, "version 2 root metadata"
                ) != {"version": 1}:
                    raise StoreError("library.json is missing beside a nonempty library tree")
            else:
                _atomic_json(root_metadata, {"version": 1})
            _atomic_json(self.library_path, {"version": 2, "root": V2_LIBRARY_ROOT})
        version = self._format_version()
        if version == 2:
            self._recover_v2_write()
        content_root = self.library_dir if version == 2 else self.legacy_content_dir
        if version == 1:
            try:
                content_root.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                raise StoreError(f"cannot create data directory: {content_root.name}") from exc
        elif not content_root.exists():
            raise StoreError("version 2 library root is missing")
        resolved_content_root = content_root.resolve()
        if (
            not resolved_content_root.is_dir()
            or root not in resolved_content_root.parents
            or content_root.is_symlink()
        ):
            raise StoreError(f"data directory escapes the configured data root: {content_root.name}")
        if not self.macros_path.exists():
            _atomic_json(self.macros_path, {"version": 1, "macros": {}})

    def _recover_v2_write(self) -> None:
        journal = self.runtime_dir / V2_WRITE_JOURNAL
        if not journal.exists():
            return
        value = self._read_json_object(journal, "version 2 write journal")
        if set(value) != {"version", "state", "backup"} or value.get("version") != 1:
            raise StoreError("version 2 write journal is invalid")
        state = value.get("state")
        backup_name = value.get("backup")
        if state not in {"prepared", "committed"} or not isinstance(
            backup_name, str
        ) or not re.fullmatch(r"library-write-backup-[a-f0-9]{32}\.tmp", backup_name):
            raise StoreError("version 2 write journal is invalid")
        backup = self.runtime_dir / backup_name
        if backup.is_symlink():
            raise StoreError("version 2 write backup is unsafe")

        if state == "prepared" and backup.is_dir():
            self._read_v2(backup)
            failed = self.runtime_dir / f"library-recovery-failed-{uuid.uuid4().hex}.tmp"
            try:
                if self.library_dir.exists() or self.library_dir.is_symlink():
                    os.replace(self.library_dir, failed)
                os.replace(backup, self.library_dir)
                self._read_v2()
            except OSError as exc:
                raise StoreError("cannot restore the interrupted version 2 write") from exc
            journal.unlink(missing_ok=True)
            # The displaced tree may contain a direct edit made after the
            # process stopped. Keep it inert under ignored runtime storage
            # rather than guessing that it is safe to delete.
            return

        # A missing prepared backup means normal rollback already restored the
        # live tree. A committed journal means the validated live tree won.
        self._read_v2()
        if backup.exists():
            shutil.rmtree(backup, ignore_errors=True)
        journal.unlink(missing_ok=True)

    def ensure_layout(self) -> None:
        """Recheck/recreate safe auxiliary directories after a Git fast-forward."""
        with self._lock:
            self._ensure_layout()

    def _library_cache_is_current(self) -> bool:
        if (
            self._library_cache is None
            or self._library_cache.get("version") != 2
            or not self._library_signatures
        ):
            return False
        return all(
            self._file_signature(path) == signature
            for path, signature in self._library_signatures.items()
        )

    def _invalidate_library_cache(self) -> None:
        self._library_cache = None
        self._library_signatures = {}

    def _cache_validated_library(
        self,
        library: dict[str, Any],
        *,
        signatures: dict[Path, tuple[int, int, int, int, int] | None],
    ) -> None:
        # Version 1 keeps authored files in several separate legacy roots.
        # Revalidating it preserves the existing fail-closed behavior; the
        # performance-sensitive current format is the self-contained v2 tree.
        if library["version"] != 2:
            self._invalidate_library_cache()
            return
        if any(signature is None for signature in signatures.values()):
            raise StoreError("library changed while loading")
        self._library_cache = copy.deepcopy(library)
        # Publish the exact signatures that bracketed validation. Never rescan
        # here: doing so could attach post-validation signatures to stale data.
        self._library_signatures = dict(signatures)

    def _read(self) -> dict[str, Any]:
        if self._library_cache_is_current():
            return copy.deepcopy(self._library_cache)

        # A manual edit or Git replacement can race a read. Cache only a
        # completely validated snapshot whose on-disk signatures stayed fixed
        # for the duration of the parse.
        for attempt in range(2):
            library_before = self._file_signature(self.library_path)
            version_before = self._format_version()
            v2_tree_before = self._v2_tree_signatures() if version_before == 2 else {}
            library = self._read_uncached()
            library_after = self._file_signature(self.library_path)
            v2_tree_after = self._v2_tree_signatures() if library["version"] == 2 else {}
            if library_before == library_after and v2_tree_before == v2_tree_after:
                signatures = {self.library_path: library_after, **v2_tree_after}
                signatures.update(
                    {
                        path: self._file_signature(path)
                        for path in self._v2_signature_paths
                        if path not in signatures
                    }
                )
                self._cache_validated_library(
                    library,
                    signatures=signatures,
                )
                return library
            if attempt == 1:
                raise StoreError("library changed repeatedly while loading")
        raise AssertionError("unreachable")

    def _read_uncached(self) -> dict[str, Any]:
        try:
            with self.library_path.open(encoding="utf-8") as stream:
                library = json.load(stream)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
            raise StoreError("library.json is unreadable or invalid") from exc
        if not isinstance(library, dict) or library.get("version") not in {1, 2}:
            raise StoreError("unsupported library version")
        if library.get("version") == 2:
            if library != {"version": 2, "root": V2_LIBRARY_ROOT}:
                raise StoreError("library.json has an invalid version 2 marker")
            return self._read_v2()
        if not isinstance(library.get("folders"), list) or not isinstance(
            library.get("entries"), list
        ):
            raise StoreError("library.json must contain folder and entry lists")
        try:
            validate_library(
                library,
                self.data_dir,
                self.content_dir,
                self.media_dir,
                self.diagram_dir,
            )
        except LibraryValidationError as exc:
            raise StoreError(str(exc)) from exc
        return library

    @staticmethod
    def _read_json_object(path: Path, label: str) -> dict[str, Any]:
        if path.is_symlink() or not path.is_file():
            raise StoreError(f"{label} is missing or unsafe")
        try:
            with path.open(encoding="utf-8") as stream:
                value = json.load(stream)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
            raise StoreError(f"{label} is unreadable or invalid") from exc
        if not isinstance(value, dict):
            raise StoreError(f"{label} must contain a JSON object")
        return value

    def _v2_data_relative(self, path: Path, *, logical_path: Path | None = None) -> str:
        try:
            relative = path.relative_to(self.data_dir).as_posix()
        except ValueError as exc:
            raise StoreError("version 2 library path escapes data") from exc
        try:
            logical_relative = (logical_path or path).relative_to(self.data_dir).as_posix()
        except ValueError as exc:
            raise StoreError("version 2 logical library path escapes data") from exc
        if len(logical_relative.encode("utf-8")) > V2_MAX_RELATIVE_PATH:
            raise StoreError(
                "version 2 library path exceeds "
                f"{V2_MAX_RELATIVE_PATH} UTF-8 bytes: {logical_relative}"
            )
        return relative

    @staticmethod
    def _v2_rank(value: Any, label: str) -> int:
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or not 0 <= value <= V2_MAX_RANK
        ):
            raise StoreError(f"{label} rank must be an integer from 0 through {V2_MAX_RANK}")
        return value

    @staticmethod
    def _reject_unexpected_keys(
        value: dict[str, Any], allowed: set[str], label: str
    ) -> None:
        unexpected = sorted(set(value) - allowed)
        if unexpected:
            raise StoreError(f"{label} has unexpected field: {unexpected[0]}")

    def _read_v2(self, root: Path | None = None) -> dict[str, Any]:
        library_root = (root or self.library_dir).resolve()
        if (root or self.library_dir).is_symlink() or not library_root.is_dir():
            raise StoreError("version 2 library root is missing or unsafe")
        if self.data_dir not in library_root.parents:
            raise StoreError("version 2 library root escapes data")

        folders: list[dict[str, Any]] = []
        entries: list[dict[str, Any]] = []
        folder_paths: dict[str, Path] = {}
        entry_paths: dict[str, Path] = {}
        folder_ranks: dict[str, int] = {}
        entry_ranks: dict[str, int] = {}
        signature_paths: set[Path] = {library_root}

        def logical_path(path: Path) -> Path:
            try:
                return self.library_dir / path.relative_to(library_root)
            except ValueError as exc:
                raise StoreError("version 2 path escapes its library root") from exc

        root_metadata_path = library_root / V2_ROOT_METADATA
        root_metadata = self._read_json_object(root_metadata_path, "version 2 root metadata")
        if root_metadata != {"version": 1}:
            raise StoreError("version 2 root metadata is invalid")
        signature_paths.add(root_metadata_path.resolve())

        def checked_children(directory: Path, label: str) -> list[Path]:
            try:
                children = sorted(directory.iterdir(), key=lambda path: path.name)
            except OSError as exc:
                raise StoreError(f"cannot read {label}") from exc
            for child in children:
                if child.is_symlink():
                    raise StoreError(f"symbolic links are not allowed in the version 2 library: {child.name}")
            signature_paths.add(directory)
            return children

        def read_entry(entry_dir: Path, folder_id: str, kind: str, tag: str) -> None:
            self._v2_data_relative(entry_dir, logical_path=logical_path(entry_dir))
            metadata_path = entry_dir / V2_ENTRY_METADATA
            metadata = self._read_json_object(metadata_path, f"entry metadata at {entry_dir.name}")
            self._reject_unexpected_keys(
                metadata,
                {
                    "version",
                    "id",
                    "title",
                    "rank",
                    "header",
                    "problem_family",
                    "confusable_with",
                    "formulations",
                    "supplements",
                    "assets",
                    "created_at",
                    "updated_at",
                },
                f"entry metadata at {entry_dir.name}",
            )
            if metadata.get("version") != 1:
                raise StoreError(f"entry metadata at {entry_dir.name} has an unsupported version")
            entry_id = metadata.get("id")
            if not isinstance(entry_id, str):
                raise StoreError(f"entry metadata at {entry_dir.name} has an invalid id")
            rank = self._v2_rank(metadata.get("rank"), f"entry {entry_id}")
            entry = {
                key: copy.deepcopy(value)
                for key, value in metadata.items()
                if key not in {"version", "rank"}
            }
            entry.update(
                {
                    "id": entry_id,
                    "folder_id": folder_id,
                    "kind": kind,
                    "tag": tag,
                    "order": 0,
                }
            )
            referenced_files: set[Path] = set()
            for group_name in ("formulations", "supplements"):
                group = entry.get(group_name)
                if not isinstance(group, list):
                    raise StoreError(f"entry {entry_id} {group_name} must be a list")
                for variant in group:
                    if not isinstance(variant, dict):
                        raise StoreError(f"entry {entry_id} {group_name} must contain objects")
                    local = variant.get("file")
                    if (
                        not isinstance(local, str)
                        or not local
                        or "\\" in local
                        or Path(local).name != local
                        or Path(local).suffix.casefold() != ".md"
                    ):
                        raise StoreError(f"entry {entry_id} has an invalid colocated Markdown path")
                    source = entry_dir / local
                    if source.is_symlink() or not source.is_file():
                        raise StoreError(f"entry {entry_id} Markdown is missing or unsafe: {local}")
                    referenced_files.add(source.resolve())
                    signature_paths.add(source.resolve())
                    resolved_source = source.resolve()
                    variant["file"] = self._v2_data_relative(
                        resolved_source, logical_path=logical_path(resolved_source)
                    )

            assets = entry.get("assets")
            if not isinstance(assets, list):
                raise StoreError(f"entry {entry_id} assets must be a list")
            referenced_assets: set[Path] = set()
            for asset in assets:
                if not isinstance(asset, dict):
                    raise StoreError(f"entry {entry_id} assets must contain objects")
                for field, route_prefix in (("path", "media"), ("source", "diagrams")):
                    if field not in asset:
                        continue
                    local = asset[field]
                    local_path = Path(local) if isinstance(local, str) else Path()
                    is_local = (
                        isinstance(local, str)
                        and local
                        and "\\" not in local
                        and len(local_path.parts) == 2
                        and local_path.parts[0] == V2_ASSETS_DIRECTORY
                        and local_path.name not in {"", ".", ".."}
                    )
                    if is_local:
                        source = entry_dir / local_path
                        if source.is_symlink() or not source.is_file():
                            raise StoreError(
                                f"entry {entry_id} asset is missing or unsafe: {local}"
                            )
                        resolved_source = source.resolve()
                        referenced_assets.add(resolved_source)
                        signature_paths.add(resolved_source)
                        self._v2_data_relative(
                            resolved_source, logical_path=logical_path(resolved_source)
                        )
                        asset[field] = f"{route_prefix}/{local_path.name}"
                        continue

                    kind = asset.get("kind")
                    pattern = MEDIA_PATH_RE if field == "path" else None
                    global_root = self.media_dir if field == "path" else self.diagram_dir
                    suffixes = {".png", ".jpg", ".jpeg", ".webp"}
                    if field == "source" and kind == "excalidraw":
                        pattern = EXCALIDRAW_PATH_RE
                        suffixes = {".excalidraw"}
                    elif field == "source" and kind == "commutative":
                        pattern = COMMUTATIVE_PATH_RE
                        suffixes = {".json"}
                    if (
                        not isinstance(local, str)
                        or pattern is None
                        or pattern.fullmatch(local) is None
                    ):
                        raise StoreError(
                            f"entry {entry_id} has an invalid colocated asset path"
                        )
                    try:
                        source = self._safe_owned_file(local, global_root, suffixes)
                    except StoreError as exc:
                        raise StoreError(
                            f"entry {entry_id} legacy asset is missing or unsafe: {local}"
                        ) from exc
                    signature_paths.add(source)

            for child in checked_children(entry_dir, f"entry directory {entry_id}"):
                if child == metadata_path:
                    signature_paths.add(child.resolve())
                    continue
                if child.is_file() and child.resolve() in referenced_files:
                    continue
                if child.name == V2_ASSETS_DIRECTORY and child.is_dir():
                    if not referenced_assets:
                        raise StoreError(
                            f"entry {entry_id} contains an unrecognized path: {child.name}"
                        )
                    for asset_file in checked_children(
                        child, f"assets for entry {entry_id}"
                    ):
                        if not asset_file.is_file() or asset_file.resolve() not in referenced_assets:
                            raise StoreError(
                                f"entry {entry_id} contains an unrecognized asset: "
                                f"{asset_file.name}"
                            )
                    continue
                raise StoreError(f"entry {entry_id} contains an unrecognized path: {child.name}")

            entry["review_modes"] = self.review_modes_for_entry(entry)
            entries.append(entry)
            if entry_id in entry_paths:
                raise StoreError(f"duplicate record id: {entry_id}")
            entry_paths[entry_id] = entry_dir.resolve()
            entry_ranks[entry_id] = rank

        def read_items(items_dir: Path, folder_id: str) -> None:
            if items_dir.is_symlink() or not items_dir.is_dir():
                raise StoreError(f"folder {folder_id} has an unsafe {V2_ITEMS_DIRECTORY} directory")
            for kind_dir in checked_children(items_dir, f"items for folder {folder_id}"):
                kind = kind_dir.name
                if not kind_dir.is_dir() or kind not in KINDS:
                    raise StoreError(f"folder {folder_id} has an invalid item kind path: {kind}")
                for entry_dir in checked_children(kind_dir, f"{kind} items for folder {folder_id}"):
                    tag = entry_dir.name
                    if not entry_dir.is_dir() or not SLUG_RE.fullmatch(tag):
                        raise StoreError(f"folder {folder_id} has an invalid entry tag path: {tag}")
                    read_entry(entry_dir, folder_id, kind, tag)

        def read_folder(
            folder_dir: Path,
            parent_id: str | None,
            depth: int,
            *,
            deep: bool = False,
        ) -> None:
            if depth > 64:
                raise StoreError("folder nesting cannot exceed 64 levels")
            directory_name = folder_dir.name
            if not folder_dir.is_dir() or (
                not deep and not SLUG_RE.fullmatch(directory_name)
            ):
                raise StoreError(f"invalid version 2 folder path: {directory_name}")
            self._v2_data_relative(folder_dir, logical_path=logical_path(folder_dir))
            metadata_path = folder_dir / V2_FOLDER_METADATA
            metadata = self._read_json_object(
                metadata_path, f"folder metadata at {directory_name}"
            )
            allowed = {
                "version",
                "id",
                "name",
                "rank",
                "review_enabled",
                "created_at",
                "updated_at",
            }
            if deep:
                allowed.update({"slug", "parent_id"})
            self._reject_unexpected_keys(
                metadata,
                allowed,
                f"folder metadata at {directory_name}",
            )
            if metadata.get("version") != 1:
                raise StoreError(
                    f"folder metadata at {directory_name} has an unsupported version"
                )
            folder_id = metadata.get("id")
            if not isinstance(folder_id, str):
                raise StoreError(f"folder metadata at {directory_name} has an invalid id")
            if deep:
                slug = metadata.get("slug")
                match = re.fullmatch(
                    r"([a-f0-9]{32})-([a-z][a-z0-9-]{0,63})", directory_name
                )
                if not isinstance(slug, str) or match is None or match.group(2) != slug:
                    raise StoreError(f"deep folder path is invalid: {directory_name}")
                parent_id = metadata.get("parent_id")
            else:
                slug = directory_name
            rank = self._v2_rank(metadata.get("rank"), f"folder {folder_id}")
            folder = {
                key: copy.deepcopy(value)
                for key, value in metadata.items()
                if key not in {"version", "rank", "slug", "parent_id"}
            }
            folder.update(
                {
                    "id": folder_id,
                    "slug": slug,
                    "parent_id": parent_id,
                    "order": 0,
                }
            )
            folders.append(folder)
            if folder_id in folder_paths:
                raise StoreError(f"duplicate record id: {folder_id}")
            folder_paths[folder_id] = folder_dir.resolve()
            folder_ranks[folder_id] = rank
            signature_paths.add(metadata_path.resolve())

            for child in checked_children(folder_dir, f"folder {folder_id}"):
                if child == metadata_path:
                    continue
                if child.name == V2_ITEMS_DIRECTORY:
                    read_items(child, folder_id)
                    continue
                if not deep and child.is_dir() and SLUG_RE.fullmatch(child.name):
                    read_folder(child, folder_id, depth + 1)
                    continue
                raise StoreError(f"folder {folder_id} contains an unrecognized path: {child.name}")

        for root_folder in checked_children(library_root, "version 2 library root"):
            if root_folder == root_metadata_path:
                continue
            if root_folder.name == V2_DEEP_DIRECTORY:
                if not root_folder.is_dir():
                    raise StoreError("version 2 deep folder container is invalid")
                for deep_folder in checked_children(
                    root_folder, "version 2 deep folder container"
                ):
                    read_folder(deep_folder, None, 1, deep=True)
                continue
            if not root_folder.is_dir() or not SLUG_RE.fullmatch(root_folder.name):
                raise StoreError(f"invalid version 2 root folder path: {root_folder.name}")
            read_folder(root_folder, None, 1)

        for parent_id in {None, *(folder["id"] for folder in folders)}:
            siblings = [folder for folder in folders if folder.get("parent_id") == parent_id]
            siblings.sort(key=lambda folder: (folder_ranks[folder["id"]], folder["id"]))
            for order, folder in enumerate(siblings):
                folder["order"] = order
        for folder in folders:
            direct = [entry for entry in entries if entry["folder_id"] == folder["id"]]
            direct.sort(key=lambda entry: (entry_ranks[entry["id"]], entry["id"]))
            for order, entry in enumerate(direct):
                entry["order"] = order

        library = {"version": 2, "folders": folders, "entries": entries}
        try:
            validate_library(
                library,
                self.data_dir,
                library_root,
                self.media_dir,
                self.diagram_dir,
            )
        except LibraryValidationError as exc:
            raise StoreError(str(exc)) from exc
        desired_folder_paths = self._desired_v2_folder_paths(library, library_root)
        for folder_id, actual_path in folder_paths.items():
            if desired_folder_paths.get(folder_id, Path()) != actual_path:
                raise StoreError(f"folder {folder_id} is stored at a noncanonical path")
        self._v2_folder_paths = folder_paths
        self._v2_entry_paths = entry_paths
        self._v2_folder_ranks = folder_ranks
        self._v2_entry_ranks = entry_ranks
        self._v2_signature_paths = signature_paths
        return library

    def _desired_v2_folder_paths(
        self, library: dict[str, Any], root: Path | None = None
    ) -> dict[str, Path]:
        folders = {folder["id"]: folder for folder in library["folders"]}
        result: dict[str, Path] = {}
        namespaces: dict[str, tuple[str, ...]] = {}
        library_root = root or self.library_dir

        def namespace(folder_id: str, pending: set[str]) -> tuple[str, ...]:
            if folder_id in namespaces:
                return namespaces[folder_id]
            if folder_id in pending:
                raise StoreError("folder cycle detected")
            folder = folders.get(folder_id)
            if folder is None:
                raise StoreError("folder not found")
            parent_id = folder.get("parent_id")
            prefix = () if parent_id is None else namespace(parent_id, pending | {folder_id})
            namespaces[folder_id] = (*prefix, folder["slug"])
            return namespaces[folder_id]

        for folder_id in folders:
            segments = namespace(folder_id, set())
            literal_relative = Path(V2_LIBRARY_ROOT).joinpath(*segments).as_posix()
            if (
                len(literal_relative.encode("utf-8")) + V2_ENTRY_PATH_RESERVE
                <= V2_MAX_RELATIVE_PATH
            ):
                relative = Path(*segments)
            else:
                full_namespace = ":".join(segments)
                digest = hashlib.sha256(full_namespace.encode("utf-8")).hexdigest()[:32]
                relative = Path(V2_DEEP_DIRECTORY) / f"{digest}-{segments[-1]}"
            path = library_root / relative
            self._v2_data_relative(self.library_dir / relative)
            if path in result.values():
                raise StoreError("version 2 folder path hash collision")
            result[folder_id] = path
        return result

    def _desired_v2_entry_paths(
        self, library: dict[str, Any], folder_paths: dict[str, Path]
    ) -> dict[str, Path]:
        result: dict[str, Path] = {}
        for entry in library["entries"]:
            path = (
                folder_paths[entry["folder_id"]]
                / V2_ITEMS_DIRECTORY
                / entry["kind"]
                / entry["tag"]
            )
            self._v2_data_relative(path)
            result[entry["id"]] = path
        return result

    @staticmethod
    def _longest_increasing_rank_anchors(
        item_ids: list[str], existing: dict[str, int]
    ) -> list[int]:
        tails: list[int] = []
        tail_indices: list[int] = []
        previous: list[int | None] = [None] * len(item_ids)
        for index, item_id in enumerate(item_ids):
            if item_id not in existing:
                continue
            value = existing[item_id]
            position = bisect_left(tails, value)
            if position == len(tails):
                tails.append(value)
                tail_indices.append(index)
            else:
                tails[position] = value
                tail_indices[position] = index
            if position:
                previous[index] = tail_indices[position - 1]
        if not tail_indices:
            return []
        anchors: list[int] = []
        cursor: int | None = tail_indices[-1]
        while cursor is not None:
            anchors.append(cursor)
            cursor = previous[cursor]
        anchors.reverse()
        return anchors

    @classmethod
    def _sparse_ranks(cls, item_ids: list[str], existing: dict[str, int]) -> dict[str, int]:
        if not item_ids:
            return {}
        anchors = cls._longest_increasing_rank_anchors(item_ids, existing)
        result = {item_ids[index]: existing[item_ids[index]] for index in anchors}
        boundaries = [(-1, 0), *((index, existing[item_ids[index]]) for index in anchors)]
        boundaries.append((len(item_ids), V2_MAX_RANK + 1))
        for (left_index, left_rank), (right_index, right_rank) in pairwise(boundaries):
            count = right_index - left_index - 1
            if not count:
                continue
            available = right_rank - left_rank - 1
            if available < count:
                return {
                    item_id: (index + 1) * V2_RANK_GAP
                    for index, item_id in enumerate(item_ids)
                }
            spacing = max(1, (right_rank - left_rank) // (count + 1))
            for offset in range(1, count + 1):
                result[item_ids[left_index + offset]] = left_rank + spacing * offset
        if any(rank > V2_MAX_RANK for rank in result.values()):
            return {
                item_id: (index + 1) * V2_RANK_GAP for index, item_id in enumerate(item_ids)
            }
        return result

    @staticmethod
    def _write_json_if_changed(path: Path, value: dict[str, Any]) -> None:
        encoded = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        try:
            if not path.is_symlink() and path.read_text(encoding="utf-8") == encoded:
                return
        except FileNotFoundError:
            pass
        except (OSError, UnicodeDecodeError) as exc:
            raise StoreError(f"cannot inspect metadata before writing: {path.name}") from exc
        _atomic_text(path, encoded)

    def _write_json_if_signature_matches(
        self,
        path: Path,
        value: dict[str, Any],
        expected_signature: tuple[int, int, int, int, int] | None,
    ) -> None:
        """Replace one JSON file only if it is still the version we validated."""
        encoded = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
        temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
        try:
            before = self._file_signature(path)
            try:
                current = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                raise StoreError(f"cannot inspect metadata before writing: {path.name}") from exc
            after = self._file_signature(path)
            if before != expected_signature or after != expected_signature:
                raise StoreError("folder metadata changed before saving its review preference")
            if current == encoded:
                return
            with temporary.open("x", encoding="utf-8") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            if self._file_signature(path) != expected_signature:
                raise StoreError("folder metadata changed before saving its review preference")
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)

    @staticmethod
    def _v2_folder_metadata(
        folder: dict[str, Any], rank: int, path: Path
    ) -> dict[str, Any]:
        value = {
            "version": 1,
            "id": folder["id"],
            "name": folder["name"],
            "rank": rank,
            "review_enabled": folder["review_enabled"],
        }
        if path.parent.name == V2_DEEP_DIRECTORY:
            value["slug"] = folder["slug"]
            value["parent_id"] = folder.get("parent_id")
        for field in ("created_at", "updated_at"):
            if field in folder:
                value[field] = folder[field]
        return value

    @staticmethod
    def _v2_entry_metadata(
        entry: dict[str, Any], rank: int, entry_path: Path
    ) -> dict[str, Any]:
        value: dict[str, Any] = {
            "version": 1,
            "id": entry["id"],
            "title": entry["title"],
            "rank": rank,
            "header": entry.get("header", ""),
            "problem_family": entry.get("problem_family", ""),
            "confusable_with": copy.deepcopy(entry.get("confusable_with", [])),
            "formulations": copy.deepcopy(entry.get("formulations", [])),
            "supplements": copy.deepcopy(entry.get("supplements", [])),
            "assets": copy.deepcopy(entry.get("assets", [])),
        }
        for variant in (*value["formulations"], *value["supplements"]):
            variant.pop("content", None)
            variant.pop("canonical_tag", None)
            variant["file"] = Path(variant["file"]).name
        for asset in value["assets"]:
            for field in ("path", "source"):
                if field in asset:
                    filename = Path(asset[field]).name
                    local = entry_path / V2_ASSETS_DIRECTORY / filename
                    if local.exists() or local.is_symlink():
                        asset[field] = f"{V2_ASSETS_DIRECTORY}/{filename}"
        for field in ("created_at", "updated_at"):
            if field in entry:
                value[field] = entry[field]
        return value

    def _trash_v2_path(self, path: Path, trash_root: Path) -> None:
        if not path.exists():
            return
        trash_root.mkdir(parents=True, exist_ok=True)
        target = trash_root / uuid.uuid4().hex
        try:
            os.replace(path, target)
        except OSError as exc:
            raise StoreError(f"cannot safely remove version 2 path: {path.name}") from exc

    def _apply_v2_write(self, library: dict[str, Any]) -> None:
        old_folder_paths = dict(self._v2_folder_paths)
        old_entry_paths = dict(self._v2_entry_paths)
        desired_folder_paths = self._desired_v2_folder_paths(library)
        desired_entry_paths = self._desired_v2_entry_paths(library, desired_folder_paths)
        trash_root = self.runtime_dir / f"library-write-{uuid.uuid4().hex}.tmp"

        old_entry_ids = set(old_entry_paths)
        desired_entry_ids = set(desired_entry_paths)
        for entry_id in sorted(old_entry_ids - desired_entry_ids):
            self._trash_v2_path(old_entry_paths[entry_id], trash_root)

        old_folder_ids = set(old_folder_paths)
        desired_folder_ids = set(desired_folder_paths)
        deleted_folders = old_folder_ids - desired_folder_ids
        deleted_roots = [
            folder_id
            for folder_id in deleted_folders
            if not any(
                other != folder_id
                and old_folder_paths[other] in old_folder_paths[folder_id].parents
                for other in deleted_folders
            )
        ]
        for folder_id in sorted(deleted_roots, key=lambda value: len(old_folder_paths[value].parts)):
            self._trash_v2_path(old_folder_paths[folder_id], trash_root)

        for path in sorted(desired_folder_paths.values(), key=lambda value: len(value.parts)):
            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                raise StoreError(f"cannot create version 2 folder path: {path.name}") from exc
            if path.is_symlink() or not path.is_dir():
                raise StoreError(f"version 2 folder path is unsafe: {path.name}")

        for entry_id, desired in desired_entry_paths.items():
            old = old_entry_paths.get(entry_id)
            if old is not None and old != desired and old.exists():
                desired.parent.mkdir(parents=True, exist_ok=True)
                if desired.exists():
                    raise StoreError(f"version 2 entry destination already exists: {desired.name}")
                try:
                    os.replace(old, desired)
                except OSError as exc:
                    raise StoreError(f"cannot move version 2 entry: {desired.name}") from exc
            else:
                desired.mkdir(parents=True, exist_ok=True)

        folder_rank_by_id: dict[str, int] = {}
        for parent_id in {None, *(folder["id"] for folder in library["folders"])}:
            siblings = sorted(
                (folder for folder in library["folders"] if folder.get("parent_id") == parent_id),
                key=lambda folder: (folder.get("order", 0), folder["id"]),
            )
            folder_rank_by_id.update(
                self._sparse_ranks(
                    [folder["id"] for folder in siblings], self._v2_folder_ranks
                )
            )

        entry_rank_by_id: dict[str, int] = {}
        for folder in library["folders"]:
            direct = sorted(
                (entry for entry in library["entries"] if entry["folder_id"] == folder["id"]),
                key=lambda entry: (entry.get("order", 0), entry["id"]),
            )
            entry_rank_by_id.update(
                self._sparse_ranks([entry["id"] for entry in direct], self._v2_entry_ranks)
            )

        for folder in library["folders"]:
            path = desired_folder_paths[folder["id"]]
            self._write_json_if_changed(
                path / V2_FOLDER_METADATA,
                self._v2_folder_metadata(
                    folder, folder_rank_by_id[folder["id"]], path
                ),
            )
        for folder_id, old in old_folder_paths.items():
            desired = desired_folder_paths.get(folder_id)
            if desired is not None and old != desired:
                try:
                    (old / V2_FOLDER_METADATA).unlink(missing_ok=True)
                except OSError as exc:
                    raise StoreError(f"cannot retire old version 2 folder metadata: {old.name}") from exc

        for entry in library["entries"]:
            entry_path = desired_entry_paths[entry["id"]]
            for variant in (*entry.get("formulations", []), *entry.get("supplements", [])):
                local = Path(variant["file"]).name
                variant["file"] = self._v2_data_relative(entry_path / local)
            self._write_json_if_changed(
                entry_path / V2_ENTRY_METADATA,
                self._v2_entry_metadata(
                    entry, entry_rank_by_id[entry["id"]], entry_path
                ),
            )

        for folder_id, old in old_folder_paths.items():
            desired = desired_folder_paths.get(folder_id)
            if desired is None or desired == old or not old.exists():
                continue
            for directory, _children, _files in os.walk(old, topdown=False, followlinks=False):
                try:
                    Path(directory).rmdir()
                except OSError:
                    pass

        for path in sorted(
            {parent for old in old_folder_paths.values() for parent in (old, *old.parents)},
            key=lambda value: len(value.parts),
            reverse=True,
        ):
            if path == self.library_dir or self.library_dir not in path.parents:
                continue
            try:
                path.rmdir()
            except OSError:
                pass

        try:
            self._read_v2()
        finally:
            shutil.rmtree(trash_root, ignore_errors=True)

    def _begin_v2_transaction(self) -> dict[str, Any]:
        journal = self.runtime_dir / V2_WRITE_JOURNAL
        if journal.exists():
            raise StoreError("an unfinished version 2 write requires recovery")
        backup = self.runtime_dir / f"library-write-backup-{uuid.uuid4().hex}.tmp"
        failed = self.runtime_dir / f"library-write-failed-{uuid.uuid4().hex}.tmp"
        old_state = (
            dict(self._v2_folder_paths),
            dict(self._v2_entry_paths),
            dict(self._v2_folder_ranks),
            dict(self._v2_entry_ranks),
            set(self._v2_signature_paths),
        )
        try:
            shutil.copytree(self.library_dir, backup, copy_function=shutil.copy2)
        except OSError as exc:
            shutil.rmtree(backup, ignore_errors=True)
            raise StoreError("cannot stage a safe version 2 metadata write") from exc
        try:
            _atomic_json(
                journal,
                {"version": 1, "state": "prepared", "backup": backup.name},
            )
        except OSError as exc:
            shutil.rmtree(backup, ignore_errors=True)
            raise StoreError("cannot record a safe version 2 metadata write") from exc
        return {
            "journal": journal,
            "backup": backup,
            "failed": failed,
            "old_state": old_state,
        }

    def _rollback_v2_transaction(self, transaction: dict[str, Any]) -> None:
        backup: Path = transaction["backup"]
        failed: Path = transaction["failed"]
        journal: Path = transaction["journal"]
        rollback_errors: list[str] = []
        try:
            os.replace(self.library_dir, failed)
        except OSError as exc:
            rollback_errors.append(f"could not preserve the failed tree: {exc}")
        if not rollback_errors:
            try:
                os.replace(backup, self.library_dir)
            except OSError as exc:
                rollback_errors.append(f"could not restore the prior tree: {exc}")
        if rollback_errors:
            details = "; ".join(rollback_errors)
            raise StoreError(
                "version 2 write failed and automatic rollback was incomplete; "
                f"recovery data remains under {self.runtime_dir}: {details}"
            )
        (
            self._v2_folder_paths,
            self._v2_entry_paths,
            self._v2_folder_ranks,
            self._v2_entry_ranks,
            self._v2_signature_paths,
        ) = transaction["old_state"]
        self._invalidate_search_index()
        journal.unlink(missing_ok=True)
        # A failed tree can contain content not present in the prior snapshot.
        # Preserve it under runtime for explicit inspection.

    def _mark_v2_transaction_committed(self, transaction: dict[str, Any]) -> None:
        journal: Path = transaction["journal"]
        backup: Path = transaction["backup"]
        _atomic_json(
            journal,
            {"version": 1, "state": "committed", "backup": backup.name},
        )

    @staticmethod
    def _cleanup_committed_v2_transaction(transaction: dict[str, Any]) -> None:
        journal: Path = transaction["journal"]
        backup: Path = transaction["backup"]
        try:
            journal.unlink(missing_ok=True)
        except OSError:
            # The committed journal is deliberately recoverable at next startup.
            # Reporting a failed authored write here could make a client retry a
            # non-idempotent operation that already committed.
            return
        shutil.rmtree(backup, ignore_errors=True)

    @contextmanager
    def _v2_write_transaction(self) -> Iterator[None]:
        if self._format_version() != 2 or self._v2_transaction_depth:
            yield
            return
        transaction = self._begin_v2_transaction()
        self._v2_transaction_depth = 1
        try:
            try:
                yield
            except BaseException as exc:
                try:
                    self._rollback_v2_transaction(transaction)
                except StoreError as rollback_exc:
                    raise rollback_exc from exc
                raise
            try:
                self._mark_v2_transaction_committed(transaction)
            except BaseException as exc:
                try:
                    self._rollback_v2_transaction(transaction)
                except StoreError as rollback_exc:
                    raise rollback_exc from exc
                raise
            self._cleanup_committed_v2_transaction(transaction)
        finally:
            self._v2_transaction_depth = 0

    def _write_v2(self, library: dict[str, Any]) -> None:
        with self._v2_write_transaction():
            self._apply_v2_write(library)

    def _write(self, library: dict[str, Any]) -> None:
        for entry in library["entries"]:
            entry["review_modes"] = self.review_modes_for_entry(entry)
        library["updated_at"] = _now()
        try:
            validate_library(
                library,
                self.data_dir,
                self.content_dir,
                self.media_dir,
                self.diagram_dir,
            )
        except LibraryValidationError as exc:
            raise StoreError(str(exc)) from exc
        if self._format_version() == 2:
            self._write_v2(library)
        else:
            _atomic_json(self.library_path, library)
        # A generic write may race an out-of-band direct edit after its final
        # validation. Let the next read use the normal before/after validation
        # loop instead of publishing signatures captured after that race.
        self._invalidate_library_cache()
        self._invalidate_search_index()

    @staticmethod
    def _folder(library: dict[str, Any], folder_id: str) -> dict[str, Any]:
        try:
            return next(folder for folder in library["folders"] if folder["id"] == folder_id)
        except StopIteration as exc:
            raise StoreError("folder not found") from exc

    @staticmethod
    def _entry(library: dict[str, Any], entry_id: str) -> dict[str, Any]:
        try:
            return next(entry for entry in library["entries"] if entry["id"] == entry_id)
        except StopIteration as exc:
            raise StoreError("entry not found") from exc

    def _safe_content_path(self, relative: str) -> Path:
        if not isinstance(relative, str) or "\\" in relative:
            raise StoreError("invalid content path")
        candidate = (self.data_dir / relative).resolve()
        root = self.content_dir.resolve()
        if root not in candidate.parents or candidate.suffix.casefold() != ".md":
            location = "data/content" if self._format_version() == 1 else "the active library root"
            raise StoreError(f"content files must be Markdown files inside {location}")
        return candidate

    def _read_content(self, relative: str) -> str:
        path = self._safe_content_path(relative)
        if not path.is_file() or path.is_symlink():
            raise StoreError(f"Markdown content is missing or unsafe: {relative}")
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise StoreError(f"Markdown content is unreadable: {relative}") from exc

    def _write_content(self, relative: str, content: str) -> None:
        _atomic_text(self._safe_content_path(relative), content.rstrip() + "\n")
        self._invalidate_search_index()

    def _new_variant_relative(
        self,
        library: dict[str, Any],
        *,
        entry_id: str,
        folder_id: str,
        kind: str,
        tag: str,
        variant_id: str,
        supplement_kind: str | None = None,
    ) -> str:
        if self._format_version() == 1:
            return f"content/{entry_id}/{variant_id}.md"
        folder_paths = self._desired_v2_folder_paths(library)
        entry_path = folder_paths[folder_id] / V2_ITEMS_DIRECTORY / kind / tag
        role = (
            "proof"
            if supplement_kind == "pf"
            else "solution"
            if supplement_kind == "sl"
            else "formulation"
        )
        return self._v2_data_relative(entry_path / f"{role}.{variant_id}.md")

    @staticmethod
    def _next_order(items: Iterable[dict[str, Any]]) -> int:
        values = [int(item.get("order", 0)) for item in items]
        return max(values, default=-1) + 1

    def _assert_folder_slug_unique(
        self,
        library: dict[str, Any],
        slug: str,
        parent_id: str | None,
        excluding: str | None = None,
    ) -> None:
        if any(
            folder["id"] != excluding
            and folder.get("parent_id") == parent_id
            and folder["slug"] == slug
            for folder in library["folders"]
        ):
            raise StoreError("that namespace segment is already used in this folder")

    @staticmethod
    def _assert_entry_tag_unique(
        library: dict[str, Any],
        folder_id: str,
        kind: str,
        tag: str,
        excluding: str | None = None,
    ) -> None:
        if any(
            entry["id"] != excluding
            and entry["folder_id"] == folder_id
            and entry["kind"] == kind
            and entry["tag"] == tag
            for entry in library["entries"]
        ):
            raise StoreError("that tag is already used for this content type in this folder")

    @staticmethod
    def _folder_namespaces(library: dict[str, Any]) -> dict[str, str]:
        """Compute every namespace once, even when folders arrive child-first."""
        folders = {folder["id"]: folder for folder in library["folders"]}
        namespaces: dict[str, str] = {}
        for folder_id in folders:
            trail: list[str] = []
            seen: set[str] = set()
            current: str | None = folder_id
            while current is not None and current not in namespaces:
                if current in seen:
                    raise StoreError("folder cycle detected")
                seen.add(current)
                folder = folders.get(current)
                if folder is None:
                    raise StoreError("folder not found")
                trail.append(current)
                current = folder.get("parent_id")
            namespace = namespaces.get(current, "") if current is not None else ""
            for current_id in reversed(trail):
                slug = folders[current_id]["slug"]
                namespace = f"{namespace}:{slug}" if namespace else slug
                namespaces[current_id] = namespace
        return namespaces

    def folder_namespace(self, library: dict[str, Any], folder_id: str) -> str:
        try:
            return self._folder_namespaces(library)[folder_id]
        except KeyError as exc:
            raise StoreError("folder not found") from exc

    def _entry_tag(
        self,
        library: dict[str, Any],
        entry: dict[str, Any],
        namespaces: dict[str, str] | None = None,
    ) -> str:
        namespace = (
            namespaces[entry["folder_id"]]
            if namespaces is not None
            else self.folder_namespace(library, entry["folder_id"])
        )
        return (
            f"{namespace}:{entry['kind']}:{entry['tag']}"
        )

    def _decorate_entry(
        self,
        library: dict[str, Any],
        entry: dict[str, Any],
        full: bool,
        namespaces: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        result = copy.deepcopy(entry)
        result["review_modes"] = self.review_modes_for_entry(result)
        result["canonical_tag"] = self._entry_tag(library, entry, namespaces)
        if full:
            for formulation in result.get("formulations", []):
                formulation["content"] = self._read_content(formulation["file"])
                formulation["canonical_tag"] = result["canonical_tag"] + (
                    f":{formulation['subtag']}" if formulation.get("subtag") else ""
                )
            for supplement in result.get("supplements", []):
                supplement["content"] = self._read_content(supplement["file"])
                supplement["canonical_tag"] = f"{result['canonical_tag']}:{supplement['kind']}" + (
                    f":{supplement['subtag']}" if supplement.get("subtag") else ""
                )
        return result

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            library = self._read()
            namespaces = self._folder_namespaces(library)
            folders = copy.deepcopy(library["folders"])
            entries = [
                self._decorate_entry(library, entry, False, namespaces)
                for entry in library["entries"]
            ]
            for folder in folders:
                folder["namespace"] = namespaces[folder["id"]]
            return {
                "version": library["version"],
                "folders": folders,
                "entries": entries,
                "tree": self._tree(library, namespaces),
                "macros": self.get_macros(),
            }

    def _tree(
        self, library: dict[str, Any], namespaces: dict[str, str] | None = None
    ) -> list[dict[str, Any]]:
        namespaces = namespaces or self._folder_namespaces(library)
        folders_by_parent: dict[str | None, list[dict[str, Any]]] = {}
        entries_by_folder: dict[str, list[dict[str, Any]]] = {}
        for folder in library["folders"]:
            folders_by_parent.setdefault(folder.get("parent_id"), []).append(folder)
        for entry in library["entries"]:
            entries_by_folder.setdefault(entry["folder_id"], []).append(entry)
        for children in folders_by_parent.values():
            children.sort(key=lambda folder: (folder.get("order", 0), folder["name"].lower()))
        for entries in entries_by_folder.values():
            entries.sort(key=lambda entry: (entry.get("order", 0), entry["title"].lower()))

        def nodes(parent_id: str | None) -> list[dict[str, Any]]:
            result = []
            for folder in folders_by_parent.get(parent_id, []):
                result.append(
                    {
                        **copy.deepcopy(folder),
                        "namespace": namespaces[folder["id"]],
                        "entries": [
                            self._decorate_entry(library, entry, False, namespaces)
                            for entry in entries_by_folder.get(folder["id"], [])
                        ],
                        "children": nodes(folder["id"]),
                    }
                )
            return result

        return nodes(None)

    def get_entry(self, entry_id: str) -> dict[str, Any]:
        with self._lock:
            library = self._read()
            return self._decorate_entry(library, self._entry(library, entry_id), True)

    def create_folder(
        self, name: str, slug: str, parent_id: str | None, index: int | None = None
    ) -> dict[str, Any]:
        with self._lock:
            library = self._read()
            name = name.strip()
            if not name:
                raise StoreError("folder name cannot be blank")
            slug = _slug(slug, "namespace")
            if parent_id is not None:
                self._folder(library, parent_id)
            self._assert_folder_slug_unique(library, slug, parent_id)
            peers = sorted(
                (
                    folder
                    for folder in library["folders"]
                    if folder.get("parent_id") == parent_id
                ),
                key=lambda folder: folder.get("order", 0),
            )
            insertion_index = len(peers) if index is None else max(0, min(index, len(peers)))
            for order, peer in enumerate(peers):
                peer["order"] = order if order < insertion_index else order + 1
            folder = {
                "id": uuid.uuid4().hex,
                "name": name,
                "slug": slug,
                "parent_id": parent_id,
                "order": insertion_index,
                "review_enabled": True,
                "created_at": _now(),
            }
            library["folders"].append(folder)
            self._write(library)
            return {**folder, "namespace": self.folder_namespace(library, folder["id"])}

    def update_folder(self, folder_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            library = self._read()
            folder = self._folder(library, folder_id)
            if set(updates) == {"review_enabled"} and updates["review_enabled"] is not None:
                folder["review_enabled"] = bool(updates["review_enabled"])
                folder["updated_at"] = _now()
                if library["version"] == 2:
                    if not self._write_v2_folder_review_preference(library, folder):
                        library = self._read()
                        folder = self._folder(library, folder_id)
                else:
                    self._write(library)
                return {
                    **copy.deepcopy(folder),
                    "namespace": self.folder_namespace(library, folder_id),
                }
            new_parent = updates.get("parent_id", folder.get("parent_id"))
            if new_parent == folder_id:
                raise StoreError("a folder cannot contain itself")
            if new_parent is not None:
                self._folder(library, new_parent)
                cursor: str | None = new_parent
                while cursor is not None:
                    if cursor == folder_id:
                        raise StoreError("a folder cannot move inside one of its descendants")
                    cursor = self._folder(library, cursor).get("parent_id")
            new_slug = _slug(updates.get("slug", folder["slug"]), "namespace")
            self._assert_folder_slug_unique(library, new_slug, new_parent, folder_id)
            if "name" in updates and updates["name"] is not None:
                name = updates["name"].strip()
                if not name:
                    raise StoreError("folder name cannot be blank")
                folder["name"] = name
            folder["slug"] = new_slug
            if "parent_id" in updates:
                old_parent = folder.get("parent_id")
                folder["parent_id"] = new_parent
                if old_parent != new_parent:
                    folder["order"] = self._next_order(
                        f
                        for f in library["folders"]
                        if f.get("parent_id") == new_parent and f["id"] != folder_id
                    )
            if updates.get("review_enabled") is not None:
                folder["review_enabled"] = bool(updates["review_enabled"])
            folder["updated_at"] = _now()
            self._write(library)
            return {**copy.deepcopy(folder), "namespace": self.folder_namespace(library, folder_id)}

    def _write_v2_folder_review_preference(
        self, library: dict[str, Any], folder: dict[str, Any]
    ) -> bool:
        """Atomically persist the one sidecar field that has no structural dependencies."""
        folder_id = folder["id"]
        folder_path = self._v2_folder_paths.get(folder_id)
        rank = self._v2_folder_ranks.get(folder_id)
        if folder_path is None or rank is None:
            raise StoreError("folder metadata path is unavailable")
        metadata_path = folder_path / V2_FOLDER_METADATA
        expected_changes = {metadata_path.resolve(), folder_path.resolve()}
        prior_library_signatures = dict(self._library_signatures)
        preserve_search = self._search_snapshot_matches_disk()
        expected_metadata = self._v2_folder_metadata(folder, rank, folder_path)
        prior_target_signature = prior_library_signatures.get(metadata_path.resolve())

        try:
            self._write_json_if_signature_matches(
                metadata_path,
                expected_metadata,
                prior_target_signature,
            )
        except StoreError:
            self._invalidate_library_cache()
            self._invalidate_search_index()
            raise

        cache_refreshed = False
        try:
            target_before = self._file_signature(metadata_path)
            target_metadata = self._read_json_object(
                metadata_path, f"folder metadata at {folder_path.name}"
            )
            target_after = self._file_signature(metadata_path)
            if target_metadata != expected_metadata or target_before != target_after:
                raise StoreError("folder metadata changed while saving its review preference")
            tree_signatures = self._v2_tree_signatures()
            next_signatures = {
                self.library_path: self._file_signature(self.library_path),
                **tree_signatures,
            }
            next_signatures.update(
                {
                    path: self._file_signature(path)
                    for path in self._v2_signature_paths
                    if path not in next_signatures
                }
            )
            unchanged_paths = set(prior_library_signatures) - expected_changes
            no_unexpected_change = (
                set(next_signatures) == set(prior_library_signatures)
                and next_signatures.get(metadata_path.resolve()) == target_after
                and all(
                    next_signatures[path] == prior_library_signatures[path]
                    for path in unchanged_paths
                )
            )
            if no_unexpected_change:
                self._cache_validated_library(
                    library,
                    signatures=next_signatures,
                )
                cache_refreshed = True
            else:
                self._invalidate_library_cache()
        except StoreError:
            # The single atomic sidecar write already committed. Force the next
            # read to validate from disk instead of reporting a false failure.
            self._invalidate_library_cache()

        if preserve_search and cache_refreshed:
            self._refresh_search_signatures(expected_changes)
        else:
            self._invalidate_search_index()
        return cache_refreshed

    @staticmethod
    def _next_sibling_id(items: list[dict[str, Any]], item_id: str) -> str | None:
        ordered = sorted(items, key=lambda item: item.get("order", 0))
        position = next(index for index, item in enumerate(ordered) if item["id"] == item_id)
        if position + 1 < len(ordered):
            return ordered[position + 1]["id"]
        if position > 0:
            return ordered[position - 1]["id"]
        return None

    def _safe_owned_file(self, relative: str, root: Path, suffixes: set[str]) -> Path:
        if not isinstance(relative, str) or not relative or "\\" in relative:
            raise StoreError("invalid owned file path")
        unresolved = self.data_dir / relative
        try:
            candidate = unresolved.resolve(strict=True)
            resolved_root = root.resolve()
        except OSError as exc:
            raise StoreError(f"owned file is missing or unsafe: {relative}") from exc
        if (
            resolved_root not in candidate.parents
            or candidate.suffix.casefold() not in suffixes
            or unresolved.is_symlink()
            or not candidate.is_file()
        ):
            raise StoreError(f"owned file is missing or unsafe: {relative}")
        return candidate

    def _safe_entry_asset_file(
        self,
        entry: dict[str, Any],
        relative: str,
        field: str,
        global_root: Path,
        suffixes: set[str],
    ) -> Path:
        pattern = MEDIA_PATH_RE if field == "path" else None
        if field == "source":
            pattern = (
                EXCALIDRAW_PATH_RE
                if Path(relative).suffix.casefold() == ".excalidraw"
                else COMMUTATIVE_PATH_RE
            )
        if pattern is None or pattern.fullmatch(relative) is None:
            raise StoreError(f"invalid owned asset path: {relative}")
        if self._format_version() == 1:
            return self._safe_owned_file(relative, global_root, suffixes)
        entry_root = self._v2_entry_paths.get(entry["id"])
        if entry_root is None:
            raise StoreError(f"entry asset owner is missing: {entry['id']}")
        local_root = entry_root / V2_ASSETS_DIRECTORY
        local = local_root / Path(relative).name
        if local.exists() or local.is_symlink():
            local_relative = self._v2_data_relative(local)
            return self._safe_owned_file(local_relative, local_root, suffixes)
        # A logical route in a v2 sidecar is an explicit pre-colocation record.
        # Resolver callers have already matched it against a registered asset.
        return self._safe_owned_file(relative, global_root, suffixes)

    def _entry_owned_files(
        self, entries: list[dict[str, Any]]
    ) -> tuple[dict[Path, str], dict[Path, tuple[str, set[str]]]]:
        content_files: dict[Path, str] = {}
        asset_files: dict[Path, tuple[str, set[str]]] = {}
        for entry in entries:
            for variant in (*entry.get("formulations", []), *entry.get("supplements", [])):
                relative = variant["file"]
                path = self._safe_owned_file(relative, self.content_dir, {".md"})
                content_files[path] = relative
            for asset in entry.get("assets", []):
                for field, root, suffixes in (
                    ("path", self.media_dir, {".png", ".jpg", ".jpeg", ".webp"}),
                    ("source", self.diagram_dir, {".excalidraw", ".json"}),
                ):
                    relative = asset.get(field)
                    if relative is None:
                        continue
                    path = self._safe_entry_asset_file(
                        entry, relative, field, root, suffixes
                    )
                    existing = asset_files.get(path)
                    tokens = {
                        relative,
                        Path(relative).name,
                        asset["id"],
                    }
                    if existing is None:
                        asset_files[path] = (relative, tokens)
                    else:
                        existing[1].update(tokens)
        return content_files, asset_files

    def _surviving_asset_references(
        self, entries: list[dict[str, Any]]
    ) -> tuple[set[Path], set[str], list[str]]:
        paths: set[Path] = set()
        tokens: set[str] = set()
        markdown: list[str] = []
        for entry in entries:
            for variant in (*entry.get("formulations", []), *entry.get("supplements", [])):
                markdown.append(self._read_content(variant["file"]))
            for asset in entry.get("assets", []):
                for field, root, suffixes in (
                    ("path", self.media_dir, {".png", ".jpg", ".jpeg", ".webp"}),
                    ("source", self.diagram_dir, {".excalidraw", ".json"}),
                ):
                    relative = asset.get(field)
                    if relative is not None:
                        paths.add(
                            self._safe_entry_asset_file(
                                entry, relative, field, root, suffixes
                            )
                        )
                        tokens.update({relative, Path(relative).name, asset["id"]})
        return paths, tokens, markdown

    def _plan_unreferenced_files(
        self,
        content_files: dict[Path, str],
        asset_files: dict[Path, tuple[str, set[str]]],
        surviving_entries: list[dict[str, Any]],
    ) -> tuple[dict[Path, str], dict[Path, str]]:
        surviving_asset_paths, surviving_asset_tokens, surviving_markdown = (
            self._surviving_asset_references(
                surviving_entries
            )
        )
        local_reference_blockers: list[str] = []
        if self._format_version() == 2:
            for relative, tokens in asset_files.values():
                matching_assets = tokens & surviving_asset_tokens
                referenced = any(
                    token in text for token in tokens for text in surviving_markdown
                )
                if referenced and not matching_assets:
                    local_reference_blockers.append(relative)
        if local_reference_blockers:
            raise StoreError(
                "cannot delete content while surviving Markdown references its local asset: "
                f"{min(local_reference_blockers)}"
            )
        preserved = {
            path: relative
            for path, (relative, tokens) in asset_files.items()
            if path in surviving_asset_paths
            or (
                self._format_version() == 1
                and any(token in text for token in tokens for text in surviving_markdown)
            )
        }
        deletions = {
            **content_files,
            **{
                path: relative
                for path, (relative, _tokens) in asset_files.items()
                if path not in preserved
            },
        }
        return deletions, preserved

    def _delete_planned_files(
        self,
        deletions: dict[Path, str],
        preserved: dict[Path, str],
    ) -> dict[str, Any]:
        deleted: list[str] = []
        pending: list[str] = []
        content_parents: set[Path] = set()
        for path, relative in sorted(deletions.items(), key=lambda item: item[1]):
            try:
                if path.exists() and (path.is_symlink() or path.resolve(strict=True) != path):
                    pending.append(relative)
                    continue
                path.unlink(missing_ok=True)
                deleted.append(relative)
                if self.content_dir.resolve() in path.parents:
                    content_parents.add(path.parent)
            except OSError:
                pending.append(relative)

        content_root = self.content_dir.resolve()
        for directory in sorted(content_parents, key=lambda path: len(path.parts), reverse=True):
            current = directory
            while current != content_root and content_root in current.parents:
                try:
                    current.rmdir()
                except OSError:
                    break
                current = current.parent

        return {
            "deleted_file_count": len(deleted),
            "deleted_paths": deleted,
            "preserved_shared_file_count": len(preserved),
            "preserved_shared_paths": sorted(preserved.values()),
            "cleanup_pending_count": len(pending),
            "cleanup_pending_paths": pending,
        }

    def delete_entry(self, entry_id: str) -> dict[str, Any]:
        """Delete one entry and its exclusively owned files."""
        with self._lock:
            library = self._read()
            entry = self._entry(library, entry_id)
            peers = [
                candidate
                for candidate in library["entries"]
                if candidate["folder_id"] == entry["folder_id"]
            ]
            next_entry_id = self._next_sibling_id(peers, entry_id)
            content_files, asset_files = self._entry_owned_files([entry])
            surviving_entries = [
                candidate for candidate in library["entries"] if candidate["id"] != entry_id
            ]
            deletions, preserved = self._plan_unreferenced_files(
                content_files, asset_files, surviving_entries
            )
            library["entries"] = surviving_entries
            self._renumber_entries(library, entry["folder_id"])

            # Commit metadata first. A later unlink failure can leave an inert orphan,
            # but it can never leave the library pointing at a deleted file.
            self._write(library)
            files = self._delete_planned_files(deletions, preserved)
            return {
                "item_type": "entry",
                "item_id": entry_id,
                "title": entry["title"],
                "folder_count": 0,
                "entry_count": 1,
                "next_entry_id": next_entry_id,
                **files,
            }

    def delete_folder(self, folder_id: str, recursive: bool = False) -> dict[str, Any]:
        """Delete an empty folder, or an explicitly confirmed complete subtree."""
        with self._lock:
            library = self._read()
            folder = self._folder(library, folder_id)
            direct_children = [
                candidate
                for candidate in library["folders"]
                if candidate.get("parent_id") == folder_id
            ]
            direct_entries = [
                entry for entry in library["entries"] if entry["folder_id"] == folder_id
            ]
            if not recursive and (direct_children or direct_entries):
                raise StoreError(
                    "folder is not empty; confirm recursive deletion to remove its "
                    "subfolders and entries"
                )

            folder_ids = self.descendants(library, folder_id) if recursive else {folder_id}
            deleted_entries = [
                entry for entry in library["entries"] if entry["folder_id"] in folder_ids
            ]
            content_files, asset_files = self._entry_owned_files(deleted_entries)
            surviving_entries = [
                entry for entry in library["entries"] if entry["folder_id"] not in folder_ids
            ]
            deletions, preserved = self._plan_unreferenced_files(
                content_files, asset_files, surviving_entries
            )
            siblings = [
                candidate
                for candidate in library["folders"]
                if candidate.get("parent_id") == folder.get("parent_id")
            ]
            next_folder_id = self._next_sibling_id(siblings, folder_id) or folder.get("parent_id")

            library["entries"] = surviving_entries
            library["folders"] = [
                candidate for candidate in library["folders"] if candidate["id"] not in folder_ids
            ]
            self._renumber_folders(library, folder.get("parent_id"))
            self._write(library)
            files = self._delete_planned_files(deletions, preserved)
            return {
                "item_type": "folder",
                "item_id": folder_id,
                "title": folder["name"],
                "folder_count": len(folder_ids),
                "entry_count": len(deleted_entries),
                "next_folder_id": next_folder_id,
                **files,
            }

    def create_entry(
        self,
        folder_id: str,
        kind: str,
        title: str,
        tag: str,
        header: str,
        content: str,
        review_modes: list[str] | None = None,
        index: int | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            library = self._read()
            self._folder(library, folder_id)
            if kind not in KINDS:
                raise StoreError("invalid content type")
            tag = _slug(tag, "tag")
            title = title.strip()
            if not title:
                raise StoreError("entry title cannot be blank")
            self._assert_entry_tag_unique(library, folder_id, kind, tag)
            modes = self.default_review_modes(kind)
            if review_modes is not None and list(dict.fromkeys(review_modes)) != modes:
                raise StoreError("review modes are fixed for this content type")
            entry_id = uuid.uuid4().hex
            formulation_id = uuid.uuid4().hex
            relative = self._new_variant_relative(
                library,
                entry_id=entry_id,
                folder_id=folder_id,
                kind=kind,
                tag=tag,
                variant_id=formulation_id,
            )
            peers = sorted(
                (entry for entry in library["entries"] if entry["folder_id"] == folder_id),
                key=lambda entry: entry.get("order", 0),
            )
            insertion_index = len(peers) if index is None else max(0, min(index, len(peers)))
            for order, peer in enumerate(peers):
                peer["order"] = order if order < insertion_index else order + 1
            entry = {
                "id": entry_id,
                "folder_id": folder_id,
                "kind": kind,
                "title": title,
                "tag": tag,
                "header": header.strip(),
                "order": insertion_index,
                "review_modes": modes,
                "problem_family": "",
                "confusable_with": [],
                "formulations": [
                    {
                        "id": formulation_id,
                        "label": "Main",
                        "subtag": None,
                        "file": relative,
                        "main": True,
                    }
                ],
                "supplements": [],
                "assets": [],
                "created_at": _now(),
                "updated_at": _now(),
            }
            with self._v2_write_transaction():
                self._write_content(relative, content)
                library["entries"].append(entry)
                self._write(library)
            return self._decorate_entry(library, entry, True)

    @staticmethod
    def default_review_modes(kind: str) -> list[str]:
        return {
            "ax": ["statement"],
            "df": ["statement"],
            "rk": ["statement"],
            "th": ["statement"],
            "pb": [],
        }[kind]

    @classmethod
    def review_modes_for_entry(cls, entry: dict[str, Any]) -> list[str]:
        modes = cls.default_review_modes(entry["kind"])
        guarded_mode = SUPPLEMENT_REVIEW_MODE.get(entry["kind"])
        expected = SUPPLEMENT_BY_ENTRY.get(entry["kind"])
        if guarded_mode and any(
            supplement.get("kind") == expected and supplement.get("main")
            for supplement in entry.get("supplements", [])
        ):
            modes.append(guarded_mode)
        return modes

    @staticmethod
    def _assert_formulation_subtag_available(kind: str, subtag: str | None) -> None:
        reserved = SUPPLEMENT_BY_ENTRY.get(kind)
        if subtag and subtag == reserved:
            raise StoreError(f"the formulation subtag {subtag!r} is reserved for this content type")

    @staticmethod
    def review_mode_available(entry: dict[str, Any], mode: str) -> bool:
        kind = entry["kind"]
        if mode not in REVIEW_MODES_BY_KIND[kind]:
            return False
        guarded_mode = SUPPLEMENT_REVIEW_MODE.get(kind)
        if mode != guarded_mode:
            return True
        expected = SUPPLEMENT_BY_ENTRY[kind]
        return any(
            supplement.get("kind") == expected and supplement.get("main")
            for supplement in entry.get("supplements", [])
        )

    def update_entry(self, entry_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            library = self._read()
            entry = self._entry(library, entry_id)
            folder_id = updates.get("folder_id") or entry["folder_id"]
            kind = updates.get("kind") or entry["kind"]
            tag = _slug(updates.get("tag") or entry["tag"], "tag")
            self._folder(library, folder_id)
            if kind not in KINDS:
                raise StoreError("invalid content type")
            if kind not in ALT_KINDS and len(entry.get("formulations", [])) > 1:
                raise StoreError(
                    "remove alternative formulations before changing to this content type"
                )
            expected_supplement = SUPPLEMENT_BY_ENTRY.get(kind)
            if any(
                item.get("kind") != expected_supplement for item in entry.get("supplements", [])
            ):
                raise StoreError(
                    "remove incompatible proofs or solutions before changing content type"
                )
            for formulation in entry.get("formulations", []):
                self._assert_formulation_subtag_available(kind, formulation.get("subtag"))
            self._assert_entry_tag_unique(library, folder_id, kind, tag, entry_id)
            if folder_id != entry["folder_id"]:
                entry["folder_id"] = folder_id
                entry["order"] = self._next_order(
                    e
                    for e in library["entries"]
                    if e["folder_id"] == folder_id and e["id"] != entry_id
                )
            entry["kind"] = kind
            entry["tag"] = tag
            for field in ("title", "header", "problem_family"):
                if field in updates and updates[field] is not None:
                    value = updates[field].strip()
                    if field == "title" and not value:
                        raise StoreError("entry title cannot be blank")
                    entry[field] = value
            fixed_modes = self.review_modes_for_entry(entry)
            if updates.get("review_modes") is not None and list(
                dict.fromkeys(updates["review_modes"])
            ) != fixed_modes:
                raise StoreError("review modes are fixed for this content type")
            entry["review_modes"] = fixed_modes
            if updates.get("confusable_with") is not None:
                entry["confusable_with"] = list(dict.fromkeys(updates["confusable_with"]))
            entry["updated_at"] = _now()
            self._write(library)
            return self._decorate_entry(library, entry, True)

    def _variant(self, entry: dict[str, Any], variant_id: str) -> dict[str, Any]:
        for group in (entry.get("formulations", []), entry.get("supplements", [])):
            for variant in group:
                if variant["id"] == variant_id:
                    return variant
        raise StoreError("formulation or supplement not found")

    @staticmethod
    def _demotion_subtag(group: list[dict[str, Any]], excluding: str) -> str:
        used = {item.get("subtag") for item in group if item["id"] != excluding}
        candidate = "standard"
        sequence = 2
        while candidate in used:
            candidate = f"standard-{sequence}"
            sequence += 1
        return candidate

    def write_variant_content(self, entry_id: str, variant_id: str, content: str) -> dict[str, Any]:
        with self._lock:
            library = self._read()
            entry = self._entry(library, entry_id)
            variant = self._variant(entry, variant_id)
            with self._v2_write_transaction():
                self._write_content(variant["file"], content)
                entry["updated_at"] = _now()
                self._write(library)
            return self._decorate_entry(library, entry, True)

    def add_formulation(self, entry_id: str, value: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            library = self._read()
            entry = self._entry(library, entry_id)
            if entry["kind"] not in ALT_KINDS:
                raise StoreError("this content type cannot have alternative formulations")
            label = value["label"].strip()
            if not label:
                raise StoreError("formulation label cannot be blank")
            subtag = _slug(value["subtag"], "subtag") if value.get("subtag") else None
            self._assert_formulation_subtag_available(entry["kind"], subtag)
            if value.get("main") and subtag:
                raise StoreError("a main formulation cannot have a subtag")
            if not value.get("main") and not subtag:
                raise StoreError("an alternative formulation needs a subtag")
            if any(item.get("subtag") == subtag and subtag for item in entry["formulations"]):
                raise StoreError("that formulation subtag is already used")
            variant_id = uuid.uuid4().hex
            relative = self._new_variant_relative(
                library,
                entry_id=entry_id,
                folder_id=entry["folder_id"],
                kind=entry["kind"],
                tag=entry["tag"],
                variant_id=variant_id,
            )
            variant = {
                "id": variant_id,
                "label": label,
                "subtag": None if value.get("main") else subtag,
                "file": relative,
                "main": bool(value.get("main")),
            }
            if variant["main"]:
                for existing in entry["formulations"]:
                    existing["main"] = False
                    if not existing.get("subtag"):
                        existing["subtag"] = self._demotion_subtag(
                            entry["formulations"], existing["id"]
                        )
            with self._v2_write_transaction():
                entry["formulations"].append(variant)
                self._write_content(relative, value.get("content", ""))
                entry["updated_at"] = _now()
                self._write(library)
            return self._decorate_entry(library, entry, True)

    def add_supplement(self, entry_id: str, value: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            library = self._read()
            entry = self._entry(library, entry_id)
            expected = SUPPLEMENT_BY_ENTRY.get(entry["kind"])
            if value["kind"] != expected:
                raise StoreError("only theorems have proofs and only problems have solutions")
            label = value["label"].strip()
            if not label:
                raise StoreError("proof or solution label cannot be blank")
            subtag = _slug(value["subtag"], "subtag") if value.get("subtag") else None
            same_kind = [item for item in entry["supplements"] if item["kind"] == expected]
            main = bool(value.get("main")) or not same_kind
            if main and subtag:
                raise StoreError("a main proof or solution cannot have a subtag")
            if not main and not subtag:
                raise StoreError("an alternative proof or solution needs a subtag")
            if any(item.get("subtag") == subtag and subtag for item in same_kind):
                raise StoreError("that supplement subtag is already used")
            variant_id = uuid.uuid4().hex
            relative = self._new_variant_relative(
                library,
                entry_id=entry_id,
                folder_id=entry["folder_id"],
                kind=entry["kind"],
                tag=entry["tag"],
                variant_id=variant_id,
                supplement_kind=expected,
            )
            supplement = {
                "id": variant_id,
                "kind": expected,
                "label": label,
                "subtag": None if main else subtag,
                "file": relative,
                "main": main,
            }
            if main:
                for existing in same_kind:
                    existing["main"] = False
                    if not existing.get("subtag"):
                        existing["subtag"] = self._demotion_subtag(same_kind, existing["id"])
            with self._v2_write_transaction():
                entry["supplements"].append(supplement)
                entry["review_modes"] = self.review_modes_for_entry(entry)
                self._write_content(relative, value.get("content", ""))
                entry["updated_at"] = _now()
                self._write(library)
            return self._decorate_entry(library, entry, True)

    def update_variant(
        self, entry_id: str, variant_id: str, updates: dict[str, Any]
    ) -> dict[str, Any]:
        with self._lock:
            library = self._read()
            entry = self._entry(library, entry_id)
            variant = self._variant(entry, variant_id)
            group_name = "formulations" if variant in entry["formulations"] else "supplements"
            group = entry[group_name]
            if updates.get("label") is not None:
                label = updates["label"].strip()
                if not label:
                    raise StoreError("variant label cannot be blank")
                variant["label"] = label
            if updates.get("subtag") and (variant.get("main") or updates.get("main") is True):
                raise StoreError("a main variant cannot have a subtag")
            if "subtag" in updates:
                subtag = _slug(updates["subtag"], "subtag") if updates["subtag"] else None
                if group_name == "formulations":
                    self._assert_formulation_subtag_available(entry["kind"], subtag)
                if any(
                    item["id"] != variant_id and item.get("subtag") == subtag and subtag
                    for item in group
                ):
                    raise StoreError("that subtag is already used")
                variant["subtag"] = subtag
            if updates.get("main") is False and variant.get("main"):
                raise StoreError(
                    "select another main variant instead of leaving the group without one"
                )
            if updates.get("main") is True:
                for item in group:
                    if item["id"] != variant_id:
                        item["main"] = False
                        if not item.get("subtag"):
                            item["subtag"] = self._demotion_subtag(group, item["id"])
                variant["main"] = True
                variant["subtag"] = None
            if not variant.get("main") and not variant.get("subtag"):
                raise StoreError("an alternative variant needs a subtag")
            with self._v2_write_transaction():
                if updates.get("content") is not None:
                    self._write_content(variant["file"], updates["content"])
                entry["updated_at"] = _now()
                self._write(library)
            return self._decorate_entry(library, entry, True)

    def move_item(
        self, item_type: str, item_id: str, destination_folder_id: str | None, index: int
    ) -> None:
        with self._lock:
            library = self._read()
            if item_type == "entry":
                if destination_folder_id is None:
                    raise StoreError("entries must be inside a folder")
                self._folder(library, destination_folder_id)
                item = self._entry(library, item_id)
                source_folder_id = item["folder_id"]
                self._assert_entry_tag_unique(
                    library,
                    destination_folder_id,
                    item["kind"],
                    item["tag"],
                    item_id,
                )
                source_peers = sorted(
                    (
                        entry
                        for entry in library["entries"]
                        if entry["folder_id"] == source_folder_id
                    ),
                    key=lambda entry: entry.get("order", 0),
                )
                source_index = next(
                    position
                    for position, peer in enumerate(source_peers)
                    if peer["id"] == item_id
                )
                insertion_index = max(0, index)
                if source_folder_id == destination_folder_id and source_index < insertion_index:
                    insertion_index -= 1
                item["folder_id"] = destination_folder_id
                if source_folder_id != destination_folder_id:
                    for order, peer in enumerate(
                        entry for entry in source_peers if entry["id"] != item_id
                    ):
                        peer["order"] = order
                peers = sorted(
                    (
                        entry
                        for entry in library["entries"]
                        if entry["folder_id"] == destination_folder_id and entry["id"] != item_id
                    ),
                    key=lambda entry: entry.get("order", 0),
                )
                peers.insert(min(insertion_index, len(peers)), item)
                for order, peer in enumerate(peers):
                    peer["order"] = order
                item["updated_at"] = _now()
            elif item_type == "folder":
                item = self._folder(library, item_id)
                if destination_folder_id == item_id:
                    raise StoreError("a folder cannot contain itself")
                if destination_folder_id is not None:
                    self._folder(library, destination_folder_id)
                    cursor: str | None = destination_folder_id
                    while cursor is not None:
                        if cursor == item_id:
                            raise StoreError(
                                "a folder cannot move inside one of its descendants"
                            )
                        cursor = self._folder(library, cursor).get("parent_id")
                self._assert_folder_slug_unique(
                    library, item["slug"], destination_folder_id, item_id
                )
                source_parent_id = item.get("parent_id")
                source_peers = sorted(
                    (
                        folder
                        for folder in library["folders"]
                        if folder.get("parent_id") == source_parent_id
                    ),
                    key=lambda folder: folder.get("order", 0),
                )
                source_index = next(
                    position
                    for position, peer in enumerate(source_peers)
                    if peer["id"] == item_id
                )
                insertion_index = max(0, index)
                if source_parent_id == destination_folder_id and source_index < insertion_index:
                    insertion_index -= 1
                if source_parent_id != destination_folder_id:
                    for order, peer in enumerate(
                        folder for folder in source_peers if folder["id"] != item_id
                    ):
                        peer["order"] = order
                item["parent_id"] = destination_folder_id
                peers = sorted(
                    (
                        folder
                        for folder in library["folders"]
                        if folder.get("parent_id") == destination_folder_id
                        and folder["id"] != item_id
                    ),
                    key=lambda folder: folder.get("order", 0),
                )
                peers.insert(min(insertion_index, len(peers)), item)
                for order, peer in enumerate(peers):
                    peer["order"] = order
                item["updated_at"] = _now()
            else:
                raise StoreError("item type must be folder or entry")
            self._write(library)

    @staticmethod
    def _renumber_entries(library: dict[str, Any], folder_id: str) -> None:
        peers = sorted(
            (entry for entry in library["entries"] if entry["folder_id"] == folder_id),
            key=lambda entry: entry.get("order", 0),
        )
        for order, peer in enumerate(peers):
            peer["order"] = order

    @staticmethod
    def _renumber_folders(library: dict[str, Any], parent_id: str | None) -> None:
        peers = sorted(
            (
                folder
                for folder in library["folders"]
                if folder.get("parent_id") == parent_id
            ),
            key=lambda folder: folder.get("order", 0),
        )
        for order, peer in enumerate(peers):
            peer["order"] = order

    def reorder_entries(self, folder_id: str, entry_ids: list[str]) -> None:
        with self._lock:
            library = self._read()
            self._folder(library, folder_id)
            actual = {
                entry["id"] for entry in library["entries"] if entry["folder_id"] == folder_id
            }
            if set(entry_ids) != actual or len(entry_ids) != len(actual):
                raise StoreError("reorder must include every direct entry exactly once")
            lookup = {entry["id"]: entry for entry in library["entries"]}
            for order, entry_id in enumerate(entry_ids):
                lookup[entry_id]["order"] = order
            self._write(library)

    def get_macros(self) -> dict[str, str | list[str | int]]:
        with self._lock:
            try:
                with self.macros_path.open(encoding="utf-8") as stream:
                    value = json.load(stream)
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise StoreError("macros.json is unreadable or invalid") from exc
            if not isinstance(value, dict) or value.get("version") != 1:
                raise StoreError("unsupported macros version")
            macros = value.get("macros")
            if not isinstance(macros, dict):
                raise StoreError("macros.json must contain a macros object")
            self._validate_macros(macros)
            return macros

    @staticmethod
    def _validate_macros(macros: dict[str, Any]) -> None:
        for name, definition in macros.items():
            if not re.fullmatch(r"[A-Za-z]+", name):
                raise StoreError(f"invalid macro name: {name}")
            if isinstance(definition, str):
                continue
            if not isinstance(definition, list) or len(definition) not in {2, 3}:
                raise StoreError(
                    f"macro {name} must be a string or [replacement, argument-count, optional-default]"
                )
            if not isinstance(definition[0], str):
                raise StoreError(f"macro {name} replacement must be a string")
            if (
                isinstance(definition[1], bool)
                or not isinstance(definition[1], int)
                or not 0 <= definition[1] <= 9
            ):
                raise StoreError(f"macro {name} argument count must be an integer from 0 through 9")
            if len(definition) == 3 and not isinstance(definition[2], str):
                raise StoreError(f"macro {name} optional default must be a string")

    def set_macros(self, macros: dict[str, str | list[str | int]]) -> dict[str, Any]:
        self._validate_macros(macros)
        value = {"version": 1, "macros": macros, "updated_at": _now()}
        with self._lock:
            _atomic_json(self.macros_path, value)
        return value

    def check_data(self) -> dict[str, int]:
        with self._lock:
            library = self._read()
            self.get_macros()
            for entry in library["entries"]:
                for variant in (
                    *entry.get("formulations", []),
                    *entry.get("supplements", []),
                ):
                    self._read_content(variant["file"])
            markdown_files = sum(
                len(entry.get("formulations", [])) + len(entry.get("supplements", []))
                for entry in library["entries"]
            )
            return {
                "version": int(library["version"]),
                "folders": len(library["folders"]),
                "entries": len(library["entries"]),
                "markdown_files": markdown_files,
            }

    def descendants(self, library: dict[str, Any], folder_id: str) -> set[str]:
        result = {folder_id}
        children: dict[str, list[str]] = {}
        for folder in library["folders"]:
            parent_id = folder.get("parent_id")
            if parent_id is not None:
                children.setdefault(parent_id, []).append(folder["id"])
        pending = [folder_id]
        while pending:
            current = pending.pop()
            for child_id in children.get(current, []):
                if child_id not in result:
                    result.add(child_id)
                    pending.append(child_id)
        return result

    def ordered_entries(
        self,
        folder_id: str | None = None,
        recursive: bool = True,
        kinds: set[str] | None = None,
        review_only: bool = False,
    ) -> list[dict[str, Any]]:
        with self._lock:
            library = self._read()
            allowed: set[str] | None = None
            if folder_id is not None:
                self._folder(library, folder_id)
                allowed = self.descendants(library, folder_id) if recursive else {folder_id}

            folder_by_id = {folder["id"]: folder for folder in library["folders"]}
            namespaces = self._folder_namespaces(library)
            eligible: dict[str, bool] = {}

            def is_review_enabled(fid: str) -> bool:
                if fid in eligible:
                    return eligible[fid]
                folder = folder_by_id[fid]
                value = bool(folder.get("review_enabled", True)) and (
                    folder.get("parent_id") is None or is_review_enabled(folder["parent_id"])
                )
                eligible[fid] = value
                return value

            ordered: list[dict[str, Any]] = []
            children: dict[str | None, list[dict[str, Any]]] = {}
            entries_by_folder: dict[str, list[dict[str, Any]]] = {}
            for folder in library["folders"]:
                children.setdefault(folder.get("parent_id"), []).append(folder)
            for values in children.values():
                values.sort(key=lambda folder: folder.get("order", 0))
            for entry in library["entries"]:
                entries_by_folder.setdefault(entry["folder_id"], []).append(entry)
            for values in entries_by_folder.values():
                values.sort(key=lambda entry: entry.get("order", 0))

            pending = list(reversed(children.get(None, [])))
            while pending:
                folder = pending.pop()
                if (allowed is None or folder["id"] in allowed) and (
                    not review_only or is_review_enabled(folder["id"])
                ):
                    for entry in entries_by_folder.get(folder["id"], []):
                        if kinds is None or entry["kind"] in kinds:
                            ordered.append(
                                self._decorate_entry(library, entry, True, namespaces)
                            )
                pending.extend(reversed(children.get(folder["id"], [])))
            return ordered

    def _asset_file_targets(
        self,
        entry: dict[str, Any],
        asset: dict[str, Any],
        version: int,
    ) -> dict[str, Path]:
        targets: dict[str, Path] = {}
        for field in ("path", "source"):
            relative = asset.get(field)
            if relative is None:
                continue
            pattern = MEDIA_PATH_RE if field == "path" else None
            if field == "source" and asset.get("kind") == "excalidraw":
                pattern = EXCALIDRAW_PATH_RE
            elif field == "source" and asset.get("kind") == "commutative":
                pattern = COMMUTATIVE_PATH_RE
            if (
                not isinstance(relative, str)
                or pattern is None
                or pattern.fullmatch(relative) is None
            ):
                raise StoreError(f"asset {field} is not a safe Study asset path")
            if version == 1:
                targets[field] = self.data_dir / relative
                continue
            entry_root = self._v2_entry_paths.get(entry["id"])
            if entry_root is None:
                raise StoreError("entry asset owner is missing")
            targets[field] = (
                entry_root / V2_ASSETS_DIRECTORY / Path(relative).name
            )
        return targets

    def register_asset(
        self,
        entry_id: str,
        asset: dict[str, Any],
        file_contents: dict[str, bytes] | None = None,
    ) -> dict[str, Any]:
        """Atomically register an asset and, when supplied, write its owned files."""
        with self._lock:
            library = self._read()
            entry = self._entry(library, entry_id)
            stored_asset = copy.deepcopy(asset)
            version = int(library["version"])
            targets = self._asset_file_targets(entry, stored_asset, version)
            contents = dict(file_contents or {})
            if set(contents) - set(targets):
                raise StoreError("asset file contents do not match its metadata")
            if any(not isinstance(value, bytes) for value in contents.values()):
                raise StoreError("asset file contents must be bytes")

            created: list[Path] = []
            try:
                with self._v2_write_transaction():
                    for field, value in contents.items():
                        target = targets[field]
                        if target.is_symlink():
                            raise StoreError(f"asset destination is unsafe: {target.name}")
                        if target.exists():
                            if not target.is_file():
                                raise StoreError(
                                    f"asset destination is unsafe: {target.name}"
                                )
                            try:
                                existing = target.read_bytes()
                            except OSError as exc:
                                raise StoreError(
                                    f"cannot inspect existing asset: {target.name}"
                                ) from exc
                            if existing != value:
                                raise StoreError(
                                    f"asset filename collides with different content: {target.name}"
                                )
                            continue
                        _atomic_bytes(target, value)
                        created.append(target)
                    entry.setdefault("assets", []).append(stored_asset)
                    entry["updated_at"] = _now()
                    self._write(library)
            except BaseException:
                if version == 1:
                    for path in created:
                        path.unlink(missing_ok=True)
                raise
            return copy.deepcopy(stored_asset)

    def _resolve_asset_file(
        self,
        *,
        field: str,
        filename: str,
        kinds: set[str],
        global_root: Path,
        suffixes: set[str],
    ) -> Path | None:
        route_prefix = "media" if field == "path" else "diagrams"
        relative = f"{route_prefix}/{filename}"
        pattern = MEDIA_PATH_RE if field == "path" else None
        if field == "source" and kinds == {"excalidraw"}:
            pattern = EXCALIDRAW_PATH_RE
        elif field == "source" and kinds == {"commutative"}:
            pattern = COMMUTATIVE_PATH_RE
        if pattern is None or pattern.fullmatch(relative) is None:
            return None
        with self._lock:
            library = self._read()
            if library["version"] == 1:
                try:
                    return self._safe_owned_file(relative, global_root, suffixes)
                except StoreError:
                    return None
            for entry in library["entries"]:
                for asset in entry.get("assets", []):
                    if asset.get("kind") not in kinds or asset.get(field) != relative:
                        continue
                    return self._safe_entry_asset_file(
                        entry, relative, field, global_root, suffixes
                    )
            return None

    def resolve_media_file(self, filename: str) -> Path | None:
        return self._resolve_asset_file(
            field="path",
            filename=filename,
            kinds={"image", "excalidraw"},
            global_root=self.media_dir,
            suffixes={".png", ".jpg", ".jpeg", ".webp"},
        )

    def resolve_excalidraw_file(self, filename: str) -> Path | None:
        return self._resolve_asset_file(
            field="source",
            filename=filename,
            kinds={"excalidraw"},
            global_root=self.diagram_dir,
            suffixes={".excalidraw"},
        )

    def resolve_commutative_file(self, filename: str) -> Path | None:
        return self._resolve_asset_file(
            field="source",
            filename=filename,
            kinds={"commutative"},
            global_root=self.diagram_dir,
            suffixes={".json"},
        )

    @staticmethod
    def _file_signature(path: Path) -> tuple[int, int, int, int, int] | None:
        try:
            status = path.stat()
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise StoreError(f"cannot inspect indexed file: {path.name}") from exc
        return (
            status.st_dev,
            status.st_ino,
            status.st_size,
            status.st_mtime_ns,
            status.st_ctime_ns,
        )

    def _v2_tree_signatures(
        self,
    ) -> dict[Path, tuple[int, int, int, int, int] | None]:
        signatures: dict[Path, tuple[int, int, int, int, int] | None] = {}
        pending = [self.library_dir]
        while pending:
            path = pending.pop()
            signatures[path] = self._file_signature(path)
            if path.is_symlink() or not path.is_dir():
                continue
            try:
                pending.extend(path.iterdir())
            except OSError as exc:
                raise StoreError("cannot inspect the version 2 library tree") from exc
        return signatures

    def _invalidate_search_index(self) -> None:
        self._search_index = None
        self._search_signatures = {}
        self._next_search_staleness_check = 0.0

    def _search_snapshot_matches_disk(self) -> bool:
        if self._search_index is None or not self._search_signatures:
            return False
        try:
            return all(
                self._file_signature(path) == signature
                for path, signature in self._search_signatures.items()
            )
        except StoreError:
            return False

    def _refresh_search_signatures(self, changed_paths: set[Path]) -> None:
        """Keep an index after an atomic write to metadata it does not consume."""
        if any(
            path not in self._search_signatures or path not in self._library_signatures
            for path in changed_paths
        ):
            self._invalidate_search_index()
            return
        for path in changed_paths:
            self._search_signatures[path] = self._library_signatures[path]
        self._next_search_staleness_check = time.monotonic() + SEARCH_STALENESS_SECONDS

    def invalidate_search_index(self) -> None:
        """Invalidate indexes after an out-of-band operation such as Git pull."""
        with self._lock:
            self._invalidate_search_index()

    def _search_files_are_current(self, now: float) -> bool:
        if self._search_index is None:
            return False
        library_signature = self._search_signatures.get(self.library_path)
        if self._file_signature(self.library_path) != library_signature:
            return False
        if now < self._next_search_staleness_check:
            return True
        self._next_search_staleness_check = now + SEARCH_STALENESS_SECONDS
        return all(
            self._file_signature(path) == signature
            for path, signature in self._search_signatures.items()
            if path != self.library_path
        )

    def _read_indexed_content(
        self, relative: str
    ) -> tuple[str, Path, tuple[int, int, int, int, int] | None]:
        path = self._safe_content_path(relative)
        for attempt in range(2):
            before = self._file_signature(path)
            try:
                content = self._read_content(relative)
            except (OSError, UnicodeDecodeError) as exc:
                raise StoreError(f"indexed Markdown is unreadable: {relative}") from exc
            self._search_content_read_count += 1
            after = self._file_signature(path)
            if before == after:
                return content, path, after
            if attempt == 1:
                raise StoreError(f"indexed Markdown changed repeatedly while loading: {relative}")
        raise AssertionError("unreachable")

    def _build_search_index(self) -> LibrarySearchIndex:
        # A Git/manual replacement can race a read. Retry once rather than
        # attaching fresh signatures to an older metadata/content snapshot.
        v2_tree_after: dict[Path, tuple[int, int, int, int, int] | None] = {}
        for attempt in range(2):
            library_before = self._file_signature(self.library_path)
            version_before = self._format_version()
            v2_tree_before = self._v2_tree_signatures() if version_before == 2 else {}
            library = self._read()
            relative_paths = sorted(
                {
                    variant["file"]
                    for entry in library["entries"]
                    for variant in (
                        *entry.get("formulations", []),
                        *entry.get("supplements", []),
                    )
                }
            )
            content_by_path: dict[str, str] = {}
            indexed_paths: dict[Path, tuple[int, int, int, int, int] | None] = {}
            for relative in relative_paths:
                content, path, signature = self._read_indexed_content(relative)
                content_by_path[relative] = content
                indexed_paths[path] = signature
            library_after = self._file_signature(self.library_path)
            v2_tree_after = (
                self._v2_tree_signatures() if library.get("version") == 2 else {}
            )
            if library_before == library_after and v2_tree_before == v2_tree_after:
                break
            if attempt == 1:
                raise StoreError("library changed repeatedly while the search index was loading")

        try:
            namespaces = self._folder_namespaces(library)
            index = LibrarySearchIndex(library, namespaces, content_by_path)
        except (KeyError, SearchIndexError) as exc:
            raise StoreError(str(exc)) from exc
        self._search_index = index
        self._search_signatures = {
            self.library_path: library_after,
            **v2_tree_after,
            **indexed_paths,
        }
        self._next_search_staleness_check = time.monotonic() + SEARCH_STALENESS_SECONDS
        self._search_build_count += 1
        return index

    def _ensure_search_index(self) -> LibrarySearchIndex:
        now = time.monotonic()
        if not self._search_files_are_current(now):
            self._invalidate_search_index()
        return self._search_index or self._build_search_index()

    def reload_search_index(self) -> None:
        """Synchronously reload indexes after Git changes application data."""
        with self._lock:
            self._invalidate_search_index()
            self._build_search_index()

    def search_index_stats(self) -> dict[str, int]:
        """Small test/diagnostic surface; it contains no content."""
        with self._lock:
            index = self._ensure_search_index()
            return {
                "builds": self._search_build_count,
                "content_reads": self._search_content_read_count,
                "entries": len(index.entry_documents),
                "targets": len(index.targets),
                "indexed_files": len(self._search_signatures) - 1,
                "staleness_bound_ms": round(SEARCH_STALENESS_SECONDS * 1000),
            }

    def search(
        self, query: str, limit: int = 40, folder_id: str | None = None
    ) -> list[dict[str, Any]]:
        if limit <= 0:
            return []
        with self._lock:
            index = self._ensure_search_index()
            try:
                return index.search_entries(query, min(limit, 200), folder_id)
            except SearchIndexError as exc:
                raise StoreError(str(exc)) from exc

    def resolve_reference(self, folder_id: str, reference: str) -> dict[str, Any]:
        with self._lock:
            index = self._ensure_search_index()
            try:
                return index.resolve(folder_id, reference)
            except SearchIndexError as exc:
                raise StoreError(str(exc)) from exc

    def reference_candidates(
        self, folder_id: str, query: str = "", limit: int = 40
    ) -> list[dict[str, Any]]:
        if limit <= 0:
            return []
        with self._lock:
            index = self._ensure_search_index()
            try:
                return index.search_visible_references(folder_id, query, min(limit, 200))
            except SearchIndexError as exc:
                raise StoreError(str(exc)) from exc
