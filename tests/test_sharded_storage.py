from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from study_app.git_ops import GitRepository
from study_app.store import SEARCH_STALENESS_SECONDS, LibraryStore, StoreError


def _git(directory: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(directory), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _v1_store(data_dir: Path) -> LibraryStore:
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "library.json").write_text(
        '{"version": 1, "folders": [], "entries": []}\n', encoding="utf-8"
    )
    return LibraryStore(data_dir)


def _library_with_variants(root: Path) -> tuple[LibraryStore, dict, dict, dict]:
    store = _v1_store(root / "data")
    mathematics = store.create_folder("Mathematics", "math", None)
    algebra = store.create_folder("Algebra", "algebra", mathematics["id"])
    theorem = store.create_entry(
        algebra["id"], "th", "Orbit theorem", "orbit", "Assume a group action.", "Statement"
    )
    theorem = store.add_formulation(
        theorem["id"],
        {"label": "Action form", "subtag": "action", "content": "Alternative", "main": False},
    )
    theorem = store.add_supplement(
        theorem["id"],
        {"kind": "pf", "label": "Main proof", "content": "Proof", "main": True},
    )
    definition = store.create_entry(
        algebra["id"], "df", "Group", "group", "", "Definition", index=0
    )
    return store, mathematics, algebra, {"theorem": theorem, "definition": definition}


