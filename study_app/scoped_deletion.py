"""Durable, recoverable moves of explicitly selected v2 deletion roots.

The store owns schema validation and coherence checks. This journal owns only
bounded filesystem moves, recovery, and the durable review-purge acknowledgement.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import stat
import uuid
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

from .library_validation import COMMUTATIVE_PATH_RE, EXCALIDRAW_PATH_RE, ID_RE, MEDIA_PATH_RE

TRANSACTION_RE = re.compile(r"library-delete-([a-f0-9]{32})\.tmp")
SLUG_RE = re.compile(r"[a-z][a-z0-9-]*")
DEEP_RE = re.compile(r"[a-f0-9]{32}-[a-z][a-z0-9-]*")


class ScopedDeletionError(ValueError):
    pass


class ScopedDeletions:
    def __init__(
        self, data_dir: Path, atomic_json: Callable[[Path, Any], None],
        fsync_directory: Callable[[Path], None],
    ):
        self.data_dir = data_dir
        self.runtime_dir = data_dir / "runtime"
        self._atomic_json = atomic_json
        self._fsync = fsync_directory

    @staticmethod
    def _safe(path: Path, *, leaf_missing: bool = False) -> None:
        # Check every existing component without following a link, including
        # runtime parents: recovery journals are untrusted filesystem input.
        for component in (path, *path.parents):
            try:
                mode = component.lstat().st_mode
            except FileNotFoundError:
                if component == path and leaf_missing:
                    continue
                raise ScopedDeletionError("deletion recovery path is missing") from None
            if stat.S_ISLNK(mode):
                raise ScopedDeletionError("deletion recovery path is a symbolic link")

    def _directory(self, transaction_id: str) -> Path:
        if not isinstance(transaction_id, str) or not re.fullmatch(r"[a-f0-9]{32}", transaction_id):
            raise ScopedDeletionError("invalid deletion transaction ID")
        return self.runtime_dir / f"library-delete-{transaction_id}.tmp"

    def _source(self, record: dict[str, Any]) -> Path:
        if not isinstance(record, dict) or set(record) != {"path", "kind", "id", "identity"}:
            raise ScopedDeletionError("invalid deletion root")
        relative, kind, item_id, identity = (
            record["path"], record["kind"], record["id"], record["identity"]
        )
        if (
            not isinstance(relative, str) or not relative or "\\" in relative
            or Path(relative).is_absolute() or Path(relative).as_posix() != relative
            or any(part in {"", ".", ".."} for part in relative.split("/"))
            or not isinstance(identity, list) or len(identity) != 2
            or any(type(value) is not int or value < 0 for value in identity)
        ):
            raise ScopedDeletionError("unsafe deletion root")
        parts = relative.split("/")
        if kind == "asset":
            if item_id is not None or not any(pattern.fullmatch(relative) for pattern in (
                MEDIA_PATH_RE, EXCALIDRAW_PATH_RE, COMMUTATIVE_PATH_RE,
            )):
                raise ScopedDeletionError("unsafe deletion asset root")
        elif kind in {"entry", "folder"}:
            if not isinstance(item_id, str) or not ID_RE.fullmatch(item_id):
                raise ScopedDeletionError("invalid deleted item ID")
            folders = parts[1:-3] if kind == "entry" else parts[1:]
            if parts[0] != "library" or not folders:
                raise ScopedDeletionError("unsafe deletion library root")
            if kind == "entry" and (
                len(parts) < 5 or parts[-3] != "_items" or parts[-2] not in {"ax", "df", "rk", "th", "pb"}
                or not SLUG_RE.fullmatch(parts[-1])
            ):
                raise ScopedDeletionError("unsafe deleted entry path")
            if folders[0] == "_deep":
                valid = len(folders) == 2 and DEEP_RE.fullmatch(folders[1])
            else:
                valid = all(SLUG_RE.fullmatch(part) for part in folders)
            if not valid:
                raise ScopedDeletionError("unsafe deleted folder path")
        else:
            raise ScopedDeletionError("invalid deletion root kind")
        return self.data_dir / relative

    def _read(self, directory: Path) -> dict[str, Any]:
        self._safe(directory)
        path = directory / "journal.json"
        self._safe(path)
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeError) as exc:
            raise ScopedDeletionError("deletion journal is unreadable") from exc
        if (
            not isinstance(value, dict) or set(value) != {"version", "state", "entry_ids", "roots"}
            or value["version"] != 1
            or value["state"] not in {"prepared", "committed", "review-complete", "rolled-back"}
            or not isinstance(value["entry_ids"], list)
            or any(not isinstance(item, str) or not ID_RE.fullmatch(item) for item in value["entry_ids"])
            or len(set(value["entry_ids"])) != len(value["entry_ids"])
            or not isinstance(value["roots"], list) or not value["roots"]
        ):
            raise ScopedDeletionError("invalid deletion journal")
        roots = [self._source(record) for record in value["roots"]]
        if len(set(roots)) != len(roots) or any(
            left in right.parents for left in roots for right in roots if left != right
        ):
            raise ScopedDeletionError("overlapping deletion roots")
        return value

    def _journals(self) -> list[tuple[str, Path, dict[str, Any]]]:
        self._safe(self.runtime_dir)
        journals = []
        for directory in sorted(self.runtime_dir.iterdir()):
            match = TRANSACTION_RE.fullmatch(directory.name)
            if match:
                journals.append((match[1], directory, self._read(directory)))
        return journals

    def _write(self, directory: Path, value: dict[str, Any], state: str) -> None:
        self._safe(directory)
        self._safe(directory / "journal.json", leaf_missing=True)
        updated = {**value, "state": state}
        self._atomic_json(directory / "journal.json", updated)
        self._fsync(directory)
        value["state"] = state

    def ensure_ready(self) -> None:
        if any(value["state"] == "prepared" for _, _, value in self._journals()):
            raise ScopedDeletionError("an interrupted deletion requires recovery before using the library")

    def _check_tombstones(self, directory: Path, value: dict[str, Any]) -> None:
        """A journal may purge only entry IDs present in its detached roots."""
        found = []
        trash = directory / "trash"
        self._safe(trash)
        for position, record in enumerate(value["roots"]):
            saved = trash / str(position)
            self._verify_identity(saved, record)
            if record["kind"] == "asset":
                continue
            for parent, directories, files in os.walk(saved, followlinks=False):
                base = Path(parent)
                for name in (*directories, *files):
                    self._safe(base / name)
                if "_entry.json" in files:
                    try:
                        metadata = json.loads((base / "_entry.json").read_text(encoding="utf-8"))
                    except (OSError, ValueError, UnicodeError) as exc:
                        raise ScopedDeletionError("deleted entry metadata is unreadable") from exc
                    item_id = metadata.get("id") if isinstance(metadata, dict) else None
                    if not isinstance(item_id, str) or not ID_RE.fullmatch(item_id):
                        raise ScopedDeletionError("invalid deleted entry identity")
                    found.append(item_id)
        if len(found) != len(set(found)) or set(found) != set(value["entry_ids"]):
            raise ScopedDeletionError("deletion tombstones do not match detached entry identities")

    def pending(self) -> dict[str, list[str]]:
        self.ensure_ready()
        result = {}
        for transaction_id, directory, value in self._journals():
            if value["state"] == "committed":
                self._check_tombstones(directory, value)
                result[transaction_id] = list(value["entry_ids"])
            elif value["state"] == "review-complete":
                # An atomic state-file replacement may have succeeded while
                # its directory fsync failed. Do not permit new grading until
                # the acknowledgement is known durable, even on a later call.
                self._fsync(directory)
        return result

    def complete(self, transaction_ids: Iterable[str]) -> None:
        self.ensure_ready()
        # The review engine has atomically replaced its state/log files. Their
        # parent must be durable before acknowledging the intent that protects it.
        self._fsync(self.data_dir)
        for transaction_id in transaction_ids:
            directory = self._directory(transaction_id)
            value = self._read(directory)
            if value["state"] == "committed":
                self._write(directory, value, "review-complete")
            elif value["state"] == "review-complete":
                self._fsync(directory)
            else:
                raise ScopedDeletionError("cannot acknowledge an uncommitted deletion")

    def _discard(self, directory: Path) -> None:
        # Remove the journal from the active namespace atomically. A interrupted
        # recursive unlink can otherwise leave an active directory without its
        # journal and prevent every future read.
        garbage = self.runtime_dir / f"library-delete-garbage-{uuid.uuid4().hex}.tmp"
        self._move(directory, garbage)
        shutil.rmtree(garbage)
        self._fsync(self.runtime_dir)

    def cleanup(self) -> None:
        for _, directory, value in self._journals():
            if value["state"] == "review-complete":
                self._fsync(directory)
                try:
                    self._discard(directory)
                except OSError:
                    # Cleanup is inert after acknowledgement; retry next startup.
                    continue
        for directory in self.runtime_dir.iterdir():
            if re.fullmatch(r"library-delete-garbage-[a-f0-9]{32}\.tmp", directory.name):
                try:
                    self._safe(directory)
                    # A previous retirement rename may have become visible
                    # just before its fsync failed. Durably retire it first.
                    self._fsync(self.runtime_dir)
                    shutil.rmtree(directory)
                    self._fsync(self.runtime_dir)
                except OSError:
                    continue

    def _verify_identity(self, path: Path, record: dict[str, Any]) -> None:
        self._safe(path)
        status = path.stat()
        if [status.st_dev, status.st_ino] != record["identity"]:
            raise ScopedDeletionError("deleted root was replaced during recovery")
        if record["kind"] != "asset":
            sidecar = path / ("_entry.json" if record["kind"] == "entry" else "_folder.json")
            self._safe(sidecar)
            try:
                metadata = json.loads(sidecar.read_text(encoding="utf-8"))
            except (OSError, ValueError, UnicodeError) as exc:
                raise ScopedDeletionError("deleted root metadata is unreadable") from exc
            if not isinstance(metadata, dict) or metadata.get("id") != record["id"]:
                raise ScopedDeletionError("deleted root metadata does not match its journal")

    def _parent_descriptor(self, path: Path) -> int:
        """Open each parent without following links, retaining its identity."""
        self._safe(self.data_dir)
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(self.data_dir, flags)
        try:
            for part in path.parent.relative_to(self.data_dir).parts:
                child = os.open(part, flags, dir_fd=descriptor)
                os.close(descriptor)
                descriptor = child
            return descriptor
        except BaseException:
            os.close(descriptor)
            raise

    def _move(self, source: Path, destination: Path, *, preserve_link: bool = False) -> None:
        if os.name != "nt" and os.rename in os.supports_dir_fd:
            source_parent = self._parent_descriptor(source)
            try:
                destination_parent = self._parent_descriptor(destination)
                try:
                    status = os.stat(source.name, dir_fd=source_parent, follow_symlinks=False)
                    if stat.S_ISLNK(status.st_mode) and not preserve_link:
                        raise ScopedDeletionError("deletion source is a symbolic link")
                    try:
                        os.stat(destination.name, dir_fd=destination_parent, follow_symlinks=False)
                    except FileNotFoundError:
                        pass
                    else:
                        raise ScopedDeletionError("deletion destination already exists")
                    os.rename(source.name, destination.name,
                              src_dir_fd=source_parent, dst_dir_fd=destination_parent)
                    os.fsync(source_parent)
                    os.fsync(destination_parent)
                finally:
                    os.close(destination_parent)
            finally:
                os.close(source_parent)
        else:  # pragma: no cover - Windows has no dirfd rename support.
            self._safe(source.parent if preserve_link else source)
            self._safe(destination, leaf_missing=True)
            if destination.exists() or destination.is_symlink():
                raise ScopedDeletionError("deletion destination already exists")
            os.rename(source, destination)
            self._fsync(source.parent)
            self._fsync(destination.parent)

    def rollback(self, directory: Path, value: dict[str, Any]) -> None:
        trash = directory / "trash"
        self._safe(trash)
        for position, record in reversed(list(enumerate(value["roots"]))):
            source, saved = self._source(record), trash / str(position)
            self._safe(source.parent)
            if saved.exists() or saved.is_symlink():
                self._verify_identity(saved, record)
                if source.exists() or source.is_symlink():
                    conflicts = directory / "conflicts"
                    conflicts.mkdir(exist_ok=True)
                    self._safe(conflicts)
                    # Preserve a newly created live path, even a leaf symlink,
                    # without traversing or overwriting it.
                    self._move(source, conflicts / f"{position}-{uuid.uuid4().hex}", preserve_link=True)
                self._move(saved, source)
            else:
                self._verify_identity(source, record)
        self._write(directory, value, "rolled-back")
        if not (directory / "conflicts").exists():
            try:
                self._discard(directory)
            except OSError:
                pass

    def recover(self, *, conflicting_writes: bool = False) -> None:
        journals = self._journals()
        if conflicting_writes and any(value["state"] == "prepared" for _, _, value in journals):
            raise ScopedDeletionError("conflicting interrupted library writes require recovery")
        for _, directory, value in journals:
            if value["state"] == "prepared":
                self.rollback(directory, value)

    def commit(
        self, roots: list[dict[str, Any]], entry_ids: Iterable[str],
        verify: Callable[[dict[Path, Path]], None],
    ) -> str:
        self.ensure_ready()
        transaction_id = uuid.uuid4().hex
        directory = self._directory(transaction_id)
        staging = self.runtime_dir / f"library-delete-preparing-{transaction_id}.tmp"
        staging.mkdir()
        (staging / "trash").mkdir()
        value = {"version": 1, "state": "prepared", "entry_ids": list(entry_ids), "roots": roots}
        # No authored move is allowed until the prepared journal is durable.
        try:
            self._write(staging, value, "prepared")
            self._move(staging, directory)
        except BaseException:
            shutil.rmtree(staging, ignore_errors=True)
            raise
        trash = directory / "trash"
        mapping = {self._source(record): trash / str(index) for index, record in enumerate(roots)}
        try:
            for record in roots:
                source = self._source(record)
                self._verify_identity(source, record)
                self._move(source, mapping[source])
            verify(mapping)
            self._write(directory, value, "committed")
        except BaseException:
            # A rename of the committed journal can succeed just before fsync
            # fails. Never resurrect a transaction whose committed state may be durable.
            on_disk = self._read(directory)
            if on_disk["state"] == "prepared":
                self.rollback(directory, on_disk)
            raise
        return directory.name[len("library-delete-"):-len(".tmp")]
