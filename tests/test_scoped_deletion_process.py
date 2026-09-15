from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from study_app.review import ReviewEngine
from study_app.store import LibraryStore


@pytest.mark.parametrize("crash_phase", ["prepared", "committed"])
def test_process_exit_obeys_durable_deletion_phase(tmp_path: Path, crash_phase: str):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    target = store.create_entry(folder["id"], "df", "Group", "group", "", "Group body")
    survivor = store.create_entry(folder["id"], "df", "Ring", "ring", "", "Ring body")
    review = ReviewEngine(store)
    card_id = review.card_id(target["id"], "statement")
    attempt = review.reveal(card_id, {
        "attempt": "Synthetic process test", "confidence": 2, "overt": True,
        "elapsed_ms": 1000,
    })
    review.grade(card_id, attempt["attempt_id"], 2)
    before_content = {
        path.relative_to(store.library_dir): path.read_bytes()
        for path in store.library_dir.rglob("*") if path.is_file()
    }
    before_review = (review.state_path.read_bytes(), review.log_path.read_bytes())
    entry_dir = (store.data_dir / target["formulations"][0]["file"]).parent
    code = """
import os
import sys
from pathlib import Path
from study_app.store import LibraryStore
from study_app.scoped_deletion import ScopedDeletions
store = LibraryStore(Path(sys.argv[1]))
entry_dir = Path(sys.argv[3])
crash_phase = sys.argv[4]
original_move = ScopedDeletions._move
def move_then_exit(self, source, destination, *args, **kwargs):
    result = original_move(self, source, destination, *args, **kwargs)
    if crash_phase == 'prepared' and Path(source) == entry_dir:
        os._exit(73)
    return result
ScopedDeletions._move = move_then_exit
original_write = ScopedDeletions._write
def write_then_exit(self, directory, value, state):
    result = original_write(self, directory, value, state)
    if crash_phase == 'committed' and state == 'committed':
        os._exit(73)
    return result
ScopedDeletions._write = write_then_exit
store.delete_entry(sys.argv[2])
raise AssertionError('the deletion never reached its detach operation')
"""
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    result = subprocess.run(
        [sys.executable, "-c", code, str(store.data_dir), target["id"], str(entry_dir), crash_phase],
        env=environment, capture_output=True, text=True, timeout=30, check=False,
    )
    assert result.returncode == 73, result.stderr
    assert not entry_dir.exists()

    reopened = LibraryStore(store.data_dir)
    restored_content = {
        path.relative_to(reopened.library_dir): path.read_bytes()
        for path in reopened.library_dir.rglob("*") if path.is_file()
    }
    if crash_phase == "prepared":
        assert restored_content == before_content
    else:
        assert not entry_dir.exists()
        assert all(value == before_content[path] for path, value in restored_content.items())
        assert list(reopened.pending_deletions().values()) == [[target["id"]]]
    reopened_review = ReviewEngine(reopened)
    reopened_review.prune_to_current_library()
    if crash_phase == "prepared":
        assert (review.state_path.read_bytes(), review.log_path.read_bytes()) == before_review
    else:
        assert target["id"] not in review.state_path.read_text()
        assert target["id"] not in review.log_path.read_text()
    assert reopened.get_entry(survivor["id"])["title"] == "Ring"
    assert not reopened.pending_deletions()
