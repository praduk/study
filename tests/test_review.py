from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import study_app.review as review_module
from study_app.review import ReviewEngine
from study_app.store import LibraryStore


def _entry(store: LibraryStore, folder_id: str, title: str, tag: str):
    return store.create_entry(folder_id, "df", title, tag, "", f"Definition of {title}")


def test_review_queue_preserves_authored_order_and_inherits_folder_exclusion(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    first_root = store.create_folder("First root", "first", None)
    child = store.create_folder("Child", "child", first_root["id"])
    second_root = store.create_folder("Second root", "second", None)
    first = _entry(store, first_root["id"], "First", "first")
    nested = _entry(store, child["id"], "Nested", "nested")
    second = _entry(store, second_root["id"], "Second", "second")
    review = ReviewEngine(store)

    assert [card["entry_id"] for card in review.queue()] == [
        first["id"],
        nested["id"],
        second["id"],
    ]

    store.update_folder(first_root["id"], {"review_enabled": False})
    assert [card["entry_id"] for card in review.queue()] == [second["id"]]


def test_statement_prompts_name_the_definition_axiom_or_theorem(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Foundations", "foundations", None)
    definition = store.create_entry(
        folder["id"], "df", "Set", "set", "", "A set is a collection."
    )
    axiom = store.create_entry(
        folder["id"], "ax", "Axiom of extensionality", "extensionality", "", "Axiom statement"
    )
    theorem = store.create_entry(
        folder["id"], "th", "Cantor's theorem", "cantor", "", "Theorem statement"
    )

    cards = {
        card["entry_id"]: card for card in ReviewEngine(store).queue()
    }

    assert cards[definition["id"]]["prompt"] == "Define Set."
    assert cards[axiom["id"]]["prompt"] == "State Axiom of extensionality."
    assert cards[theorem["id"]]["prompt"] == "State Cantor's theorem."
    assert all(card["prompt_body"] == "" for card in cards.values())


def test_theorem_and_problem_cards_reveal_only_the_matching_answer(tmp_path: Path):
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    theorem = store.create_entry(
        folder["id"], "th", "Orbit theorem", "orbit", "", "Main statement"
    )
    theorem = store.add_formulation(
        theorem["id"],
        {"label": "Equivalent", "subtag": "equivalent", "content": "Other statement"},
    )
    theorem = store.add_supplement(
        theorem["id"],
        {"kind": "pf", "label": "Main proof", "content": "Proof body", "main": True},
    )
    theorem = store.add_supplement(
        theorem["id"],
        {
            "kind": "pf",
            "label": "Alternate proof",
            "subtag": "alternate",
            "content": "Other proof",
            "main": False,
        },
    )
    problem = store.create_entry(
        folder["id"], "pb", "Compute an orbit", "compute-orbit", "", "Problem statement"
    )
    problem = store.add_supplement(
        problem["id"],
        {"kind": "sl", "label": "Solution", "content": "Solution body", "main": True},
    )
    review = ReviewEngine(store)

    cards = review.queue()
    assert [(card["entry_id"], card["mode"]) for card in cards] == [
        (theorem["id"], "statement"),
        (theorem["id"], "proof-plan"),
        (problem["id"], "solve"),
    ]
    assert cards[0]["prompt"] == "State Orbit theorem."
    assert cards[0]["prompt_body"] == ""
    assert cards[1]["prompt"] == "Prove Orbit theorem."
    assert cards[1]["prompt_body"] == "Main statement\n"
    assert cards[2]["prompt"] == "Solve the following problem."
    assert cards[2]["prompt_body"] == "Problem statement\n"
    statement = review.reveal(
        cards[0]["id"], {"attempt": "statement", "confidence": 2, "overt": True}
    )
    proof = review.reveal(
        cards[1]["id"], {"attempt": "proof", "confidence": 2, "overt": True}
    )
    solution = review.reveal(
        cards[2]["id"], {"attempt": "solution", "confidence": 2, "overt": True}
    )

    assert statement["answer"]["primary"]["content"] == "Main statement\n"
    assert [item["content"] for item in statement["answer"]["alternatives"]] == [
        "Other statement\n"
    ]
    assert proof["answer"]["primary"]["content"] == "Proof body\n"
    assert [item["content"] for item in proof["answer"]["alternatives"]] == [
        "Other proof\n"
    ]
    assert solution["answer"]["primary"]["content"] == "Solution body\n"
    assert solution["answer"]["alternatives"] == []


def test_legacy_review_modes_load_without_reentering_the_queue(tmp_path: Path):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "library.json").write_text(
        '{"version": 1, "folders": [], "entries": []}\n', encoding="utf-8"
    )
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    entry = _entry(store, folder["id"], "Group", "group")
    library = json.loads(store.library_path.read_text(encoding="utf-8"))
    library["entries"][0]["review_modes"] = ["transfer"]
    store.library_path.write_text(json.dumps(library), encoding="utf-8")

    cards = ReviewEngine(store).queue()
    assert [(card["entry_id"], card["mode"]) for card in cards] == [
        (entry["id"], "statement")
    ]


def test_again_is_due_in_ten_minutes_and_grade_recovery_does_not_duplicate_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    fixed = datetime(2026, 9, 4, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(review_module, "_now", lambda: fixed)
    store = LibraryStore(tmp_path / "data")
    folder = store.create_folder("Algebra", "algebra", None)
    _entry(store, folder["id"], "Group", "group")
    review = ReviewEngine(store)
    card = review.queue()[0]
    revealed = review.reveal(
        card["id"],
        {"attempt": "A set with an operation", "confidence": 3, "overt": True},
    )

    original_write = review._write
    failures = 0

    def fail_once(state):
        nonlocal failures
        failures += 1
        if failures == 1:
            raise OSError("simulated interrupted state write")
        original_write(state)

    monkeypatch.setattr(review, "_write", fail_once)
    with pytest.raises(OSError, match="interrupted"):
        review.grade(card["id"], revealed["attempt_id"], 0)

    recovered = review.grade(card["id"], revealed["attempt_id"], 0)
    assert datetime.fromisoformat(recovered["due_at"]) == fixed + timedelta(minutes=10)
    assert recovered["retry_in_session"] is True
    assert recovered["retry_after_items"] == 3
    records = [json.loads(line) for line in review.log_path.read_text().splitlines()]
    assert [record["id"] for record in records] == [revealed["attempt_id"]]
    assert review._read()["pending_attempts"] == {}
    assert review._read()["cards"][card["id"]]["lapses"] == 1

    # Lost HTTP responses are safe to retry after the state write as well.
    repeated = review.grade(card["id"], revealed["attempt_id"], 0)
    assert repeated["due_at"] == recovered["due_at"]
    assert len(review.log_path.read_text().splitlines()) == 1
