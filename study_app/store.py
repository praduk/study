from __future__ import annotations

import copy
import json
import os
import re
import threading
import time
import uuid
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .library_validation import LibraryValidationError, validate_library
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


class StoreError(ValueError):
    pass


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
        self.content_dir = self.data_dir / "content"
        self.media_dir = self.data_dir / "media"
        self.diagram_dir = self.data_dir / "diagrams"
        self.templates_dir = self.data_dir / "excalidraw" / "templates"
        self.exports_dir = self.data_dir / "exports"
        self.runtime_dir = self.data_dir / "runtime"
        self._lock = threading.RLock()
        self._search_index: LibrarySearchIndex | None = None
        self._search_signatures: dict[Path, tuple[int, int, int, int, int] | None] = {}
        self._next_search_staleness_check = 0.0
        self._search_build_count = 0
        self._search_content_read_count = 0
        self._ensure_layout()

    @property
    def mutation_lock(self) -> Any:
        """Application-wide lock shared with review and Git mutations."""
        return self._lock

    def _ensure_layout(self) -> None:
        root = self.data_dir.resolve()
        for directory in (
            self.data_dir,
            self.content_dir,
            self.media_dir,
            self.diagram_dir,
            self.templates_dir,
            self.exports_dir,
            self.runtime_dir,
        ):
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
            _atomic_json(self.library_path, {"version": 1, "folders": [], "entries": []})
        if not self.macros_path.exists():
            _atomic_json(self.macros_path, {"version": 1, "macros": {}})

    def ensure_layout(self) -> None:
        """Recheck/recreate safe auxiliary directories after a Git fast-forward."""
        with self._lock:
            self._ensure_layout()

    def _read(self) -> dict[str, Any]:
        try:
            with self.library_path.open(encoding="utf-8") as stream:
                library = json.load(stream)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise StoreError("library.json is unreadable or invalid") from exc
        if not isinstance(library, dict) or library.get("version") != 1:
            raise StoreError("unsupported library version")
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
        _atomic_json(self.library_path, library)
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
            raise StoreError("content files must be Markdown files inside data/content")
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
                    path = self._safe_owned_file(relative, root, suffixes)
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
    ) -> tuple[set[Path], list[str]]:
        paths: set[Path] = set()
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
                        paths.add(self._safe_owned_file(relative, root, suffixes))
        return paths, markdown

    def _plan_unreferenced_files(
        self,
        content_files: dict[Path, str],
        asset_files: dict[Path, tuple[str, set[str]]],
        surviving_entries: list[dict[str, Any]],
    ) -> tuple[dict[Path, str], dict[Path, str]]:
        surviving_asset_paths, surviving_markdown = self._surviving_asset_references(
            surviving_entries
        )
        preserved = {
            path: relative
            for path, (relative, tokens) in asset_files.items()
            if path in surviving_asset_paths
            or any(token in text for token in tokens for text in surviving_markdown)
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
        """Delete one entry while retaining review history and shared asset files."""
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
            relative = f"content/{entry_id}/{formulation_id}.md"
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
            relative = f"content/{entry_id}/{variant_id}.md"
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
            relative = f"content/{entry_id}/{variant_id}.md"
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

    def register_asset(self, entry_id: str, asset: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            library = self._read()
            entry = self._entry(library, entry_id)
            entry.setdefault("assets", []).append(asset)
            entry["updated_at"] = _now()
            self._write(library)
            return asset

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

    def _invalidate_search_index(self) -> None:
        self._search_index = None
        self._search_signatures = {}
        self._next_search_staleness_check = 0.0

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
        # A Git/manual replacement of library.json can race a read. Retry once rather
        # than attaching a fresh file signature to an older metadata snapshot.
        for attempt in range(2):
            library_before = self._file_signature(self.library_path)
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
            if library_before == library_after:
                break
            if attempt == 1:
                raise StoreError("library changed repeatedly while the search index was loading")

        try:
            namespaces = self._folder_namespaces(library)
            index = LibrarySearchIndex(library, namespaces, content_by_path)
        except (KeyError, SearchIndexError) as exc:
            raise StoreError(str(exc)) from exc
        self._search_index = index
        self._search_signatures = {self.library_path: library_after, **indexed_paths}
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
