from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .store import LibraryStore, StoreError

MODE_LABELS = {
    "statement": "Statement",
    "example": "Example and near-miss",
    "discriminate": "Concept discrimination",
    "explain": "Explain the idea",
    "proof-plan": "Proof of theorem",
    "solve": "Solve problem",
    "transfer": "Transfer",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


class ReviewEngine:
    """A conservative adaptive scheduler; spacing is evidence-based, exact constants are not."""

    def __init__(self, store: LibraryStore):
        self.store = store
        self.state_path = store.data_dir / "review.json"
        self.log_path = store.data_dir / "review-log.jsonl"
        self._lock = store.mutation_lock
        if self.state_path.is_symlink() or self.log_path.is_symlink():
            raise StoreError("review-state files cannot be symbolic links")
        if not self.state_path.exists():
            _atomic_json(self.state_path, {"version": 1, "cards": {}, "pending_attempts": {}})

    def _read(self) -> dict[str, Any]:
        try:
            with self.state_path.open(encoding="utf-8") as stream:
                result = json.load(stream)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise StoreError("review.json is unreadable or invalid") from exc
        if not isinstance(result, dict) or result.get("version") != 1:
            raise StoreError("unsupported review-state version")
        result.setdefault("cards", {})
        result.setdefault("pending_attempts", {})
        return result

    def _write(self, state: dict[str, Any]) -> None:
        state["updated_at"] = _now().isoformat()
        _atomic_json(self.state_path, state)

    def _logged_attempt(self, attempt_id: str) -> dict[str, Any] | None:
        """Return a durable grade record, if one exists, for idempotent recovery."""
        if not self.log_path.exists():
            return None
        try:
            with self.log_path.open(encoding="utf-8") as stream:
                for line in stream:
                    if not line.strip():
                        continue
                    record = json.loads(line)
                    if record.get("id") == attempt_id:
                        return record
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise StoreError("review-log.jsonl is unreadable or invalid") from exc
        return None

    def _append_log(self, record: dict[str, Any]) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())

    @staticmethod
    def _grade_response(card_state: dict[str, Any], grade: int) -> dict[str, Any]:
        return {
            **card_state,
            "retry_in_session": grade == 0,
            "retry_after_items": 3 if grade == 0 else None,
            "note": "Spacing is supported by evidence; these adaptive constants are a transparent product heuristic, not a scientifically optimal formula.",
        }

    @staticmethod
    def card_id(entry_id: str, mode: str) -> str:
        return f"{entry_id}::{mode}"

    @staticmethod
    def split_card_id(card_id: str) -> tuple[str, str]:
        try:
            entry_id, mode = card_id.rsplit("::", 1)
        except ValueError as exc:
            raise StoreError("invalid review card") from exc
        if mode not in MODE_LABELS:
            raise StoreError("invalid review mode")
        return entry_id, mode

    def _prompt(self, entry: dict[str, Any], mode: str) -> dict[str, Any]:
        title = entry["title"]
        prompts = {
            "statement": f"State {title} precisely from memory. Include every hypothesis and conclusion.",
            "example": f"Give an example of {title} and a near-miss. Explain the decisive difference.",
            "discriminate": f"State {title}, then give an example and a nonexample with justification.",
            "explain": f"Explain {title} in your own words. Why does it matter, and what would fail without it?",
            "proof-plan": f"Prove {title} from memory. Give the complete argument and justify every major step.",
            "solve": f"Solve {title} without looking at the stored solution. Show the strategy and work.",
            "transfer": f"Give a genuinely new application of {title}, or explain how it changes when one assumption is removed.",
        }
        prompt_body = ""
        if mode in {"solve", "proof-plan"}:
            main = next(
                (item for item in entry["formulations"] if item.get("main")),
                entry["formulations"][0],
            )
            prompt_body = main.get("content", "")
        return {
            "id": self.card_id(entry["id"], mode),
            "entry_id": entry["id"],
            "folder_id": entry["folder_id"],
            "mode": mode,
            "mode_label": MODE_LABELS[mode],
            "title": title,
            "kind": entry["kind"],
            "canonical_tag": entry["canonical_tag"],
            "header": entry.get("header", ""),
            "prompt": prompts[mode],
            "prompt_body": prompt_body,
        }

    def queue(self, include_not_due: bool = False, limit: int = 100) -> list[dict[str, Any]]:
        now = _now()
        with self._lock:
            state = self._read()
            queue: list[dict[str, Any]] = []
            for entry in self.store.ordered_entries(review_only=True):
                for mode in entry.get("review_modes") or self.store.default_review_modes(
                    entry["kind"]
                ):
                    if not self.store.review_mode_available(entry, mode):
                        continue
                    card_id = self.card_id(entry["id"], mode)
                    card_state = state["cards"].get(card_id, {})
                    due_text = card_state.get("due_at")
                    due = datetime.fromisoformat(due_text) if due_text else None
                    if include_not_due or due is None or due <= now:
                        prompt = self._prompt(entry, mode)
                        prompt["due_at"] = due_text
                        prompt["new"] = due is None
                        prompt["repetitions"] = int(card_state.get("repetitions", 0))
                        queue.append(prompt)
                        if len(queue) >= limit:
                            return queue
            return queue

    def stats(self) -> dict[str, Any]:
        due = self.queue(limit=10000)
        with self._lock:
            state = self._read()
            today = _now().date().isoformat()
            completed_today = sum(
                1
                for card in state["cards"].values()
                if str(card.get("last_reviewed_at", "")).startswith(today)
            )
            minutes = round(
                sum(
                    int(card.get("last_elapsed_ms", 0))
                    for card in state["cards"].values()
                    if str(card.get("last_reviewed_at", "")).startswith(today)
                )
                / 60_000
            )
        return {"due": len(due), "completed_today": completed_today, "minutes_today": minutes}

    def reveal(self, card_id: str, attempt: dict[str, Any]) -> dict[str, Any]:
        entry_id, mode = self.split_card_id(card_id)
        entry = self.store.get_entry(entry_id)
        if mode not in entry.get("review_modes", []) or not self.store.review_mode_available(
            entry, mode
        ):
            raise StoreError("this review mode is not enabled for the entry")
        attempt_id = uuid.uuid4().hex
        created = {
            "id": attempt_id,
            "card_id": card_id,
            "entry_id": entry_id,
            "mode": mode,
            "started_at": _now().isoformat(),
            **attempt,
        }
        with self._lock:
            state = self._read()
            state["pending_attempts"][attempt_id] = created
            self._write(state)
        if mode == "statement":
            answer_variants = entry["formulations"]
        else:
            supplement_kind = "pf" if mode == "proof-plan" else "sl"
            answer_variants = [
                item
                for item in entry.get("supplements", [])
                if item.get("kind") == supplement_kind
            ]
        main = next(
            (item for item in answer_variants if item.get("main")), answer_variants[0]
        )
        answer = {
            "primary": main,
            "alternatives": [item for item in answer_variants if item["id"] != main["id"]],
        }
        if mode == "statement":
            feedback_cues = [
                "Compare each hypothesis, conclusion, and logical dependency—not just the wording.",
                "If something was missing, name the precise gap before grading.",
            ]
        else:
            feedback_cues = [
                "Check the strategy choice and justification for every major step, not only the result.",
                "If the argument has a gap, identify the first unsupported step before grading.",
            ]
        return {"attempt_id": attempt_id, "answer": answer, "feedback_cues": feedback_cues}

    def grade(self, card_id: str, attempt_id: str, grade: int) -> dict[str, Any]:
        self.split_card_id(card_id)
        now = _now()
        with self._lock:
            state = self._read()
            pending = state["pending_attempts"].get(attempt_id)
            logged = self._logged_attempt(attempt_id)
            if logged is not None:
                if logged.get("card_id") != card_id or logged.get("grade") != grade:
                    raise StoreError("review attempt was already graded differently")
                schedule = logged.get("schedule")
                if not isinstance(schedule, dict):
                    raise StoreError("review log contains an invalid schedule")
                if pending is not None:
                    state["cards"][card_id] = schedule
                    state["pending_attempts"].pop(attempt_id, None)
                    self._write(state)
                return self._grade_response(schedule, grade)
            if pending is None or pending["card_id"] != card_id:
                raise StoreError("review attempt is missing, expired, or belongs to another card")
            previous = state["cards"].get(card_id, {})
            old_stability = float(previous.get("stability_days", 0.5))
            old_difficulty = float(previous.get("difficulty", 5.0))
            repetitions = int(previous.get("repetitions", 0))
            lapses = int(previous.get("lapses", 0))

            if grade == 0:
                stability = max(0.25, old_stability * 0.45)
                difficulty = min(10.0, old_difficulty + 0.7)
                due = now + timedelta(minutes=10)
                lapses += 1
            elif grade == 1:
                stability = max(1.0, old_stability * 1.35)
                difficulty = min(10.0, old_difficulty + 0.2)
                due = now + timedelta(days=max(1, round(stability)))
                repetitions += 1
            elif grade == 2:
                stability = max(2.0, old_stability * (2.25 - old_difficulty * 0.035))
                difficulty = max(1.0, old_difficulty - 0.15)
                due = now + timedelta(days=max(1, round(stability)))
                repetitions += 1
            else:
                stability = max(4.0, old_stability * (3.1 - old_difficulty * 0.045))
                difficulty = max(1.0, old_difficulty - 0.35)
                due = now + timedelta(days=max(2, round(stability)))
                repetitions += 1

            confidence = pending.get("confidence")
            calibration = None
            if confidence is not None:
                expected = 1 if grade == 0 else 2 if grade < 3 else 3
                calibration = int(confidence) - expected
                if grade == 0 and confidence == 3:
                    difficulty = min(10.0, difficulty + 0.35)

            card_state = {
                "due_at": due.isoformat(),
                "last_reviewed_at": now.isoformat(),
                "last_grade": grade,
                "last_elapsed_ms": int(pending.get("elapsed_ms", 0)),
                "stability_days": round(stability, 3),
                "difficulty": round(difficulty, 3),
                "repetitions": repetitions,
                "lapses": lapses,
                "last_confidence": confidence,
                "last_calibration": calibration,
            }
            log_record = {
                **pending,
                "graded_at": now.isoformat(),
                "grade": grade,
                "schedule": card_state,
            }
            # Make the audit record durable before consuming the pending attempt.
            # If the following atomic state write fails, retrying this request
            # recovers from the log without appending a duplicate event.
            self._append_log(log_record)
            state["cards"][card_id] = card_state
            state["pending_attempts"].pop(attempt_id, None)
            self._write(state)
        return self._grade_response(card_state, grade)