def test_fresh_data_root_initializes_directly_as_v2(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")

    assert json.loads(store.library_path.read_text()) == {"version": 2, "root": "library"}
    assert json.loads((store.library_dir / "_library.json").read_text()) == {"version": 1}
    assert not store.legacy_content_dir.exists()
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    assert store.get_entry(entry["id"])["formulations"][0]["content"] == "Body\n"


def test_v1_to_v2_migration_is_lossless_explicit_and_round_trips(tmp_path: Path):
    store, mathematics, algebra, values = _library_with_variants(tmp_path)
    theorem = values["theorem"]
    definition = values["definition"]
    review_path = store.data_dir / "review.json"
    review_path.write_text('{"version": 1, "cards": {}, "pending_attempts": {}}\n')
    review_before = review_path.read_bytes()

    result = store.migrate_to_v2()

    assert result == {"version": 2, "folders": 2, "entries": 2, "markdown_files": 4}
    assert json.loads(store.library_path.read_text()) == {"version": 2, "root": "library"}
    assert not store.legacy_content_dir.exists()
    assert review_path.read_bytes() == review_before
    assert store.check_data() == {
        "version": 2,
        "folders": 2,
        "entries": 2,
        "markdown_files": 4,
    }

    entry_dir = store.library_dir / "math" / "algebra" / "_items" / "th" / "orbit"
    assert json.loads((store.library_dir / "_library.json").read_text()) == {"version": 1}
    assert (store.library_dir / "math" / "_folder.json").is_file()
    assert (store.library_dir / "math" / "algebra" / "_folder.json").is_file()
    assert (entry_dir / "_entry.json").is_file()
    assert len(list(entry_dir.glob("formulation.*.md"))) == 2
    assert len(list(entry_dir.glob("proof.*.md"))) == 1

    reopened = LibraryStore(store.data_dir)
    migrated = reopened.get_entry(theorem["id"])
    assert migrated["folder_id"] == algebra["id"]
    assert migrated["canonical_tag"] == "math:algebra:th:orbit"
    assert [item["content"] for item in migrated["formulations"]] == [
        "Statement\n",
        "Alternative\n",
    ]
    assert migrated["supplements"][0]["content"] == "Proof\n"
    assert [entry["id"] for entry in reopened.snapshot()["tree"][0]["children"][0]["entries"]] == [
        definition["id"],
        theorem["id"],
    ]
    assert reopened.snapshot()["folders"][0]["id"] == mathematics["id"]
    with pytest.raises(StoreError, match="already uses version 2"):
        reopened.migrate_to_v2()


def test_empty_v2_library_has_a_tracked_root_sentinel(tmp_path: Path):
    store = _v1_store(tmp_path / "data")

    assert store.migrate_to_v2()["entries"] == 0
    assert (store.library_dir / "_library.json").is_file()
    assert LibraryStore(store.data_dir).check_data() == {
        "version": 2,
        "folders": 0,
        "entries": 0,
        "markdown_files": 0,
    }


def test_migration_preserves_effective_order_from_noncontiguous_v1_values(tmp_path: Path):
    store, _mathematics, algebra, values = _library_with_variants(tmp_path)
    library = json.loads(store.library_path.read_text())
    for entry in library["entries"]:
        entry["order"] = 20 if entry["id"] == values["theorem"]["id"] else 10
    store.library_path.write_text(json.dumps(library), encoding="utf-8")

    before = [entry["id"] for entry in store.snapshot()["tree"][0]["children"][0]["entries"]]
    store.migrate_to_v2()
    after = [entry["id"] for entry in store.snapshot()["tree"][0]["children"][0]["entries"]]

    assert before == after
    assert store.get_entry(values["theorem"]["id"])["folder_id"] == algebra["id"]


def test_migration_preserves_source_list_order_when_v1_order_values_tie(tmp_path: Path):
    store = _v1_store(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    zulu = store.create_entry(folder["id"], "df", "Zulu", "zulu", "", "Zulu")
    alpha = store.create_entry(folder["id"], "df", "Alpha", "alpha", "", "Alpha")
    library = json.loads(store.library_path.read_text())
    for entry in library["entries"]:
        entry["order"] = 0
    store.library_path.write_text(json.dumps(library), encoding="utf-8")

    before = [entry["id"] for entry in store.ordered_entries()]
    store.migrate_to_v2()
    after = [entry["id"] for entry in store.ordered_entries()]

    assert before == [zulu["id"], alpha["id"]]
    assert after == before


def test_v1_to_v2_migration_restores_v1_after_post_cutover_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store, _mathematics, _algebra, values = _library_with_variants(tmp_path)
    theorem_id = values["theorem"]["id"]
    original_library = store.library_path.read_bytes()
    original_content = {
        path.relative_to(store.data_dir): path.read_bytes()
        for path in store.legacy_content_dir.rglob("*.md")
    }
    original_read = store._read
    read_count = 0

    def fail_after_cutover():
        nonlocal read_count
        read_count += 1
        if read_count == 3:
            raise StoreError("injected post-cutover validation failure")
        return original_read()

    monkeypatch.setattr(store, "_read", fail_after_cutover)
    with pytest.raises(StoreError, match="injected post-cutover"):
        store.migrate_to_v2()

    monkeypatch.setattr(store, "_read", original_read)
    assert store.library_path.read_bytes() == original_library
    assert not store.library_dir.exists()
    assert {
        path.relative_to(store.data_dir): path.read_bytes()
        for path in store.legacy_content_dir.rglob("*.md")
    } == original_content
    assert store.get_entry(theorem_id)["id"] == theorem_id


@pytest.mark.parametrize("interrupted_source", ["library", "content"])
def test_migration_recovers_when_rename_completes_before_base_exception(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    interrupted_source: str,
):
    store, _mathematics, _algebra, values = _library_with_variants(tmp_path)
    theorem_id = values["theorem"]["id"]
    original_library = store.library_path.read_bytes()
    original_content = {
        path.relative_to(store.data_dir): path.read_bytes()
        for path in store.legacy_content_dir.rglob("*.md")
    }
    selected = (
        store.library_path
        if interrupted_source == "library"
        else store.legacy_content_dir
    )
    original_replace = os.replace
    interrupted = False

    def interrupt_after_replace(source, destination):
        nonlocal interrupted
        original_replace(source, destination)
        if not interrupted and Path(source) == selected:
            interrupted = True
            raise KeyboardInterrupt

    monkeypatch.setattr(os, "replace", interrupt_after_replace)
    with pytest.raises(KeyboardInterrupt):
        store.migrate_to_v2()

    monkeypatch.setattr(os, "replace", original_replace)
    assert interrupted
    assert store.library_path.read_bytes() == original_library
    assert {
        path.relative_to(store.data_dir): path.read_bytes()
        for path in store.legacy_content_dir.rglob("*.md")
    } == original_content
    reopened = LibraryStore(store.data_dir)
    assert reopened.format_version == 1
    assert reopened.get_entry(theorem_id)["id"] == theorem_id


def test_migration_never_removes_an_independently_created_v2_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store, _mathematics, _algebra, _values = _library_with_variants(tmp_path)
    original_builder = store._build_v2_tree

    def create_competing_target(library: dict, destination: Path):
        original_builder(library, destination)
        store.library_dir.mkdir()
        (store.library_dir / "external.txt").write_text("external", encoding="utf-8")

    monkeypatch.setattr(store, "_build_v2_tree", create_competing_target)
    with pytest.raises(StoreError, match="storage migration failed"):
        store.migrate_to_v2()

    assert (store.library_dir / "external.txt").read_text(encoding="utf-8") == "external"
    assert store.format_version == 1


def test_migration_refuses_unknown_metadata_and_unreferenced_content(tmp_path: Path):
    unknown_store = _v1_store(tmp_path / "unknown" / "data")
    unknown_library = json.loads(unknown_store.library_path.read_text())
    unknown_library["owner_note"] = "must not be discarded"
    unknown_store.library_path.write_text(json.dumps(unknown_library), encoding="utf-8")
    with pytest.raises(StoreError, match="unknown field: owner_note"):
        unknown_store.migrate_to_v2()

    orphan_store = _v1_store(tmp_path / "orphan" / "data")
    orphan = orphan_store.legacy_content_dir / "orphan" / "notes.md"
    orphan.parent.mkdir()
    orphan.write_text("must not be discarded", encoding="utf-8")
    with pytest.raises(StoreError, match="unreferenced"):
        orphan_store.migrate_to_v2()
    assert orphan.read_text(encoding="utf-8") == "must not be discarded"


def test_migration_freezes_and_restores_a_file_added_during_staging(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store, _mathematics, _algebra, _values = _library_with_variants(tmp_path)
    original_builder = store._build_v2_tree
    late = store.legacy_content_dir / "late.md"

    def add_late_file(library: dict, destination: Path):
        original_builder(library, destination)
        late.write_text("must survive", encoding="utf-8")

    monkeypatch.setattr(store, "_build_v2_tree", add_late_file)
    with pytest.raises(StoreError, match="unreferenced"):
        store.migrate_to_v2()

    assert store.format_version == 1
    assert late.read_text(encoding="utf-8") == "must survive"
    assert not store.library_dir.exists()


def test_startup_recovers_v1_after_process_exit_during_migration_cutover(tmp_path: Path):
    store, _mathematics, _algebra, values = _library_with_variants(tmp_path)
    theorem_id = values["theorem"]["id"]
    script = """
import os
import sys
from pathlib import Path

from study_app.store import LibraryStore

store = LibraryStore(Path(sys.argv[1]))
original_replace = os.replace

def crash_after_content_freeze(source, destination):
    original_replace(source, destination)
    if Path(source) == store.legacy_content_dir and Path(destination).name == "content":
        os._exit(79)

os.replace = crash_after_content_freeze
store.migrate_to_v2()
"""

    crashed = subprocess.run(
        [sys.executable, "-c", script, str(store.data_dir)],
        cwd=Path(__file__).parents[1],
        check=False,
    )

    assert crashed.returncode == 79
    recovered = LibraryStore(store.data_dir)
    assert recovered.format_version == 1
    assert recovered.get_entry(theorem_id)["id"] == theorem_id
    assert not (store.runtime_dir / "library-migration-journal.tmp").exists()


def test_migration_fails_closed_when_legacy_tree_cannot_be_scanned(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store, _mathematics, _algebra, _values = _library_with_variants(tmp_path)
    original_scandir = os.scandir
    failed = False

    def fail_once(path):
        nonlocal failed
        if not failed and Path(path) == store.legacy_content_dir:
            failed = True
            raise PermissionError("injected scan failure")
        return original_scandir(path)

    monkeypatch.setattr(os, "scandir", fail_once)
    with pytest.raises(StoreError, match="inspect all legacy content"):
        store.migrate_to_v2()

    assert store.format_version == 1


def test_migration_fails_closed_when_staged_tree_cannot_be_synced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store, _mathematics, _algebra, values = _library_with_variants(tmp_path)
    original_scandir = os.scandir
    failed = False

    def fail_staging_scan(path):
        nonlocal failed
        if isinstance(path, int):
            return original_scandir(path)
        candidate = Path(path)
        if not failed and candidate.name.startswith("library-migration-"):
            failed = True
            raise PermissionError("injected staging scan failure")
        return original_scandir(path)

    monkeypatch.setattr(os, "scandir", fail_staging_scan)
    with pytest.raises(StoreError, match="storage migration failed"):
        store.migrate_to_v2()

    assert failed
    assert store.format_version == 1
    assert store.get_entry(values["theorem"]["id"])["id"] == values["theorem"]["id"]


def test_data_check_and_migration_reject_non_utf8_markdown(tmp_path: Path):
    store, _mathematics, _algebra, values = _library_with_variants(tmp_path)
    entry = store.get_entry(values["theorem"]["id"])
    source = store.data_dir / entry["formulations"][0]["file"]
    source.write_bytes(b"\xff\xfe")

    with pytest.raises(StoreError, match="unreadable"):
        store.check_data()
    with pytest.raises(StoreError, match="UTF-8"):
        store.migrate_to_v2()


def test_v2_crud_moves_paths_but_preserves_stable_ids_and_sparse_peer_metadata(tmp_path: Path):
    store = _v1_store(tmp_path / "data")
    source = store.create_folder("Source", "source", None)
    destination = store.create_folder("Destination", "destination", None)
    first = store.create_entry(source["id"], "df", "First", "first", "", "First")
    last = store.create_entry(source["id"], "df", "Last", "last", "", "Last")
    store.migrate_to_v2()

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


def test_v2_multi_path_write_rolls_back_after_metadata_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    store = _v1_store(tmp_path / "data")
    folder = store.create_folder("Old", "old", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    store.migrate_to_v2()
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


def test_migration_serializes_a_second_store_writer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    migrating, _mathematics, _algebra, values = _library_with_variants(tmp_path)
    writer = LibraryStore(migrating.data_dir)
    entered_build = threading.Event()
    release_build = threading.Event()
    original_builder = migrating._build_v2_tree

    def paused_builder(library: dict, destination: Path):
        entered_build.set()
        assert release_build.wait(timeout=5)
        return original_builder(library, destination)

    monkeypatch.setattr(migrating, "_build_v2_tree", paused_builder)
    def write():
        entry = writer.get_entry(values["theorem"]["id"])
        writer.write_variant_content(
            entry["id"], entry["formulations"][0]["id"], "new-from-writer"
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        migration_future = executor.submit(migrating.migrate_to_v2)
        assert entered_build.wait(timeout=5)
        writer_future = executor.submit(write)
        time.sleep(0.05)
        assert not writer_future.done()
        release_build.set()
        migration_future.result(timeout=5)
        writer_future.result(timeout=5)

    assert LibraryStore(migrating.data_dir).get_entry(values["theorem"]["id"])[
        "formulations"
    ][0]["content"] == "new-from-writer\n"


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
    store = _v1_store(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    entry = store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    store.migrate_to_v2()
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
    store = _v1_store(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    store.migrate_to_v2()
    target = store.library_dir / "algebra" / "unexpected"
    try:
        target.symlink_to(store.library_dir / "algebra", target_is_directory=True)
    except OSError:
        pytest.skip("symbolic links are unavailable")
    with pytest.raises(StoreError, match="Symbolic links|symbolic links"):
        LibraryStore(store.data_dir).snapshot()


def test_v2_direct_markdown_and_path_edits_refresh_search(tmp_path: Path):
    store = _v1_store(tmp_path / "data")
    folder = store.create_folder("Analysis", "analysis", None)
    entry = store.create_entry(
        folder["id"], "df", "Continuity", "continuity", "", "old-body-token"
    )
    store.migrate_to_v2()
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
    store = _v1_store(tmp_path / "data")
    folder = store.create_folder("Analysis", "analysis", None)
    store.create_entry(folder["id"], "df", "Old unique title", "continuity", "", "Body")
    store.migrate_to_v2()
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
    store = _v1_store(root / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    first = store.create_entry(folder["id"], "df", "First", "first", "", "First")
    second = store.create_entry(folder["id"], "df", "Second", "second", "", "Second")
    store.migrate_to_v2()
    _git(root, "add", ".")
    _git(root, "commit", "-m", "v2 library")

    store.update_entry(first["id"], {"title": "First changed"})
    changed = _git(root, "diff", "--name-only").splitlines()

    assert changed == ["data/library/algebra/_items/df/first/_entry.json"]
    assert second["id"]


def test_candidate_pull_accepts_and_validates_a_v2_transition(tmp_path: Path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    local = tmp_path / "local"
    local.mkdir()
    _git(local, "init", "-b", "main")
    _git(local, "config", "user.name", "Study Tests")
    _git(local, "config", "user.email", "study-tests@example.invalid")
    (local / ".gitignore").write_text("data/runtime/*.tmp\n", encoding="utf-8")
    local_store = _v1_store(local / "data")
    folder = local_store.create_folder("Algebra", "algebra", None)
    entry = local_store.create_entry(folder["id"], "df", "Group", "group", "", "Body")
    _git(local, "add", ".")
    _git(local, "commit", "-m", "version 1")
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
    LibraryStore(other / "data").migrate_to_v2()
    _git(other, "add", "-A", "data")
    _git(other, "commit", "-m", "version 2")
    _git(other, "push")

    def validate_candidate(candidate_data: Path) -> None:
        candidate = LibraryStore(candidate_data)
        assert candidate.check_data()["version"] == 2
        candidate.reload_search_index()

    repository = GitRepository(local, local / "data", local_store.mutation_lock)
    repository.pull_fast_forward(validate_candidate)

    reopened = LibraryStore(local / "data")
    assert reopened.format_version == 2
    assert reopened.get_entry(entry["id"])["formulations"][0]["content"] == "Body\n"
