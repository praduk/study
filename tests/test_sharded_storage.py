from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import threading
import time
from pathlib import Path

import pytest
from PIL import Image

from study_app.git_ops import GitRepository
from study_app.store import SEARCH_STALENESS_SECONDS, LibraryStore, StoreError


def _png_bytes(width: int = 4, height: int = 3) -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (width, height), "#638b7d").save(output, "PNG")
    return output.getvalue()


def _image_asset(image: bytes, asset_id: str = "image-asset") -> dict:
    filename = f"{hashlib.sha256(image).hexdigest()}.png"
    return {
        "id": asset_id,
        "kind": "image",
        "path": f"media/{filename}",
        "alt": "A diagram preview",
        "width": 70,
        "invert_lightness": False,
        "pixels": [4, 3],
    }


def _git(directory: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(directory), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_fresh_data_root_initializes_directly_as_v2(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")

    assert json.loads(store.library_path.read_text()) == {"version": 2, "root": "library"}
    assert json.loads((store.library_dir / "_library.json").read_text()) == {"version": 1}
    assert not store.legacy_content_dir.exists()
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    assert store.get_entry(entry["id"])["formulations"][0]["content"] == "Body\n"


def test_data_check_rejects_non_utf8_markdown(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    source = store.data_dir / entry["formulations"][0]["file"]
    source.write_bytes(b"\xff\xfe")

    with pytest.raises(StoreError, match="unreadable"):
        store.check_data()


def test_v2_crud_moves_paths_but_preserves_stable_ids_and_sparse_peer_metadata(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    source = store.create_folder("Source", "source", None)
    destination = store.create_folder("Destination", "destination", None)
    first = store.create_entry(source["id"], "df", "First", "first", "", "First")
    last = store.create_entry(source["id"], "df", "Last", "last", "", "Last")
    first_metadata = next(store.library_dir.rglob("first/_entry.json"))
    last_metadata = next(store.library_dir.rglob("last/_entry.json"))
    first_before = first_metadata.read_bytes()
    last_before = last_metadata.read_bytes()
    middle = store.create_entry(
        source["id"], "th", "Middle", "middle", "", "Middle", index=1
    )

    assert first_metadata.read_bytes() == first_before
    assert last_metadata.read_bytes() == last_before
    assert [entry["id"] for entry in store.snapshot()["tree"][0]["entries"]] == [
        first["id"],
        middle["id"],
        last["id"],
    ]

    store.move_item("entry", middle["id"], destination["id"], 0)
    store.update_folder(destination["id"], {"slug": "target"})
    moved = store.get_entry(middle["id"])
    assert moved["id"] == middle["id"]
    assert moved["canonical_tag"] == "target:th:middle"
    assert next(store.library_dir.rglob("target/_items/th/middle/_entry.json")).is_file()

    deletion = store.delete_entry(middle["id"])
    assert deletion["entry_count"] == 1
    assert store.check_data()["entries"] == 2


def test_v2_review_preference_updates_only_its_folder_sidecar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store = LibraryStore(tmp_path / "data")
    target = store.create_folder("Target", "target", None)
    other = store.create_folder("Other", "other", None)
    store.create_entry(target["id"], "df", "Group", "group", "", "Body")
    store.create_entry(other["id"], "df", "Ring", "ring", "", "Body")
    target_sidecar = store.library_dir / "target" / "_folder.json"
    before = {
        path.relative_to(store.library_dir): path.read_bytes()
        for path in store.library_dir.rglob("*")
        if path.is_file()
    }

    def reject_generic_transaction() -> None:
        pytest.fail("a review-only update must not start a whole-library transaction")

    monkeypatch.setattr(store, "_begin_v2_transaction", reject_generic_transaction)
    updated = store.update_folder(target["id"], {"review_enabled": False})

    after = {
        path.relative_to(store.library_dir): path.read_bytes()
        for path in store.library_dir.rglob("*")
        if path.is_file()
    }
    assert set(after) == set(before)
    changed = {path for path in before if before[path] != after[path]}
    assert changed == {target_sidecar.relative_to(store.library_dir)}
    assert updated["review_enabled"] is False
    assert json.loads(target_sidecar.read_text())["review_enabled"] is False
    reopened = LibraryStore(store.data_dir)
    persisted = next(
        folder for folder in reopened.snapshot()["folders"] if folder["id"] == target["id"]
    )
    assert persisted["review_enabled"] is False


def test_v2_review_preference_preserves_a_current_search_index(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    store.create_entry(
        folder["id"], "df", "Group", "group", "", "unique-review-search-token"
    )
    assert store.search("unique-review-search-token")
    index = store._search_index
    before = store.search_index_stats()

    store.update_folder(folder["id"], {"review_enabled": False})

    assert store._search_index is index
    assert store.search("unique-review-search-token")
    assert store.search_index_stats() == before


def test_v2_cached_reads_detect_a_direct_entry_sidecar_edit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    store.create_entry(folder["id"], "df", "Old title", "group", "", "Body")
    store.snapshot()
    original_read = store._read_uncached
    uncached_reads = 0

    def count_uncached_read() -> dict:
        nonlocal uncached_reads
        uncached_reads += 1
        return original_read()

    monkeypatch.setattr(store, "_read_uncached", count_uncached_read)
    assert store.snapshot()["entries"][0]["title"] == "Old title"
    assert uncached_reads == 0

    sidecar = next(store.library_dir.rglob("group/_entry.json"))
    metadata = json.loads(sidecar.read_text())
    metadata["title"] = "Directly edited title"
    sidecar.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    assert store.snapshot()["entries"][0]["title"] == "Directly edited title"
    assert uncached_reads == 1


def test_v2_generic_write_does_not_cache_over_a_concurrent_direct_edit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "df", "Old title", "group", "", "Body")
    sidecar = next(store.library_dir.rglob("group/_entry.json"))
    original_apply = store._apply_v2_write

    def apply_then_edit(library: dict) -> None:
        original_apply(library)
        metadata = json.loads(sidecar.read_text())
        metadata["title"] = "Concurrent direct title"
        sidecar.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    monkeypatch.setattr(store, "_apply_v2_write", apply_then_edit)
    store.update_entry(entry["id"], {"title": "Application title"})

    assert store.snapshot()["entries"][0]["title"] == "Concurrent direct title"
    assert LibraryStore(store.data_dir).snapshot()["entries"][0]["title"] == (
        "Concurrent direct title"
    )


def test_v2_review_preference_does_not_cache_over_a_concurrent_sidecar_edit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Original folder", "original", None)
    sidecar = store.library_dir / "original" / "_folder.json"
    original_write = store._write_json_if_signature_matches

    def write_then_edit(
        path: Path,
        value: dict,
        expected_signature: tuple[int, int, int, int, int] | None,
    ) -> None:
        original_write(path, value, expected_signature)
        metadata = json.loads(sidecar.read_text())
        metadata["name"] = "Concurrent direct folder"
        metadata["review_enabled"] = True
        sidecar.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    monkeypatch.setattr(store, "_write_json_if_signature_matches", write_then_edit)
    updated = store.update_folder(folder["id"], {"review_enabled": False})

    current = store.snapshot()["folders"][0]
    assert updated["name"] == "Concurrent direct folder"
    assert updated["review_enabled"] is True
    assert current["name"] == "Concurrent direct folder"
    assert current["review_enabled"] is True
    assert LibraryStore(store.data_dir).snapshot()["folders"][0]["name"] == (
        "Concurrent direct folder"
    )


def test_v2_review_preference_does_not_overwrite_a_concurrent_target_edit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Original folder", "original", None)
    sidecar = store.library_dir / "original" / "_folder.json"
    original_write = store._write_json_if_signature_matches

    def edit_then_write(
        path: Path,
        value: dict,
        expected_signature: tuple[int, int, int, int, int] | None,
    ) -> None:
        metadata = json.loads(sidecar.read_text())
        metadata["name"] = "Concurrent direct folder"
        sidecar.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        original_write(path, value, expected_signature)

    monkeypatch.setattr(store, "_write_json_if_signature_matches", edit_then_write)
    with pytest.raises(
        StoreError, match="folder metadata changed before saving its review preference"
    ):
        store.update_folder(folder["id"], {"review_enabled": False})

    current = store.snapshot()["folders"][0]
    assert current["name"] == "Concurrent direct folder"
    assert current["review_enabled"] is True
    assert LibraryStore(store.data_dir).snapshot()["folders"][0] == current


def test_v2_assets_are_colocated_and_follow_entry_moves_and_deletion(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    source = store.create_folder("Source", "source", None)
    destination = store.create_folder("Destination", "destination", None)
    entry = store.create_entry(source["id"], "df", "Diagram", "diagram", "", "Body")
    image = _png_bytes()
    image_asset = _image_asset(image)
    excalidraw_id = "b" * 32
    excalidraw = {
        "type": "excalidraw",
        "version": 2,
        "elements": [],
    }
    commutative_id = "c" * 32
    commutative = {
        "version": 1,
        "name": "Commutative diagram",
        "width": 76,
        "nodes": [{"id": "a", "label": "$A$", "row": 0, "column": 0}],
        "arrows": [],
    }
    store.register_asset(entry["id"], image_asset, {"path": image})
    store.register_asset(
        entry["id"],
        {
            "id": excalidraw_id,
            "kind": "excalidraw",
            "source": f"diagrams/{excalidraw_id}.excalidraw",
            "path": image_asset["path"],
            "alt": "Drawing",
            "width": 76,
            "invert_lightness": True,
            "pixels": [4, 3],
        },
        {
            "path": image,
            "source": (json.dumps(excalidraw, indent=2) + "\n").encode(),
        },
    )
    store.register_asset(
        entry["id"],
        {
            "id": commutative_id,
            "kind": "commutative",
            "source": f"diagrams/{commutative_id}.commutative.json",
            "alt": "Commutative diagram",
            "width": 76,
        },
        {"source": (json.dumps(commutative, indent=2) + "\n").encode()},
    )

    entry_dir = next(store.library_dir.rglob("diagram/_entry.json")).parent
    sidecar = json.loads((entry_dir / "_entry.json").read_text())
    assert {
        asset.get("path") for asset in sidecar["assets"] if asset.get("path")
    } == {f"assets/{Path(image_asset['path']).name}"}
    assert {
        asset.get("source") for asset in sidecar["assets"] if asset.get("source")
    } == {
        f"assets/{excalidraw_id}.excalidraw",
        f"assets/{commutative_id}.commutative.json",
    }
    assert sorted(path.name for path in (entry_dir / "assets").iterdir()) == sorted(
        [
            Path(image_asset["path"]).name,
            f"{excalidraw_id}.excalidraw",
            f"{commutative_id}.commutative.json",
        ]
    )
    assert list(store.media_dir.iterdir()) == []
    assert list(store.diagram_dir.iterdir()) == []

    store.move_item("entry", entry["id"], destination["id"], 0)
    store.update_folder(destination["id"], {"slug": "target"})
    store.update_entry(entry["id"], {"kind": "rk", "tag": "moved-diagram"})
    moved_dir = store.library_dir / "target" / "_items" / "rk" / "moved-diagram"
    assert (moved_dir / "assets" / Path(image_asset["path"]).name).read_bytes() == image
    assert store.resolve_media_file(Path(image_asset["path"]).name).parent == (
        moved_dir / "assets"
    )
    assert store.resolve_excalidraw_file(f"{excalidraw_id}.excalidraw").parent == (
        moved_dir / "assets"
    )
    assert store.resolve_commutative_file(
        f"{commutative_id}.commutative.json"
    ).parent == (moved_dir / "assets")
    reopened = LibraryStore(store.data_dir)
    assert reopened.get_entry(entry["id"])["assets"][0]["path"] == image_asset["path"]

    deletion = reopened.delete_entry(entry["id"])
    assert deletion["deleted_file_count"] == 4
    assert not moved_dir.exists()
    assert reopened.resolve_media_file(Path(image_asset["path"]).name) is None


def test_v2_reads_and_preserves_explicit_legacy_global_asset_records(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Source", "source", None)
    entry = store.create_entry(folder["id"], "df", "Legacy", "legacy", "", "Body")
    image = _png_bytes()
    image_name = f"{'a' * 64}.png"
    excalidraw_id = "b" * 32
    commutative_id = "c" * 32
    store.media_dir.mkdir(parents=True, exist_ok=True)
    (store.media_dir / image_name).write_bytes(image)
    store.diagram_dir.mkdir(parents=True, exist_ok=True)
    (store.diagram_dir / f"{excalidraw_id}.excalidraw").write_text(
        json.dumps({"type": "excalidraw", "version": 2, "elements": []})
    )
    (store.diagram_dir / f"{commutative_id}.commutative.json").write_text(
        json.dumps(
            {
                "version": 1,
                "name": "Legacy commutative diagram",
                "width": 76,
                "nodes": [{"id": "a", "label": "$A$", "row": 0, "column": 0}],
                "arrows": [],
            }
        )
    )
    entry_dir = next(store.library_dir.rglob("legacy/_entry.json")).parent
    sidecar_path = entry_dir / "_entry.json"
    sidecar = json.loads(sidecar_path.read_text())
    sidecar["assets"] = [
        {
            "id": "legacy-image",
            "kind": "image",
            "path": f"media/{image_name}",
            "alt": "Legacy image",
            "width": 70,
            "invert_lightness": False,
            "pixels": [4, 3],
        },
        {
            "id": excalidraw_id,
            "kind": "excalidraw",
            "source": f"diagrams/{excalidraw_id}.excalidraw",
            "path": f"media/{image_name}",
            "alt": "Legacy drawing",
            "width": 76,
            "invert_lightness": True,
            "pixels": [4, 3],
        },
        {
            "id": commutative_id,
            "kind": "commutative",
            "source": f"diagrams/{commutative_id}.commutative.json",
            "alt": "Legacy commutative diagram",
            "width": 76,
        },
    ]
    sidecar_path.write_text(json.dumps(sidecar, indent=2) + "\n")

    reopened = LibraryStore(store.data_dir)
    assert reopened.resolve_media_file(image_name) == store.media_dir / image_name
    assert reopened.resolve_excalidraw_file(
        f"{excalidraw_id}.excalidraw"
    ) == store.diagram_dir / f"{excalidraw_id}.excalidraw"
    assert reopened.resolve_commutative_file(
        f"{commutative_id}.commutative.json"
    ) == store.diagram_dir / f"{commutative_id}.commutative.json"

    reopened.update_entry(entry["id"], {"title": "Still legacy"})
    rewritten = json.loads(sidecar_path.read_text())
    assert rewritten["assets"] == sidecar["assets"]
    assert not (entry_dir / "assets").exists()


def test_v2_asset_registration_rolls_back_without_a_live_orphan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    image = _png_bytes()
    asset = _image_asset(image)
    original_writer = store._write_json_if_changed

    def fail_asset_sidecar(path: Path, value: dict):
        if path.name == "_entry.json" and value.get("assets"):
            raise StoreError("injected asset sidecar failure")
        return original_writer(path, value)

    monkeypatch.setattr(store, "_write_json_if_changed", fail_asset_sidecar)
    with pytest.raises(StoreError, match="injected asset sidecar failure"):
        store.register_asset(entry["id"], asset, {"path": image})

    reopened = LibraryStore(store.data_dir)
    entry_dir = next(reopened.library_dir.rglob("group/_entry.json")).parent
    assert reopened.get_entry(entry["id"])["assets"] == []
    assert not (entry_dir / "assets").exists()
    assert not (store.runtime_dir / "library-write-journal.tmp").exists()


def test_v2_deletion_rejects_a_surviving_markdown_asset_reference_until_copied(
    tmp_path: Path,
):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Topology", "topology", None)
    owner = store.create_entry(folder["id"], "df", "Owner", "owner", "", "Owner")
    survivor = store.create_entry(
        folder["id"], "df", "Survivor", "survivor", "", "Survivor"
    )
    image = _png_bytes()
    asset = _image_asset(image)
    store.register_asset(owner["id"], asset, {"path": image})
    survivor_variant = survivor["formulations"][0]
    store.write_variant_content(
        survivor["id"],
        survivor_variant["id"],
        f"Keep ![shared](/media/{Path(asset['path']).name}).",
    )

    with pytest.raises(StoreError, match="surviving Markdown references"):
        store.delete_entry(owner["id"])
    assert store.get_entry(owner["id"])["id"] == owner["id"]

    store.register_asset(
        survivor["id"], _image_asset(image, "surviving-copy"), {"path": image}
    )
    owner_asset_path = store.resolve_media_file(Path(asset["path"]).name)
    assert owner_asset_path is not None
    store.delete_entry(owner["id"])
    surviving_path = store.resolve_media_file(Path(asset["path"]).name)
    assert surviving_path is not None and surviving_path != owner_asset_path
    assert surviving_path.read_bytes() == image


def test_v2_rejects_orphan_traversing_and_content_mismatched_assets(tmp_path: Path):
    mismatched = LibraryStore(tmp_path / "mismatched" / "data")
    folder = mismatched.create_folder("Algebra", "algebra", None)
    entry = mismatched.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    image = _png_bytes()
    bad_asset = _image_asset(image)
    bad_asset["path"] = f"media/{'a' * 64}.png"
    with pytest.raises(StoreError, match="content hash"):
        mismatched.register_asset(entry["id"], bad_asset, {"path": image})

    orphaned = LibraryStore(tmp_path / "orphaned" / "data")
    folder = orphaned.create_folder("Algebra", "algebra", None)
    entry = orphaned.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    asset = _image_asset(image)
    orphaned.register_asset(entry["id"], asset, {"path": image})
    entry_dir = next(orphaned.library_dir.rglob("group/_entry.json")).parent
    (entry_dir / "assets" / "orphan.txt").write_text("orphan")
    with pytest.raises(StoreError, match="unrecognized asset"):
        LibraryStore(orphaned.data_dir).snapshot()
    (entry_dir / "assets" / "orphan.txt").unlink()
    sidecar_path = entry_dir / "_entry.json"
    sidecar = json.loads(sidecar_path.read_text())
    sidecar["assets"][0]["path"] = "assets/../escape.png"
    sidecar_path.write_text(json.dumps(sidecar))
    with pytest.raises(StoreError, match="invalid colocated asset path"):
        LibraryStore(orphaned.data_dir).snapshot()


def test_v2_multi_path_write_rolls_back_after_metadata_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Old", "old", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    old_entry = store.library_dir / "old" / "_items" / "df" / "group" / "_entry.json"
    original_writer = store._write_json_if_changed

    def fail_new_folder(path: Path, value: dict):
        if path.name == "_folder.json" and path.parent.name == "new":
            raise StoreError("injected metadata write failure")
        return original_writer(path, value)

    monkeypatch.setattr(store, "_write_json_if_changed", fail_new_folder)
    with pytest.raises(StoreError, match="injected metadata"):
        store.update_folder(folder["id"], {"slug": "new"})

    reopened = LibraryStore(store.data_dir)
    assert old_entry.is_file()
    assert not (store.library_dir / "new").exists()
    assert reopened.get_entry(entry["id"])["canonical_tag"] == "old:df:group"


def test_v2_create_rolls_back_on_base_exception(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)

    def interrupt(_library: dict):
        raise KeyboardInterrupt

    monkeypatch.setattr(store, "_apply_v2_write", interrupt)
    with pytest.raises(KeyboardInterrupt):
        store.create_entry(folder["id"], "df", "Group", "group", "", "Body")

    reopened = LibraryStore(store.data_dir)
    assert reopened.check_data()["entries"] == 0
    assert not (store.runtime_dir / "library-write-journal.tmp").exists()


def test_v2_prepared_journal_recovers_an_interrupted_live_tree(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    with store.mutation_lock:
        store._begin_v2_transaction()
        (store.library_dir / "algebra" / "_folder.json").unlink()

    reopened = LibraryStore(store.data_dir)

    assert reopened.get_entry(entry["id"])["canonical_tag"] == "algebra:df:group"
    assert not (store.runtime_dir / "library-write-journal.tmp").exists()


def test_v2_recovery_preserves_direct_edits_from_displaced_live_tree(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Original")
    content_path = store.data_dir / entry["formulations"][0]["file"]
    with store.mutation_lock:
        store._begin_v2_transaction()
        content_path.write_text("Direct edit after interruption\n", encoding="utf-8")

    reopened = LibraryStore(store.data_dir)

    assert reopened.get_entry(entry["id"])["formulations"][0]["content"] == "Original\n"
    displaced = list(store.runtime_dir.glob("library-recovery-failed-*.tmp"))
    assert len(displaced) == 1
    preserved_bodies = [
        path.read_text(encoding="utf-8") for path in displaced[0].rglob("*.md")
    ]
    assert "Direct edit after interruption\n" in preserved_bodies


def test_committed_v2_write_does_not_report_cleanup_failure_as_write_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Old")
    variant_id = entry["formulations"][0]["id"]
    original_unlink = Path.unlink

    def fail_journal_cleanup(path: Path, *args, **kwargs):
        if path.name == "library-write-journal.tmp":
            raise OSError("injected journal cleanup failure")
        return original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fail_journal_cleanup)
    store.write_variant_content(entry["id"], variant_id, "Committed")

    monkeypatch.setattr(Path, "unlink", original_unlink)
    reopened = LibraryStore(store.data_dir)
    assert reopened.get_entry(entry["id"])["formulations"][0]["content"] == "Committed\n"
    assert not (store.runtime_dir / "library-write-journal.tmp").exists()


def test_v2_deep_path_escape_preserves_full_namespace_and_supports_moves(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    parent_id = None
    folders = []
    for index in range(64):
        initial = chr(ord("a") + index % 26)
        folder = store.create_folder(
            f"Level {index}", f"{initial}{'x' * 63}", parent_id
        )
        folders.append(folder)
        parent_id = folder["id"]
    entry = store.create_entry(parent_id, "df", "Deep", "deep", "", "Deep body")

    deep_metadata = list((store.library_dir / "_deep").glob("*/_folder.json"))
    assert deep_metadata
    reopened = LibraryStore(store.data_dir)
    assert reopened.get_entry(entry["id"])["canonical_tag"].endswith(":df:deep")

    store.move_item("folder", folders[-1]["id"], None, 0)
    moved = store.get_entry(entry["id"])
    assert moved["canonical_tag"] == f"{folders[-1]['slug']}:df:deep"
    assert (store.library_dir / folders[-1]["slug"] / "_folder.json").is_file()


def test_interprocess_lock_releases_thread_guard_after_base_exception(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store = LibraryStore(tmp_path / "data")
    original_acquire = store._lock._acquire_file

    def interrupt(_stream):
        raise KeyboardInterrupt

    monkeypatch.setattr(store._lock, "_acquire_file", interrupt)
    with pytest.raises(KeyboardInterrupt), store.mutation_lock:
        pass

    monkeypatch.setattr(store._lock, "_acquire_file", original_acquire)
    acquired: list[bool] = []

    def probe_guard():
        locked = store._lock._state.thread_lock.acquire(timeout=1)
        acquired.append(locked)
        if locked:
            store._lock._state.thread_lock.release()

    probe = threading.Thread(target=probe_guard)
    probe.start()
    probe.join(timeout=2)
    assert acquired == [True]


def test_store_rejects_symlinked_runtime_without_writing_outside_data(tmp_path: Path):
    data_dir = tmp_path / "data"
    outside = tmp_path / "outside"
    data_dir.mkdir()
    outside.mkdir()
    (data_dir / "runtime").symlink_to(outside, target_is_directory=True)

    with pytest.raises(StoreError, match="mutation lock"):
        LibraryStore(data_dir)

    assert not (outside / "library-lock.tmp").exists()


@pytest.mark.parametrize(
    "corruption",
    [
        "missing-root",
        "missing-markdown",
        "missing-folder-metadata",
        "missing-entry-metadata",
        "duplicate-id",
    ],
)
def test_v2_tree_corruption_is_rejected(tmp_path: Path, corruption: str):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    entry_dir = next(store.library_dir.rglob("group/_entry.json")).parent

    if corruption == "missing-root":
        shutil.rmtree(store.library_dir)
    elif corruption == "missing-markdown":
        next(entry_dir.glob("formulation.*.md")).unlink()
    elif corruption == "missing-folder-metadata":
        (store.library_dir / "algebra" / "_folder.json").unlink()
    elif corruption == "missing-entry-metadata":
        (entry_dir / "_entry.json").unlink()
    else:
        duplicate = entry_dir.parent / "duplicate"
        shutil.copytree(entry_dir, duplicate)

    with pytest.raises(StoreError):
        LibraryStore(store.data_dir).snapshot()
    assert entry["id"]


def test_v2_rejects_symlinks_in_the_authored_tree(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    target = store.library_dir / "algebra" / "unexpected"
    try:
        target.symlink_to(store.library_dir / "algebra", target_is_directory=True)
    except OSError:
        pytest.skip("symbolic links are unavailable")
    with pytest.raises(StoreError, match="Symbolic links|symbolic links"):
        LibraryStore(store.data_dir).snapshot()


def test_v2_direct_markdown_and_path_edits_refresh_search(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Analysis", "analysis", None)
    entry = store.create_entry(
        folder["id"], "df", "Continuity", "continuity", "", "old-body-token"
    )
    assert store.search("old-body-token")
    initial_builds = store.search_index_stats()["builds"]

    source = store.data_dir / store.get_entry(entry["id"])["formulations"][0]["file"]
    source.write_text("new-body-token\n", encoding="utf-8")
    old_dir = source.parent
    new_dir = old_dir.with_name("continuous-map")
    os.replace(old_dir, new_dir)
    time.sleep(SEARCH_STALENESS_SECONDS + 0.05)

    assert store.search("old-body-token") == []
    assert store.search("new-body-token")[0]["canonical_tag"] == "analysis:df:continuous-map"
    assert store.search_index_stats()["builds"] == initial_builds + 1


def test_v2_search_retries_when_sidecar_changes_during_index_build(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Analysis", "analysis", None)
    store.create_entry(folder["id"], "df", "Old unique title", "continuity", "", "Body")
    metadata_path = next(store.library_dir.rglob("continuity/_entry.json"))
    original_reader = store._read_indexed_content
    injected = False

    def edit_during_build(relative: str):
        nonlocal injected
        if not injected:
            injected = True
            metadata = json.loads(metadata_path.read_text())
            metadata["title"] = "New zebrafish title"
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        return original_reader(relative)

    monkeypatch.setattr(store, "_read_indexed_content", edit_during_build)

    assert store.search("zebrafish")[0]["title"] == "New zebrafish title"


def test_v2_entry_edit_has_a_local_git_diff(tmp_path: Path):
    root = tmp_path / "repository"
    root.mkdir()
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.name", "Study Tests")
    _git(root, "config", "user.email", "study-tests@example.invalid")
    store = LibraryStore(root / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    first = store.create_entry(folder["id"], "df", "First", "first", "", "First")
    second = store.create_entry(folder["id"], "df", "Second", "second", "", "Second")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "v2 library")

    store.update_entry(first["id"], {"title": "First changed"})
    changed = _git(root, "diff", "--name-only").splitlines()

    assert changed == ["data/library/algebra/_items/df/first/_entry.json"]
    assert second["id"]


def test_v2_asset_addition_has_only_an_entry_local_git_diff(tmp_path: Path):
    root = tmp_path / "repository"
    root.mkdir()
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.name", "Study Tests")
    _git(root, "config", "user.email", "study-tests@example.invalid")
    store = LibraryStore(root / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "v2 library")

    image = _png_bytes()
    asset = _image_asset(image)
    store.register_asset(entry["id"], asset, {"path": image})
    changed = _git(root, "status", "--short").splitlines()

    prefix = "data/library/algebra/_items/df/group/"
    assert [line.lstrip() for line in changed] == [
        f"M {prefix}_entry.json",
        f"?? {prefix}assets/",
    ]
    assert list(store.media_dir.iterdir()) == []


def test_candidate_pull_accepts_and_validates_a_v2_update(tmp_path: Path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    local = tmp_path / "local"
    local.mkdir()
    _git(local, "init", "-b", "main")
    _git(local, "config", "user.name", "Study Tests")
    _git(local, "config", "user.email", "study-tests@example.invalid")
    (local / ".gitignore").write_text("data/runtime/*.tmp\n", encoding="utf-8")
    local_store = LibraryStore(local / "data")
    folder = local_store.create_folder("Algebra", "algebra", None)
    entry = local_store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    _git(local, "add", ".")
    _git(local, "commit", "-m", "initial library")
    _git(local, "remote", "add", "origin", str(remote))
    _git(local, "push", "-u", "origin", "main")

    other = tmp_path / "other"
    subprocess.run(
        ["git", "clone", "--branch", "main", str(remote), str(other)],
        check=True,
        capture_output=True,
    )
    _git(other, "config", "user.name", "Study Tests")
    _git(other, "config", "user.email", "study-tests@example.invalid")
    other_store = LibraryStore(other / "data")
    other_entry = other_store.get_entry(entry["id"])
    other_store.write_variant_content(
        entry["id"], other_entry["formulations"][0]["id"], "Updated body"
    )
    _git(other, "add", "-A", "data")
    _git(other, "commit", "-m", "update body")
    _git(other, "push")

    def validate_candidate(candidate_data: Path) -> None:
        candidate = LibraryStore(candidate_data)
        assert candidate.check_data()["version"] == 2
        candidate.reload_search_index()

    repository = GitRepository(local, local / "data", local_store.mutation_lock)
    repository.pull_fast_forward(validate_candidate)

    reopened = LibraryStore(local / "data")
    assert reopened.format_version == 2
    assert reopened.get_entry(entry["id"])["formulations"][0]["content"] == "Updated body\n"
