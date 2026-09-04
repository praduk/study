from __future__ import annotations

import asyncio
import hashlib
import io
import json
import shutil
import subprocess
from pathlib import Path

import pytest
from PIL import Image
from pydantic import ValidationError

from study_app.export import build_export_html, export_pdf
from study_app.git_ops import GitError, GitRepository
from study_app.models import ReviewReveal
from study_app.store import LibraryStore, StoreError


def _git(directory: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(directory), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _initialize_repository(root: Path) -> None:
    root.mkdir()
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.name", "Study Tests")
    _git(root, "config", "user.email", "study-tests@example.invalid")


def test_content_paths_and_mathjax_macros_are_strictly_validated(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    with pytest.raises(StoreError, match="inside data/content"):
        store._safe_content_path("runtime/stolen.md")
    with pytest.raises(StoreError, match="inside data/content"):
        store._safe_content_path("content/../../outside.md")
    with pytest.raises(StoreError, match="argument count"):
        store.set_macros({"bad": ["#1", 12]})
    with pytest.raises(StoreError, match="optional default"):
        store.set_macros({"bad": ["#1", 1, 4]})
    assert store.set_macros({"pair": ["(#1,#2)", 2]})["macros"]["pair"] == ["(#1,#2)", 2]


def test_review_modes_require_kind_appropriate_answers(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    theorem = store.create_entry(folder["id"], "th", "A theorem", "result", "", "Statement")
    assert theorem["review_modes"] == ["statement"]
    with pytest.raises(StoreError, match="fixed for this content type"):
        store.update_entry(theorem["id"], {"review_modes": ["explain"]})
    with pytest.raises(StoreError, match="fixed for this content type"):
        store.update_entry(theorem["id"], {"review_modes": ["proof-plan"]})
    with pytest.raises(StoreError, match="cannot have a subtag"):
        store.add_supplement(
            theorem["id"],
            {"kind": "pf", "label": "Proof", "subtag": "tagged", "content": "", "main": True},
        )
    theorem = store.add_supplement(
        theorem["id"],
        {"kind": "pf", "label": "Proof", "subtag": None, "content": "Proof", "main": True},
    )
    assert "proof-plan" in theorem["review_modes"]
    store.update_entry(theorem["id"], {"review_modes": ["statement", "proof-plan"]})
    with pytest.raises(StoreError, match="reserved"):
        store.add_formulation(
            theorem["id"],
            {"label": "Collision", "subtag": "pf", "content": "Other", "main": False},
        )
    alternative = store.add_formulation(
        theorem["id"],
        {"label": "Other", "subtag": "other", "content": "Other", "main": False},
    )
    alternative_id = next(
        item["id"] for item in alternative["formulations"] if item.get("subtag") == "other"
    )
    with pytest.raises(StoreError, match="reserved"):
        store.update_variant(theorem["id"], alternative_id, {"subtag": "pf"})
    main_formulation = next(item for item in theorem["formulations"] if item["main"])
    with pytest.raises(StoreError, match="cannot have a subtag"):
        store.update_variant(
            theorem["id"], main_formulation["id"], {"subtag": "not-main-compatible"}
        )
    with pytest.raises(ValidationError):
        ReviewReveal.model_validate({"attempt": "answer", "overt": True})

    problem = store.create_entry(folder["id"], "pb", "A problem", "problem", "", "Prompt")
    assert problem["review_modes"] == []
    store.update_entry(problem["id"], {"review_modes": []})
    with pytest.raises(StoreError, match="fixed for this content type"):
        store.update_entry(problem["id"], {"review_modes": ["solve"]})
    problem = store.add_supplement(
        problem["id"],
        {"kind": "sl", "label": "Solution", "content": "Answer", "main": True},
    )
    assert problem["review_modes"] == ["solve"]
    with pytest.raises(StoreError, match="fixed for this content type"):
        store.update_entry(problem["id"], {"review_modes": []})

    definition = store.create_entry(folder["id"], "df", "Definition", "definition", "", "Main")
    assert definition["review_modes"] == ["statement"]
    with pytest.raises(StoreError, match="fixed for this content type"):
        store.create_entry(
            folder["id"],
            "df",
            "Another definition",
            "another-definition",
            "",
            "Main",
            ["transfer"],
        )
    with pytest.raises(StoreError, match="fixed for this content type"):
        store.create_entry(folder["id"], "df", "Invalid", "invalid", "", "Main", ["solve"])
    store.add_formulation(
        definition["id"],
        {"label": "Proof-like", "subtag": "pf", "content": "Other", "main": False},
    )
    with pytest.raises(StoreError, match="reserved"):
        store.update_entry(definition["id"], {"kind": "th"})


def test_moving_entry_rejects_destination_tag_collision(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    source = store.create_folder("Source", "source", None)
    destination = store.create_folder("Destination", "destination", None)
    moving = store.create_entry(source["id"], "df", "First", "same", "", "One")
    store.create_entry(destination["id"], "df", "Second", "same", "", "Two")

    with pytest.raises(StoreError, match="tag is already used"):
        store.move_item("entry", moving["id"], destination["id"], 0)

    unchanged = store.get_entry(moving["id"])
    assert unchanged["folder_id"] == source["id"]


def test_entry_creation_inserts_at_an_exact_direct_entry_position(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    first = store.create_entry(folder["id"], "df", "First", "first", "", "First")
    last = store.create_entry(folder["id"], "th", "Last", "last", "", "Last")

    middle = store.create_entry(
        folder["id"], "rk", "Middle", "middle", "", "Middle", index=1
    )
    beginning = store.create_entry(
        folder["id"], "ax", "Beginning", "beginning", "", "Beginning", index=0
    )
    clamped = store.create_entry(
        folder["id"], "pb", "Clamped", "clamped", "", "Clamped", index=100_000
    )

    entries = store.snapshot()["tree"][0]["entries"]
    assert [entry["id"] for entry in entries] == [
        beginning["id"],
        first["id"],
        middle["id"],
        last["id"],
        clamped["id"],
    ]
    assert [entry["order"] for entry in entries] == list(range(5))


def test_folder_creation_inserts_at_an_exact_sibling_position(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    first = store.create_folder("First", "first", None)
    last = store.create_folder("Last", "last", None)
    middle = store.create_folder("Middle", "middle", None, index=1)
    beginning = store.create_folder("Beginning", "beginning", None, index=0)
    clamped = store.create_folder("Clamped", "clamped", None, index=100_000)

    parent = store.create_folder("Parent", "parent", None)
    child_last = store.create_folder("Child last", "child-last", parent["id"])
    child_first = store.create_folder("Child first", "child-first", parent["id"], index=0)

    roots = store.snapshot()["tree"]
    assert [folder["id"] for folder in roots[:5]] == [
        beginning["id"],
        first["id"],
        middle["id"],
        last["id"],
        clamped["id"],
    ]
    assert [folder["order"] for folder in roots] == list(range(len(roots)))
    parent_node = next(folder for folder in roots if folder["id"] == parent["id"])
    assert [folder["id"] for folder in parent_node["children"]] == [
        child_first["id"],
        child_last["id"],
    ]


def test_folder_moves_keep_both_sibling_lists_contiguous(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    first = store.create_folder("First", "first", None)
    second = store.create_folder("Second", "second", None)
    third = store.create_folder("Third", "third", None)
    destination = store.create_folder("Destination", "destination", None)
    existing_child = store.create_folder("Existing", "existing", destination["id"])

    store.move_item("folder", first["id"], None, 3)
    assert [folder["id"] for folder in store.snapshot()["tree"]] == [
        second["id"], third["id"], first["id"], destination["id"],
    ]
    store.move_item("folder", first["id"], None, 0)
    store.move_item("folder", second["id"], destination["id"], 0)

    roots = store.snapshot()["tree"]
    assert [folder["id"] for folder in roots] == [
        first["id"], third["id"], destination["id"],
    ]
    assert [folder["order"] for folder in roots] == [0, 1, 2]
    destination_node = next(folder for folder in roots if folder["id"] == destination["id"])
    assert [folder["id"] for folder in destination_node["children"]] == [
        second["id"], existing_child["id"],
    ]
    assert [folder["order"] for folder in destination_node["children"]] == [0, 1]


def test_delete_entry_removes_owned_files_but_preserves_shared_assets_and_history(
    tmp_path: Path,
):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    before = store.create_entry(folder["id"], "df", "Before", "before", "", "Before")
    target = store.create_entry(folder["id"], "th", "Target", "target", "", "Target")
    after = store.create_entry(folder["id"], "df", "After", "after", "", "After")
    target = store.add_supplement(
        target["id"],
        {"kind": "pf", "label": "Proof", "content": "Proof", "main": True},
    )

    image = io.BytesIO()
    Image.new("RGB", (4, 3), "#638b7d").save(image, "PNG")
    image_bytes = image.getvalue()
    image_name = hashlib.sha256(image_bytes).hexdigest() + ".png"
    image_path = store.media_dir / image_name
    image_path.write_bytes(image_bytes)

    excalidraw_id = "b" * 32
    excalidraw_path = store.diagram_dir / f"{excalidraw_id}.excalidraw"
    excalidraw_path.write_text(
        json.dumps({"type": "excalidraw", "version": 2, "elements": []}),
        encoding="utf-8",
    )
    store.register_asset(
        target["id"],
        {
            "id": excalidraw_id,
            "kind": "excalidraw",
            "source": f"diagrams/{excalidraw_id}.excalidraw",
            "path": f"media/{image_name}",
            "alt": "Drawing",
            "width": 76,
            "invert_lightness": True,
            "pixels": [4, 3],
        },
    )
    store.register_asset(
        after["id"],
        {
            "id": "shared-image",
            "kind": "image",
            "path": f"media/{image_name}",
            "alt": "Shared image",
            "width": 70,
            "invert_lightness": False,
            "pixels": [4, 3],
        },
    )

    commutative_id = "c" * 32
    commutative_path = store.diagram_dir / f"{commutative_id}.commutative.json"
    commutative_path.write_text(
        json.dumps(
            {
                "version": 1,
                "name": "Referenced diagram",
                "width": 61,
                "nodes": [{"id": "a", "label": "$A$", "row": 0, "column": 0}],
                "arrows": [],
            }
        ),
        encoding="utf-8",
    )
    store.register_asset(
        target["id"],
        {
            "id": commutative_id,
            "kind": "commutative",
            "source": f"diagrams/{commutative_id}.commutative.json",
            "alt": "Referenced diagram",
            "width": 61,
        },
    )
    after_variant = after["formulations"][0]
    store.write_variant_content(
        after["id"],
        after_variant["id"],
        f"Keep [[commutative:{commutative_id}|width=61]].",
    )

    review_path = store.data_dir / "review.json"
    log_path = store.data_dir / "review-log.jsonl"
    review_path.write_text('{"version": 1, "cards": {"old": {}}}\n', encoding="utf-8")
    log_path.write_text('{"old": true}\n', encoding="utf-8")
    review_before = review_path.read_bytes()
    log_before = log_path.read_bytes()
    target_content_paths = [
        store.data_dir / variant["file"]
        for variant in (*target["formulations"], *target["supplements"])
    ]
    assert any(item["id"] == target["id"] for item in store.search("Target"))

    result = store.delete_entry(target["id"])

    assert result["entry_count"] == 1
    assert result["next_entry_id"] == after["id"]
    assert result["cleanup_pending_count"] == 0
    assert result["deleted_file_count"] == 3
    assert result["preserved_shared_file_count"] == 2
    assert not any(path.exists() for path in target_content_paths)
    assert not excalidraw_path.exists()
    assert image_path.exists()
    assert commutative_path.exists()
    remaining = store.snapshot()["tree"][0]["entries"]
    assert [entry["id"] for entry in remaining] == [before["id"], after["id"]]
    assert [entry["order"] for entry in remaining] == [0, 1]
    assert review_path.read_bytes() == review_before
    assert log_path.read_bytes() == log_before
    assert not any(item["id"] == target["id"] for item in store.search("Target"))
    with pytest.raises(StoreError, match="entry not found"):
        store.get_entry(target["id"])


def test_folder_delete_requires_explicit_recursive_confirmation_and_renumbers(
    tmp_path: Path,
):
    store = LibraryStore(tmp_path / "data")
    before = store.create_folder("Before", "before", None)
    target = store.create_folder("Target", "target", None)
    child = store.create_folder("Child", "child", target["id"])
    after = store.create_folder("After", "after", None)
    entry = store.create_entry(child["id"], "df", "Nested", "nested", "", "Nested")
    content_path = store.data_dir / entry["formulations"][0]["file"]

    with pytest.raises(StoreError, match="confirm recursive deletion"):
        store.delete_folder(target["id"])
    assert content_path.exists()
    assert store.get_entry(entry["id"])["title"] == "Nested"

    result = store.delete_folder(target["id"], recursive=True)

    assert result["folder_count"] == 2
    assert result["entry_count"] == 1
    assert result["next_folder_id"] == after["id"]
    assert result["deleted_file_count"] == 1
    assert not content_path.exists()
    roots = store.snapshot()["tree"]
    assert [folder["id"] for folder in roots] == [before["id"], after["id"]]
    assert [folder["order"] for folder in roots] == [0, 1]


def test_delete_empty_folder_uses_safe_default(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    parent = store.create_folder("Parent", "parent", None)
    empty = store.create_folder("Empty", "empty", parent["id"])

    result = store.delete_folder(empty["id"])

    assert result["folder_count"] == 1
    assert result["entry_count"] == 0
    assert result["next_folder_id"] == parent["id"]
    assert store.snapshot()["tree"][0]["children"] == []


def test_git_commit_is_limited_to_authored_data(tmp_path: Path):
    root = tmp_path / "repository"
    _initialize_repository(root)
    (root / "data" / "runtime").mkdir(parents=True)
    (root / "data" / "exports").mkdir()
    (root / "data" / "library.json").write_text("initial\n")
    (root / "data" / "runtime" / "README.md").write_text("initial\n")
    (root / "data" / "runtime" / "sessions.sqlite3").write_text("session\n")
    (root / "data" / "exports" / "output.pdf").write_text("initial\n")
    (root / "app.txt").write_text("initial\n")
    (root / ".gitignore").write_text(
        "data/runtime/sessions.sqlite3\ndata/runtime/sessions.sqlite3-*\n"
    )
    _git(root, "add", ".")
    _git(root, "commit", "-m", "initial")

    (root / "data" / "library.json").write_text("authored change\n")
    (root / "data" / "runtime" / "README.md").write_text("runtime documentation\n")
    (root / "data" / "runtime" / "sessions.sqlite3").write_text("session change\n")
    (root / "data" / "exports" / "output.pdf").write_text("generated change\n")
    (root / "app.txt").write_text("code change\n")
    _git(root, "add", "app.txt")

    repository = GitRepository(root, root / "data")
    status = repository.status()
    assert status["content_dirty"] is True
    assert {item["path"] for item in status["content_changed"]} == {
        "data/exports/output.pdf",
        "data/library.json",
        "data/runtime/README.md",
    }
    repository.commit_content("Update study material")

    assert set(_git(root, "show", "--format=", "--name-only", "HEAD").splitlines()) == {
        "data/exports/output.pdf",
        "data/library.json",
        "data/runtime/README.md",
    }
    assert _git(root, "diff", "--cached", "--name-only") == "app.txt"
    remaining = repository.status()
    assert remaining["dirty"] is True
    assert remaining["content_dirty"] is False


def test_git_commit_bypasses_hooks_to_enforce_content_scope(tmp_path: Path):
    root = tmp_path / "repository"
    _initialize_repository(root)
    (root / "data").mkdir()
    (root / "data" / "library.json").write_text("initial\n")
    (root / "app.txt").write_text("initial\n")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "initial")
    (root / "data" / "library.json").write_text("authored change\n")
    (root / "app.txt").write_text("staged code change\n")
    _git(root, "add", "app.txt")
    hook = root / ".git" / "hooks" / "pre-commit"
    marker = root / "hook-ran"
    hook.write_text(f"#!/bin/sh\ntouch '{marker}'\ngit add app.txt\nexit 1\n")
    hook.chmod(0o755)

    repository = GitRepository(root, root / "data")
    repository.commit_content("Update authored content")

    assert not marker.exists()
    assert _git(root, "show", "--format=", "--name-only", "HEAD") == "data/library.json"
    assert _git(root, "diff", "--cached", "--name-only") == "app.txt"
    assert not _git(root, "diff", "--", "data/library.json")


def test_git_commit_excludes_force_tracked_session_database(tmp_path: Path):
    root = tmp_path / "repository"
    _initialize_repository(root)
    (root / "data" / "runtime").mkdir(parents=True)
    (root / "data" / "library.json").write_text("initial\n")
    session_path = root / "data" / "runtime" / "sessions.sqlite3"
    session_path.write_text("old credential material\n")
    (root / ".gitignore").write_text("data/runtime/sessions.sqlite3\n")
    _git(root, "add", ".")
    _git(root, "add", "-f", "data/runtime/sessions.sqlite3")
    _git(root, "commit", "-m", "initial")

    (root / "data" / "library.json").write_text("authored change\n")
    session_path.write_text("live credential material\n")
    repository = GitRepository(root, root / "data")
    repository.commit_content("Update authored content")

    assert set(_git(root, "show", "--format=", "--name-only", "HEAD").splitlines()) == {
        "data/library.json",
        "data/runtime/sessions.sqlite3",
    }
    assert session_path.read_text() == "live credential material\n"
    assert not _git(root, "ls-files", "data/runtime/sessions.sqlite3")


def test_git_commit_refuses_runtime_path_type_collision(tmp_path: Path):
    root = tmp_path / "repository"
    _initialize_repository(root)
    runtime = root / "data" / "runtime"
    runtime.mkdir(parents=True)
    (root / "data" / "library.json").write_text("initial\n")
    (runtime / "README.md").write_text("runtime documentation\n")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "initial")
    before = _git(root, "rev-parse", "HEAD")

    shutil.rmtree(runtime)
    runtime.symlink_to("elsewhere")
    repository = GitRepository(root, root / "data")

    with pytest.raises(GitError, match="protected runtime path"):
        repository.commit_content("Unsafe runtime replacement")

    assert _git(root, "rev-parse", "HEAD") == before
    assert _git(root, "show", "HEAD:data/runtime/README.md") == "runtime documentation"


def test_git_commit_rolls_head_back_when_real_index_cannot_be_updated(tmp_path: Path):
    root = tmp_path / "repository"
    _initialize_repository(root)
    (root / "data").mkdir()
    (root / "data" / "library.json").write_text("initial\n")
    (root / "app.txt").write_text("initial\n")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "initial")
    before = _git(root, "rev-parse", "HEAD")
    (root / "data" / "library.json").write_text("authored change\n")
    (root / "app.txt").write_text("staged code change\n")
    _git(root, "add", "app.txt")
    index_lock = root / ".git" / "index.lock"
    index_lock.write_text("busy\n")

    repository = GitRepository(root, root / "data")
    try:
        with pytest.raises(GitError, match="HEAD was restored"):
            repository.commit_content("Update authored content")
    finally:
        index_lock.unlink()

    assert _git(root, "rev-parse", "HEAD") == before
    assert _git(root, "diff", "--cached", "--name-only") == "app.txt"
    assert _git(root, "diff", "--name-only", "--", "data/library.json")


def test_git_remote_display_redacts_credentials_and_query_values():
    assert GitRepository._display_remote(
        "https://token:secret@example.test/owner/study.git?access_token=also-secret"
    ) == "https://example.test/owner/study.git"
    assert GitRepository._display_remote("git@example.test:owner/study.git") == (
        "example.test:owner/study.git"
    )


def test_pull_is_fast_forward_only(tmp_path: Path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    local = tmp_path / "local"
    _initialize_repository(local)
    (local / "data").mkdir()
    (local / "data" / "library.json").write_text("one\n")
    _git(local, "add", ".")
    _git(local, "commit", "-m", "initial")
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
    (other / "data" / "library.json").write_text("two\n")
    _git(other, "commit", "-am", "remote update")
    _git(other, "push")

    repository = GitRepository(local, local / "data")
    repository.pull_fast_forward()
    assert (local / "data" / "library.json").read_text() == "two\n"

    (local / "local.txt").write_text("local\n")
    _git(local, "add", "local.txt")
    _git(local, "commit", "-m", "local commit")
    (other / "remote.txt").write_text("remote\n")
    _git(other, "add", "remote.txt")
    _git(other, "commit", "-m", "second remote update")
    _git(other, "push")
    before = _git(local, "rev-parse", "HEAD")
    with pytest.raises(GitError):
        repository.pull_fast_forward()
    assert _git(local, "rev-parse", "HEAD") == before


def test_pull_refuses_force_tracked_session_database(tmp_path: Path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    local = tmp_path / "local"
    _initialize_repository(local)
    (local / "data" / "runtime").mkdir(parents=True)
    (local / "data" / "library.json").write_text("one\n")
    (local / ".gitignore").write_text("data/runtime/sessions.sqlite3\n")
    _git(local, "add", ".")
    _git(local, "commit", "-m", "initial")
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
    session_path = other / "data" / "runtime" / "sessions.sqlite3"
    session_path.parent.mkdir(parents=True, exist_ok=True)
    session_path.write_text("remote credential material\n")
    _git(other, "add", "-f", "data/runtime/sessions.sqlite3")
    _git(other, "commit", "-m", "force-track a session database")
    _git(other, "push")

    local_session = local / "data" / "runtime" / "sessions.sqlite3"
    local_session.write_text("local credential material\n")
    before = _git(local, "rev-parse", "HEAD")
    repository = GitRepository(local, local / "data")
    with pytest.raises(GitError, match="protected session or transient"):
        repository.pull_fast_forward()

    assert _git(local, "rev-parse", "HEAD") == before
    assert local_session.read_text() == "local credential material\n"


def test_pull_refuses_when_current_tree_tracks_session_database(tmp_path: Path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    local = tmp_path / "local"
    _initialize_repository(local)
    (local / "data" / "runtime").mkdir(parents=True)
    session_path = local / "data" / "runtime" / "sessions.sqlite3"
    session_path.write_text("live credential material\n")
    (local / "data" / "library.json").write_text("one\n")
    (local / ".gitignore").write_text("data/runtime/sessions.sqlite3\n")
    _git(local, "add", ".")
    _git(local, "add", "-f", "data/runtime/sessions.sqlite3")
    _git(local, "commit", "-m", "initial")
    _git(local, "remote", "add", "origin", str(remote))
    _git(local, "push", "-u", "origin", "main")

    repository = GitRepository(local, local / "data")
    with pytest.raises(GitError, match="protected session or transient"):
        repository.pull_fast_forward()

    assert session_path.read_text() == "live credential material\n"


@pytest.mark.parametrize("collision", ["runtime-symlink", "session-directory"])
def test_pull_refuses_runtime_path_type_collisions(tmp_path: Path, collision: str):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    local = tmp_path / "local"
    _initialize_repository(local)
    runtime = local / "data" / "runtime"
    runtime.mkdir(parents=True)
    (runtime / "README.md").write_text("runtime documentation\n")
    (local / "data" / "library.json").write_text("one\n")
    (local / ".gitignore").write_text("data/runtime/sessions.sqlite3\n")
    _git(local, "add", ".")
    _git(local, "commit", "-m", "initial")
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
    other_runtime = other / "data" / "runtime"
    if collision == "runtime-symlink":
        shutil.rmtree(other_runtime)
        other_runtime.symlink_to("elsewhere")
        _git(other, "add", "-A", "data/runtime")
    else:
        (other_runtime / "sessions.sqlite3").mkdir()
        payload = other_runtime / "sessions.sqlite3" / "payload"
        payload.write_text("not a database\n")
        _git(other, "add", "-f", "data/runtime/sessions.sqlite3/payload")
    _git(other, "commit", "-m", "unsafe runtime path")
    _git(other, "push")

    local_session = runtime / "sessions.sqlite3"
    local_session.write_text("live credential material\n")
    before = _git(local, "rev-parse", "HEAD")
    repository = GitRepository(local, local / "data")
    with pytest.raises(GitError, match="protected session or transient"):
        repository.pull_fast_forward()

    assert _git(local, "rev-parse", "HEAD") == before
    assert local_session.read_text() == "live credential material\n"


def test_pull_validates_fetched_data_before_advancing_head(tmp_path: Path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    local = tmp_path / "local"
    _initialize_repository(local)
    (local / "data").mkdir()
    library_path = local / "data" / "library.json"
    library_path.write_text('{"folders": [], "entries": []}\n')
    _git(local, "add", ".")
    _git(local, "commit", "-m", "initial")
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
    (other / "data" / "library.json").write_text('{"broken": true}\n')
    _git(other, "commit", "-am", "invalid library")
    _git(other, "push")

    before = _git(local, "rev-parse", "HEAD")

    def validate_data(data_dir: Path) -> None:
        value = json.loads((data_dir / "library.json").read_text())
        if not isinstance(value.get("folders"), list) or not isinstance(
            value.get("entries"), list
        ):
            raise TypeError("library must contain folder and entry lists")

    repository = GitRepository(local, local / "data")
    with pytest.raises(GitError, match="upstream Study data is invalid"):
        repository.pull_fast_forward(validate_data)

    assert _git(local, "rev-parse", "HEAD") == before
    assert json.loads(library_path.read_text()) == {"folders": [], "entries": []}


def _export_fixture(store: LibraryStore) -> list[dict]:
    store.set_macros({"RR": "\\mathbb{R}"})
    folder = store.create_folder("Category theory", "category", None)
    entry = store.create_entry(folder["id"], "df", "A diagram", "diagram", "", "placeholder")
    diagram_id = "a" * 32
    diagram = {
        "version": 1,
        "name": "A commuting square",
        "width": 76,
        "nodes": [
            {"id": "a", "label": "$A$", "row": 0, "column": 0},
            {"id": "b", "label": "$B$", "row": 0, "column": 1},
        ],
        "arrows": [
            {"source": "a", "target": "b", "label": "$f$", "dashed": False, "double": False}
        ],
    }
    (store.diagram_dir / f"{diagram_id}.commutative.json").write_text(json.dumps(diagram))
    image = io.BytesIO()
    Image.new("RGB", (5, 4), "#b7d7f0").save(image, "PNG")
    image_bytes = image.getvalue()
    image_name = hashlib.sha256(image_bytes).hexdigest() + ".png"
    (store.media_dir / image_name).write_bytes(image_bytes)
    content = (
        f"Inline math $\\alpha + \\beta$, braces $\\{{x\\}}$, subscript $x_1$, "
        f"macro $\\RR$, and price \\$5.\n\n"
        f"$$\n\\begin{{aligned}}\na &= b \\\\\nc &= d\n\\end{{aligned}}\n$$\n\n"
        f"![A small image](/media/{image_name}#width=37&invert=lightness)\n\n"
        f"<!-- excalidraw:{'b' * 32}.excalidraw -->\n\n"
        f"[[commutative:{diagram_id}|width=61]]"
    )
    variant_id = entry["formulations"][0]["id"]
    store.write_variant_content(entry["id"], variant_id, content)
    return store.ordered_entries()


def test_export_embeds_image_width_and_renders_commutative_placeholders(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    entries = _export_fixture(store)
    document = build_export_html(store, entries, "Export test", True)
    assert "[[commutative:" not in document
    assert 'class="commutative" style="width:61%"' in document
    assert "$A$" in document and "$f$" in document
    assert 'src="data:image/png;base64,' in document
    assert 'style="width:37%"' in document
    assert "excalidraw:" not in document
    assert f"{'b' * 32}.excalidraw" not in document
    assert r"\(\{x\}\)" in document
    assert r"\(x_1\)" in document
    assert r"\(\RR\)" in document
    assert r"\begin{aligned}" in document
    assert r"b \\" + "\n" + "c &amp;= d" in document
    assert "price $5" in document
    assert r"\\mathbb{R}" in document


def test_export_keeps_diagram_tokens_and_markers_literal_inside_code(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    entries = _export_fixture(store)
    diagram_id = "a" * 32
    marker_id = "b" * 32
    token = f"[[commutative:{diagram_id}|width=61]]"
    coded = (
        f"Inline `{token}`.\n\n"
        f"```text\n{token}\n<!-- excalidraw:{marker_id}.excalidraw -->\n```\n\n"
        f"    {token}\n"
    )
    entries[0]["formulations"][0]["content"] = coded

    document = build_export_html(store, entries, "Code export", True)

    assert 'class="commutative"' not in document
    assert document.count(token) == 3
    assert f"excalidraw:{marker_id}.excalidraw" in document


def test_export_supports_slash_math_delimiters_without_changing_code(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    entries = _export_fixture(store)
    entries[0]["formulations"][0]["content"] = (
        "Inline \\(x_1 + \\RR\\).\n\n"
        "\\[y_2 = 3\\]\n\n"
        "`\\(inline_code\\)`\n\n"
        "```tex\n\\[fenced_code\\]\n```\n"
    )

    document = build_export_html(store, entries, "Slash math export", True)

    assert r"\(x_1 + \RR\)" in document
    assert r"\[y_2 = 3\]" in document
    assert r"<code>\(inline_code\)</code>" in document
    assert r"\[fenced_code\]" in document


def test_pdf_export_uses_only_vendored_mathjax(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    entries = _export_fixture(store)
    mathjax = Path(__file__).resolve().parents[1] / "frontend/public/vendor/mathjax/tex-svg.js"
    try:
        target = asyncio.run(export_pdf(store, entries, "Offline export", True, mathjax))
    except StoreError as exc:
        if "Executable doesn't exist" in str(exc):
            pytest.skip("Playwright Chromium is not installed")
        raise
    assert target.read_bytes().startswith(b"%PDF-")
    assert target.stat().st_size > 1000
