from __future__ import annotations

import json
import re
import threading
import warnings
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError
from pydantic import ValidationError

from .models import CommutativeDiagramCreate

SLUG_RE = re.compile(r"^[a-z][a-z0-9-]*$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
MEDIA_PATH_RE = re.compile(r"^media/[a-f0-9]{64}\.(?:png|jpe?g|webp)$")
EXCALIDRAW_PATH_RE = re.compile(r"^diagrams/[a-f0-9]{32}\.excalidraw$")
COMMUTATIVE_PATH_RE = re.compile(r"^diagrams/[a-f0-9]{32}\.commutative\.json$")
MAX_FOLDER_DEPTH = 64
# The longest valid canonical reference at the maximum depth is under 4,400 characters.
MAX_REFERENCE_QUERY_LENGTH = 8192
IMAGE_DECODE_LOCK = threading.Lock()
KINDS = {"ax", "df", "rk", "th", "pb"}
ALT_KINDS = {"ax", "df", "th"}
SUPPLEMENT_BY_ENTRY = {"th": "pf", "pb": "sl"}
# Known legacy modes remain readable so older checked-in libraries can be
# normalized by LibraryStore on their next write. New writes use fixed modes.
REVIEW_MODES_BY_KIND = {
    "ax": {"statement", "example", "discriminate", "transfer"},
    "df": {"statement", "example", "discriminate", "transfer"},
    "rk": {"statement", "explain", "example", "transfer"},
    "th": {"statement", "proof-plan", "transfer"},
    "pb": {"solve", "transfer"},
}


class LibraryValidationError(ValueError):
    pass


def _record(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LibraryValidationError(f"{label} must be an object")
    return value


def _identifier(value: Any, label: str) -> str:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        raise LibraryValidationError(f"{label} has an invalid id")
    return value


def _nonblank(value: Any, label: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise LibraryValidationError(f"{label} must be nonblank and at most {maximum} characters")
    return value


def _slug(value: Any, label: str, maximum: int) -> str:
    if not isinstance(value, str) or len(value) > maximum or not SLUG_RE.fullmatch(value):
        raise LibraryValidationError(
            f"{label} must start with a lowercase letter and contain only letters, digits, or hyphens"
        )
    return value


def _order(value: Any, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise LibraryValidationError(f"{label} order must be a nonnegative integer")


def _existing_file(
    data_dir: Path,
    relative: Any,
    root: Path,
    label: str,
    suffixes: set[str],
) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise LibraryValidationError(f"{label} has an invalid path")
    unresolved = data_dir / relative
    try:
        candidate = unresolved.resolve()
        resolved_root = root.resolve()
    except OSError as exc:
        raise LibraryValidationError(f"{label} path cannot be resolved") from exc
    if resolved_root not in candidate.parents or candidate.suffix.casefold() not in suffixes:
        raise LibraryValidationError(f"{label} escapes its allowed data directory")
    if unresolved.is_symlink() or not candidate.is_file():
        raise LibraryValidationError(f"{label} is missing or is not a regular file: {relative}")
    return candidate


def _asset_path(value: Any, label: str, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise LibraryValidationError(f"{label} is not reachable through a Study asset route")
    return value


def _validate_image(path: Path, label: str) -> tuple[int, int]:
    expected_format = {
        ".png": "PNG",
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".webp": "WEBP",
    }[path.suffix.casefold()]
    try:
        with IMAGE_DECODE_LOCK, warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as opened:
                if opened.format != expected_format:
                    raise LibraryValidationError(
                        f"{label} contents do not match its filename extension"
                    )
                if getattr(opened, "is_animated", False):
                    raise LibraryValidationError(f"{label} cannot be animated")
                width, height = opened.size
                if width <= 0 or height <= 0:
                    raise LibraryValidationError(f"{label} has invalid dimensions")
                opened.verify()
    except LibraryValidationError:
        raise
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        raise LibraryValidationError(f"{label} is not a valid image") from exc
    except Image.DecompressionBombWarning as exc:
        raise LibraryValidationError(f"{label} is too large to validate safely") from exc
    return width, height


def _json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as stream:
            value = json.load(stream)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise LibraryValidationError(f"{label} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise LibraryValidationError(f"{label} must contain a JSON object")
    return value


def _validate_asset_metadata(asset: dict[str, Any], label: str) -> None:
    _nonblank(asset.get("alt"), f"{label} alt text", 240)
    width = asset.get("width")
    if isinstance(width, bool) or not isinstance(width, int) or not 10 <= width <= 100:
        raise LibraryValidationError(f"{label} width must be an integer from 10 through 100")
    if "invert_lightness" in asset and not isinstance(asset["invert_lightness"], bool):
        raise LibraryValidationError(f"{label} invert_lightness must be true or false")


def _validate_pixel_metadata(asset: dict[str, Any], dimensions: tuple[int, int], label: str) -> None:
    pixels = asset.get("pixels")
    if pixels is None:
        return
    if (
        not isinstance(pixels, list)
        or len(pixels) != 2
        or any(isinstance(value, bool) or not isinstance(value, int) or value <= 0 for value in pixels)
    ):
        raise LibraryValidationError(f"{label} pixels must contain two positive integers")
    if tuple(pixels) != dimensions:
        raise LibraryValidationError(f"{label} pixel metadata does not match its image")


def _validate_variant_group(
    *,
    entry_id: str,
    kind: str,
    group_name: str,
    values: Any,
    data_dir: Path,
    content_dir: Path,
    record_ids: set[str],
    content_files: set[Path],
    expected_supplement: str | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(values, list):
        raise LibraryValidationError(f"entry {entry_id} {group_name} must be a list")
    if group_name == "formulations" and not values:
        raise LibraryValidationError(f"entry {entry_id} must have at least one formulation")
    if group_name == "formulations" and kind not in ALT_KINDS and len(values) != 1:
        raise LibraryValidationError(f"entry {entry_id} cannot have alternative formulations")
    if group_name == "supplements" and values and expected_supplement is None:
        raise LibraryValidationError(f"entry {entry_id} cannot have proofs or solutions")

    parsed: list[dict[str, Any]] = []
    subtags: set[str] = set()
    main_count = 0
    for index, raw in enumerate(values):
        label = f"entry {entry_id} {group_name}[{index}]"
        variant = _record(raw, label)
        variant_id = _identifier(variant.get("id"), label)
        if variant_id in record_ids:
            raise LibraryValidationError(f"duplicate record id: {variant_id}")
        record_ids.add(variant_id)
        _nonblank(variant.get("label"), f"{label} label", 120)
        if not isinstance(variant.get("main"), bool):
            raise LibraryValidationError(f"{label} main must be true or false")
        main = variant["main"]
        main_count += int(main)
        subtag = variant.get("subtag")
        if main:
            if subtag is not None:
                raise LibraryValidationError(f"{label} main variant cannot have a subtag")
        else:
            subtag = _slug(subtag, f"{label} subtag", 80)
            if subtag in subtags:
                raise LibraryValidationError(f"entry {entry_id} has a duplicate {group_name} subtag")
            subtags.add(subtag)
        if group_name == "formulations":
            reserved = SUPPLEMENT_BY_ENTRY.get(kind)
            if subtag is not None and subtag == reserved:
                raise LibraryValidationError(
                    f"entry {entry_id} formulation subtag {subtag!r} is reserved"
                )
        elif variant.get("kind") != expected_supplement:
            raise LibraryValidationError(f"entry {entry_id} has an incompatible supplement")
        content_path = _existing_file(
            data_dir,
            variant.get("file"),
            content_dir,
            f"{label} Markdown",
            {".md"},
        )
        if content_path in content_files:
            raise LibraryValidationError(f"Markdown file is referenced more than once: {variant['file']}")
        content_files.add(content_path)
        parsed.append(variant)

    if values and main_count != 1:
        raise LibraryValidationError(f"entry {entry_id} {group_name} must have exactly one main item")
    return parsed


def _validate_assets(
    entry_id: str,
    values: Any,
    data_dir: Path,
    media_dir: Path,
    diagram_dir: Path,
    asset_ids: set[str],
) -> None:
    if not isinstance(values, list):
        raise LibraryValidationError(f"entry {entry_id} assets must be a list")
    for index, raw in enumerate(values):
        label = f"entry {entry_id} assets[{index}]"
        asset = _record(raw, label)
        asset_id = _identifier(asset.get("id"), label)
        if asset_id in asset_ids:
            raise LibraryValidationError(f"duplicate asset id: {asset_id}")
        asset_ids.add(asset_id)
        kind = asset.get("kind")
        if kind not in {"image", "excalidraw", "commutative"}:
            raise LibraryValidationError(f"{label} has an invalid kind")
        _validate_asset_metadata(asset, label)
        if kind in {"image", "excalidraw"}:
            preview_relative = _asset_path(
                asset.get("path"), f"{label} preview path", MEDIA_PATH_RE
            )
            preview = _existing_file(
                data_dir,
                preview_relative,
                media_dir,
                f"{label} preview",
                {".png", ".jpg", ".jpeg", ".webp"},
            )
            dimensions = _validate_image(preview, f"{label} preview")
            _validate_pixel_metadata(asset, dimensions, label)
        if kind == "excalidraw":
            source_relative = _asset_path(
                asset.get("source"), f"{label} source path", EXCALIDRAW_PATH_RE
            )
            if source_relative != f"diagrams/{asset_id}.excalidraw":
                raise LibraryValidationError(f"{label} source does not match its asset id")
            source = _existing_file(
                data_dir,
                source_relative,
                diagram_dir,
                f"{label} source",
                {".excalidraw"},
            )
            scene = _json_object(source, f"{label} Excalidraw source")
            if not isinstance(scene.get("elements", []), list):
                raise LibraryValidationError(f"{label} Excalidraw elements must be a list")
        elif kind == "commutative":
            source_relative = _asset_path(
                asset.get("source"), f"{label} source path", COMMUTATIVE_PATH_RE
            )
            if source_relative != f"diagrams/{asset_id}.commutative.json":
                raise LibraryValidationError(f"{label} source does not match its asset id")
            source = _existing_file(
                data_dir,
                source_relative,
                diagram_dir,
                f"{label} source",
                {".json"},
            )
            diagram = _json_object(source, f"{label} commutative source")
            if diagram.get("version") != 1:
                raise LibraryValidationError(f"{label} commutative source has an invalid version")
            try:
                parsed = CommutativeDiagramCreate.model_validate(diagram)
            except ValidationError as exc:
                raise LibraryValidationError(
                    f"{label} commutative source has an invalid structure"
                ) from exc
            node_ids = [node.id for node in parsed.nodes]
            if len(node_ids) != len(set(node_ids)):
                raise LibraryValidationError(f"{label} commutative source has duplicate node ids")
            known_nodes = set(node_ids)
            if any(
                arrow.source not in known_nodes or arrow.target not in known_nodes
                for arrow in parsed.arrows
            ):
                raise LibraryValidationError(
                    f"{label} commutative source has an unknown arrow endpoint"
                )


def validate_library(
    library: dict[str, Any],
    data_dir: Path,
    content_dir: Path,
    media_dir: Path,
    diagram_dir: Path,
) -> None:
    """Reject corrupt Git/manual edits before they can be silently interpreted."""
    folders = library.get("folders")
    entries = library.get("entries")
    if not isinstance(folders, list) or not isinstance(entries, list):
        raise LibraryValidationError("library.json must contain folder and entry lists")

    folder_by_id: dict[str, dict[str, Any]] = {}
    record_ids: set[str] = set()
    sibling_slugs: set[tuple[str | None, str]] = set()
    for index, raw in enumerate(folders):
        label = f"folders[{index}]"
        folder = _record(raw, label)
        folder_id = _identifier(folder.get("id"), label)
        if folder_id in record_ids:
            raise LibraryValidationError(f"duplicate record id: {folder_id}")
        record_ids.add(folder_id)
        folder_by_id[folder_id] = folder
        _nonblank(folder.get("name"), f"folder {folder_id} name", 120)
        slug = _slug(folder.get("slug"), f"folder {folder_id} namespace", 64)
        parent_id = folder.get("parent_id")
        if parent_id is not None:
            _identifier(parent_id, f"folder {folder_id} parent")
        sibling_key = (parent_id, slug)
        if sibling_key in sibling_slugs:
            raise LibraryValidationError("sibling folder namespace segments must be unique")
        sibling_slugs.add(sibling_key)
        _order(folder.get("order"), f"folder {folder_id}")
        if not isinstance(folder.get("review_enabled"), bool):
            raise LibraryValidationError(f"folder {folder_id} review_enabled must be true or false")

    for folder_id, folder in folder_by_id.items():
        parent_id = folder.get("parent_id")
        if parent_id is not None and parent_id not in folder_by_id:
            raise LibraryValidationError(f"folder {folder_id} has a missing parent")
    for folder_id in folder_by_id:
        seen: set[str] = set()
        cursor: str | None = folder_id
        while cursor is not None:
            if cursor in seen:
                raise LibraryValidationError("folder cycle detected")
            seen.add(cursor)
            if len(seen) > MAX_FOLDER_DEPTH:
                raise LibraryValidationError(
                    f"folder nesting cannot exceed {MAX_FOLDER_DEPTH} levels"
                )
            cursor = folder_by_id[cursor].get("parent_id")

    entry_keys: set[tuple[str, str, str]] = set()
    content_files: set[Path] = set()
    asset_ids: set[str] = set()
    for index, raw in enumerate(entries):
        label = f"entries[{index}]"
        entry = _record(raw, label)
        entry_id = _identifier(entry.get("id"), label)
        if entry_id in record_ids:
            raise LibraryValidationError(f"duplicate record id: {entry_id}")
        record_ids.add(entry_id)
        folder_id = entry.get("folder_id")
        if folder_id not in folder_by_id:
            raise LibraryValidationError(f"entry {entry_id} has a missing folder")
        kind = entry.get("kind")
        if kind not in KINDS:
            raise LibraryValidationError(f"entry {entry_id} has an invalid content type")
        _nonblank(entry.get("title"), f"entry {entry_id} title", 240)
        tag = _slug(entry.get("tag"), f"entry {entry_id} tag", 80)
        entry_key = (folder_id, kind, tag)
        if entry_key in entry_keys:
            raise LibraryValidationError(
                "entry tags must be unique within a folder and content type"
            )
        entry_keys.add(entry_key)
        if not isinstance(entry.get("header"), str) or len(entry["header"]) > 4000:
            raise LibraryValidationError(f"entry {entry_id} header must be text")
        _order(entry.get("order"), f"entry {entry_id}")

        formulations = _validate_variant_group(
            entry_id=entry_id,
            kind=kind,
            group_name="formulations",
            values=entry.get("formulations"),
            data_dir=data_dir,
            content_dir=content_dir,
            record_ids=record_ids,
            content_files=content_files,
        )
        expected_supplement = SUPPLEMENT_BY_ENTRY.get(kind)
        supplements = _validate_variant_group(
            entry_id=entry_id,
            kind=kind,
            group_name="supplements",
            values=entry.get("supplements"),
            data_dir=data_dir,
            content_dir=content_dir,
            record_ids=record_ids,
            content_files=content_files,
            expected_supplement=expected_supplement,
        )
        modes = entry.get("review_modes")
        if (
            not isinstance(modes, list)
            or len(modes) > 12
            or any(not isinstance(mode, str) or mode not in REVIEW_MODES_BY_KIND[kind] for mode in modes)
            or len(modes) != len(set(modes))
        ):
            raise LibraryValidationError(f"entry {entry_id} has invalid review modes")
        main_supplement = next((item for item in supplements if item.get("main")), None)
        if "proof-plan" in modes and (
            expected_supplement != "pf" or main_supplement is None
        ):
            raise LibraryValidationError(f"entry {entry_id} proof-plan mode requires a main proof")
        if "solve" in modes and (expected_supplement != "sl" or main_supplement is None):
            raise LibraryValidationError(f"entry {entry_id} solve mode requires a main solution")
        if not modes and not (kind == "pb" and main_supplement is None):
            raise LibraryValidationError(f"entry {entry_id} must select at least one review mode")
        if not isinstance(entry.get("problem_family"), str):
            raise LibraryValidationError(f"entry {entry_id} problem_family must be text")
        confusable = entry.get("confusable_with")
        if not isinstance(confusable, list) or any(not isinstance(item, str) for item in confusable):
            raise LibraryValidationError(f"entry {entry_id} confusable_with must be a list of text")
        _validate_assets(
            entry_id,
            entry.get("assets"),
            data_dir,
            media_dir,
            diagram_dir,
            asset_ids,
        )
        if not formulations:
            raise AssertionError("validated formulations unexpectedly empty")
