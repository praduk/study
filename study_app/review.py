from __future__ import annotations

import hashlib
import json
import math
import os
import stat
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .review_calibration import (
    CALIBRATION_VERSION,
    MAX_INTERVAL_DAYS,
    apply_recorded_observation,
    calibration_reporting_summary,
    calibration_summary,
    new_calibration_state,
    observe_review,
    reporting_model_estimate,
    schedule_interval,
    validate_recorded_observation,
)
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
RECENT_LOG_CACHE_SIZE = 64
MAX_REPORT_RANGE = timedelta(days=366)
DEFAULT_CALENDAR_RANGE = timedelta(days=90)
GRADE_NAMES = ("again", "hard", "good", "easy")
MAX_TIME_ZONE_LENGTH = 128


def _now() -> datetime:
    return datetime.now(timezone.utc)


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


def _atomic_json(path: Path, value: Any) -> None:
    _atomic_bytes(
        path,
        (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    )


def _extend_log_digest(previous: str | None, encoded_record: str) -> str:
    """Extend a chain digest so a persisted checkpoint can accept new suffixes."""
    digest = hashlib.sha256()
    if previous is not None:
        digest.update(bytes.fromhex(previous))
    digest.update(encoded_record.strip().encode("utf-8"))
    return digest.hexdigest()


def _calibration_digest(calibration: dict[str, Any]) -> str:
    encoded = json.dumps(
        calibration,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _cards_digest(cards: dict[str, Any]) -> str:
    encoded = json.dumps(
        cards,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class ReviewEngine:
    """A bounded self-calibrating scheduler; its target is the learner's self-grade."""

    def __init__(self, store: LibraryStore):
        self.store = store
        self.state_path = store.data_dir / "review.json"
        self.log_path = store.data_dir / "review-log.jsonl"
        self._lock = store.mutation_lock
        self._calibration_verified = False
        self._log_signature_cache: tuple[int, int, int, int] | None = None
        self._log_checkpoint_cache: tuple[int, str | None, str | None] = (
            0,
            None,
            None,
        )
        self._calibration_cache: dict[str, Any] | None = None
        self._calibration_digest_cache: str | None = None
        self._cards_digest_cache: str | None = None
        self._recent_logged_attempts: dict[str, dict[str, Any]] = {}
        self._recent_log_order: list[str] = []
        self._known_current_cards: frozenset[str] | None = None
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
        if not isinstance(result["cards"], dict) or not isinstance(
            result["pending_attempts"], dict
        ):
            raise StoreError("review state has invalid card or attempt data")
        for card_id, card_state in result["cards"].items():
            self._validate_card_state(card_id, card_state)
        for attempt_id, attempt in result["pending_attempts"].items():
            self._validate_pending_attempt(attempt_id, attempt)
        return result

    def _write(self, state: dict[str, Any]) -> None:
        state["updated_at"] = _now().isoformat()
        # Bayesian calibration is derived from the review log. Keeping its
        # 161-point posterior grids in versioned current state makes every
        # grade create a large, conflict-prone JSON diff.
        persisted = {key: value for key, value in state.items() if key != "calibration"}
        _atomic_json(self.state_path, persisted)

    def _log_signature(self) -> tuple[int, int, int, int] | None:
        try:
            details = self.log_path.lstat()
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise StoreError("review-log.jsonl cannot be inspected") from exc
        if stat.S_ISLNK(details.st_mode) or not stat.S_ISREG(details.st_mode):
            raise StoreError("review-log.jsonl is not a safe regular file")
        return (details.st_dev, details.st_ino, details.st_size, details.st_mtime_ns)

    def _remember_logged_attempt(self, record: dict[str, Any]) -> None:
        attempt_id = record["id"]
        if attempt_id in self._recent_logged_attempts:
            self._recent_log_order.remove(attempt_id)
        self._recent_logged_attempts[attempt_id] = record
        self._recent_log_order.append(attempt_id)
        while len(self._recent_log_order) > RECENT_LOG_CACHE_SIZE:
            expired = self._recent_log_order.pop(0)
            self._recent_logged_attempts.pop(expired, None)

    def _cache_complete_log(
        self,
        signature: tuple[int, int, int, int] | None,
        calibration: dict[str, Any],
        cards: dict[str, Any],
        recent_records: list[dict[str, Any]],
    ) -> None:
        self._calibration_cache = calibration
        self._log_signature_cache = signature
        self._log_checkpoint_cache = (
            calibration["processed_log_records"],
            calibration["last_log_attempt_id"],
            calibration["processed_log_digest"],
        )
        self._calibration_digest_cache = _calibration_digest(calibration)
        self._cards_digest_cache = _cards_digest(cards)
        self._recent_logged_attempts = {}
        self._recent_log_order = []
        for record in recent_records:
            self._remember_logged_attempt(record)

    def _cache_appended_record(
        self,
        record: dict[str, Any],
        encoded_record: str,
        added_bytes: int,
        calibration: dict[str, Any],
        cards: dict[str, Any],
    ) -> None:
        """Advance the verified in-process cache after both durable writes succeed."""
        current_signature = self._log_signature()
        previous_signature = self._log_signature_cache
        file_append_matches = current_signature is not None and (
            (
                previous_signature is None
                and current_signature[2] == added_bytes
            )
            or (
                previous_signature is not None
                and current_signature[:2] == previous_signature[:2]
                and current_signature[2] == previous_signature[2] + added_bytes
            )
        )
        expected_digest = _extend_log_digest(
            self._log_checkpoint_cache[2], encoded_record
        )
        checkpoint_matches = (
            calibration["processed_log_records"]
            == self._log_checkpoint_cache[0] + 1
            and calibration["last_log_attempt_id"] == record["id"]
            and calibration["processed_log_digest"] == expected_digest
        )
        if not file_append_matches or not checkpoint_matches:
            self._calibration_verified = False
            return
        self._log_signature_cache = current_signature
        self._log_checkpoint_cache = (
            calibration["processed_log_records"],
            calibration["last_log_attempt_id"],
            calibration["processed_log_digest"],
        )
        self._calibration_digest_cache = _calibration_digest(calibration)
        self._calibration_cache = calibration
        self._cards_digest_cache = _cards_digest(cards)
        self._remember_logged_attempt(record)
        self._calibration_verified = True

    @staticmethod
    def _aware_datetime(value: Any, label: str) -> datetime:
        if not isinstance(value, str):
            raise StoreError(f"{label} is not a timestamp")
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:
            raise StoreError(f"{label} is not a timestamp") from exc
        if parsed.tzinfo is None:
            raise StoreError(f"{label} has no timezone")
        return parsed

    @staticmethod
    def _finite_card_number(
        value: Any, label: str, *, minimum: float, maximum: float | None = None
    ) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise StoreError(f"{label} is not numeric")
        try:
            result = float(value)
        except OverflowError as exc:
            raise StoreError(f"{label} is outside its valid range") from exc
        if (
            not math.isfinite(result)
            or result < minimum
            or (maximum is not None and result > maximum)
        ):
            raise StoreError(f"{label} is outside its valid range")
        return result

    @staticmethod
    def _card_count(value: Any, label: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise StoreError(f"{label} is outside its valid range")
        return value

    @classmethod
    def _validate_card_state(
        cls, card_id: Any, value: Any, *, require_complete: bool = False
    ) -> None:
        if not isinstance(card_id, str) or not isinstance(value, dict):
            raise StoreError("review card state is invalid")
        cls.split_card_id(card_id)
        if not value and not require_complete:
            return
        required = {
            "due_at",
            "last_reviewed_at",
            "last_grade",
            "last_elapsed_ms",
            "stability_days",
            "difficulty",
            "repetitions",
            "lapses",
        }
        if (require_complete or value) and not required.issubset(value):
            raise StoreError("review card schedule is incomplete")
        if "due_at" in value:
            cls._aware_datetime(value["due_at"], "review due time")
        if "last_reviewed_at" in value:
            cls._aware_datetime(value["last_reviewed_at"], "review time")
        if "last_grade" in value:
            grade = value["last_grade"]
            if isinstance(grade, bool) or not isinstance(grade, int) or grade not in range(4):
                raise StoreError("review grade is outside its valid range")
        if "last_elapsed_ms" in value:
            cls._card_count(value["last_elapsed_ms"], "review elapsed time")
        if "stability_days" in value:
            stability = cls._finite_card_number(
                value["stability_days"], "review stability", minimum=0.0
            )
            if stability == 0.0:
                raise StoreError("review stability must be positive")
        if "difficulty" in value:
            cls._finite_card_number(
                value["difficulty"], "review difficulty", minimum=1.0, maximum=10.0
            )
        if "repetitions" in value:
            cls._card_count(value["repetitions"], "review repetitions")
        if "lapses" in value:
            cls._card_count(value["lapses"], "review lapses")
        if "scheduler" in value and not isinstance(value["scheduler"], dict):
            raise StoreError("review scheduler diagnostics are invalid")

    @classmethod
    def _validate_pending_attempt(cls, attempt_id: Any, value: Any) -> None:
        if not isinstance(attempt_id, str) or not isinstance(value, dict):
            raise StoreError("pending review attempt is invalid")
        if value.get("id") != attempt_id:
            raise StoreError("pending review attempt ID is inconsistent")
        card_id = value.get("card_id")
        if not isinstance(card_id, str):
            raise StoreError("pending review attempt has no card")
        entry_id, mode = cls.split_card_id(card_id)
        if value.get("entry_id") != entry_id or value.get("mode") != mode:
            raise StoreError("pending review attempt does not match its card")
        cls._aware_datetime(value.get("started_at"), "review attempt time")
        cls._card_count(value.get("elapsed_ms", 0), "review attempt elapsed time")

    @classmethod
    def _validate_log_record(
        cls, value: Any, line_number: int
    ) -> tuple[str, str, dict[str, Any], int, datetime]:
        label = f"review log line {line_number}"
        if not isinstance(value, dict):
            raise StoreError(f"{label} is not an object")
        attempt_id = value.get("id")
        if (
            not isinstance(attempt_id, str)
            or len(attempt_id) != 32
            or any(character not in "0123456789abcdef" for character in attempt_id)
        ):
            raise StoreError(f"{label} has an invalid attempt ID")
        card_id = value.get("card_id")
        if not isinstance(card_id, str):
            raise StoreError(f"{label} has an invalid card")
        try:
            entry_id, mode = cls.split_card_id(card_id)
        except StoreError as exc:
            raise StoreError(f"{label} has an invalid card") from exc
        if value.get("entry_id") != entry_id or value.get("mode") != mode:
            raise StoreError(f"{label} does not match its card")
        grade = value.get("grade")
        if isinstance(grade, bool) or not isinstance(grade, int) or grade not in range(4):
            raise StoreError(f"{label} has an invalid grade")
        schedule = value.get("schedule")
        try:
            cls._validate_card_state(card_id, schedule, require_complete=True)
        except StoreError as exc:
            raise StoreError(f"{label} has an invalid schedule") from exc
        if schedule["last_grade"] != grade:
            raise StoreError(f"{label} schedule does not match its grade")
        observed_text = value.get("started_at", value.get("graded_at"))
        try:
            observed_at = cls._aware_datetime(observed_text, "review observation time")
        except StoreError as exc:
            raise StoreError(f"{label} has an invalid observation time") from exc
        try:
            reviewed_at = cls._aware_datetime(
                schedule["last_reviewed_at"], "review completion time"
            )
            due_at = cls._aware_datetime(schedule["due_at"], "review due time")
            graded_at = (
                cls._aware_datetime(value["graded_at"], "review grade time")
                if "graded_at" in value
                else observed_at
            )
        except StoreError as exc:
            raise StoreError(f"{label} has an invalid review chronology") from exc
        if reviewed_at < max(observed_at, graded_at) or due_at <= reviewed_at:
            raise StoreError(f"{label} has an invalid review chronology")
        event_version = value.get("calibration_event_version")
        if event_version is not None and (
            isinstance(event_version, bool)
            or event_version not in {1, CALIBRATION_VERSION}
        ):
            raise StoreError(f"{label} has an unsupported calibration event")
        observation = value.get("calibration_observation")
        if observation is not None:
            try:
                validate_recorded_observation(observation, mode=mode, grade=grade)
            except (TypeError, ValueError) as exc:
                raise StoreError(f"{label} has an invalid calibration observation") from exc
        return attempt_id, mode, schedule, grade, observed_at

    def _sync_state_with_log(
        self,
        state: dict[str, Any],
        attempt_id: str | None = None,
        *,
        force_rebuild: bool = False,
        record_visitor: Callable[[dict[str, Any]], None] | None = None,
    ) -> tuple[dict[str, Any] | None, dict[str, Any], bool]:
        """Use a verified cache or rebuild derived state from authoritative history."""
        had_persisted_calibration = "calibration" in state
        cached_calibration = self._calibration_cache
        signature_before = self._log_signature()
        if (
            not force_rebuild
            and record_visitor is None
            and self._calibration_verified
            and not had_persisted_calibration
            and cached_calibration is not None
            and signature_before == self._log_signature_cache
            and _calibration_digest(cached_calibration)
            == self._calibration_digest_cache
            and _cards_digest(state["cards"]) == self._cards_digest_cache
            and (
                cached_calibration["processed_log_records"],
                cached_calibration["last_log_attempt_id"],
                cached_calibration["processed_log_digest"],
            )
            == self._log_checkpoint_cache
        ):
            logged_attempt = self._recent_logged_attempts.get(attempt_id or "")
            if (
                attempt_id is None
                or logged_attempt is not None
                or attempt_id in state["pending_attempts"]
            ):
                state["calibration"] = cached_calibration
                return logged_attempt, cached_calibration, False

        # Startup, external file changes, old idempotency lookups, and explicit
        # validation all take the deterministic full-replay path.
        self._calibration_verified = False
        calibration = new_calibration_state()
        current_digest: str | None = None
        record_count = 0
        last_attempt_id: str | None = None
        logged_attempt: dict[str, Any] | None = None
        previous_cards: dict[str, dict[str, Any]] = {}
        latest_schedules: dict[str, dict[str, Any]] = {}
        logged_pending_attempts: set[str] = set()
        seen_attempts: set[str] = set()
        recent_records: list[dict[str, Any]] = []

        if signature_before is not None:
            try:
                with self.log_path.open(encoding="utf-8") as stream:
                    for line_number, line in enumerate(stream, start=1):
                        if not line.strip():
                            continue
                        record = json.loads(line)
                        (
                            record_attempt,
                            mode,
                            schedule,
                            grade,
                            observed_at,
                        ) = self._validate_log_record(record, line_number)
                        if record_attempt in seen_attempts:
                            raise StoreError(
                                f"review log line {line_number} duplicates an attempt ID"
                            )
                        seen_attempts.add(record_attempt)
                        record_count += 1
                        current_digest = _extend_log_digest(current_digest, line)
                        last_attempt_id = record_attempt
                        recent_records.append(record)
                        if len(recent_records) > RECENT_LOG_CACHE_SIZE:
                            recent_records.pop(0)

                        if record_attempt == attempt_id:
                            logged_attempt = record
                        if record_attempt in state["pending_attempts"]:
                            logged_pending_attempts.add(record_attempt)

                        previous = previous_cards.get(record["card_id"])
                        if previous is not None:
                            previous_reviewed_at = self._aware_datetime(
                                previous["last_reviewed_at"],
                                f"review log line {line_number} previous review time",
                            )
                            current_reviewed_at = self._aware_datetime(
                                schedule["last_reviewed_at"],
                                f"review log line {line_number} review time",
                            )
                            if current_reviewed_at < previous_reviewed_at:
                                raise StoreError(
                                    f"review log line {line_number} moves its card backward in time"
                                )
                        if record_visitor is not None:
                            record_visitor(record)
                        observation = record.get("calibration_observation")
                        if observation is not None:
                            if (
                                previous is None
                                and observation.get("version") == CALIBRATION_VERSION
                            ):
                                raise StoreError(
                                    f"review log line {line_number} has calibration evidence "
                                    "without a previous review"
                                )
                            try:
                                apply_recorded_observation(
                                    calibration,
                                    observation,
                                    mode=mode,
                                    grade=grade,
                                    observed_at=observed_at,
                                    card_id=record["card_id"],
                                    previous_card_state=previous,
                                )
                            except (TypeError, ValueError) as exc:
                                raise StoreError(
                                    f"review log line {line_number} has inconsistent "
                                    "calibration evidence"
                                ) from exc
                        elif (
                            record.get("calibration_event_version") is None
                            and previous is not None
                        ):
                            # Old records predate explicit observation data.
                            observe_review(
                                calibration,
                                mode,
                                previous,
                                observed_at,
                                grade,
                                card_id=record["card_id"],
                                evaluate_forecast=False,
                            )
                        previous_cards[record["card_id"]] = schedule
                        latest_schedules[record["card_id"]] = schedule
            except StoreError:
                raise
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise StoreError("review-log.jsonl is unreadable or invalid") from exc

        signature_after = self._log_signature()
        if signature_after != signature_before:
            raise StoreError("review-log.jsonl changed while it was being validated")

        calibration["processed_log_records"] = record_count
        calibration["last_log_attempt_id"] = last_attempt_id
        calibration["processed_log_digest"] = current_digest

        # A legacy persisted calibration is deliberately removed on the next
        # state write. The authoritative log always reconstructs it exactly.
        changed = had_persisted_calibration
        for card_id, schedule in latest_schedules.items():
            if state["cards"].get(card_id) != schedule:
                state["cards"][card_id] = schedule
                changed = True
        for logged_id in logged_pending_attempts:
            state["pending_attempts"].pop(logged_id, None)
            changed = True
        state["calibration"] = calibration
        self._cache_complete_log(
            signature_after, calibration, state["cards"], recent_records
        )
        return logged_attempt, calibration, changed

    def validate_log(self) -> dict[str, Any]:
        """Fully validate state and replayable history without changing either file."""
        with self._lock:
            state = self._read()
            _, calibration, _ = self._sync_state_with_log(state, force_rebuild=True)
            return calibration_summary(calibration)

    def rebuild_calibration(self) -> dict[str, Any]:
        """Rebuild and persist all derived review state from authoritative history."""
        with self._lock:
            state = self._read()
            _, calibration, changed = self._sync_state_with_log(
                state, force_rebuild=True
            )
            if changed:
                self._write(state)
            self._calibration_verified = True
            return calibration_summary(calibration)

    def _current_card_ids(self) -> set[str]:
        current: set[str] = set()
        for entry in self.store.snapshot()["entries"]:
            for mode in entry.get("review_modes", []):
                if self.store.review_mode_available(entry, mode):
                    current.add(self.card_id(entry["id"], mode))
        return current

    def _prune_if_library_changed(self) -> None:
        """Compact stale review data after a live direct library edit."""
        with self._lock:
            current_cards = frozenset(self._current_card_ids())
            if current_cards != self._known_current_cards:
                self.prune_to_current_library()

    def prune_to_current_library(self) -> dict[str, int]:
        """Remove review data for entries and review tasks that no longer exist."""
        with self._lock:
            state = self._read()
            records: list[dict[str, Any]] = []
            _, _, replayed_changed = self._sync_state_with_log(
                state,
                force_rebuild=True,
                record_visitor=records.append,
            )
            validated_log_signature = self._log_signature()
            current_cards = self._current_card_ids()
            retained_records = [
                record for record in records if record["card_id"] in current_cards
            ]
            removed_log_records = len(records) - len(retained_records)

            retained_cards = {
                card_id: card
                for card_id, card in state["cards"].items()
                if card_id in current_cards
            }
            retained_attempts = {
                attempt_id: attempt
                for attempt_id, attempt in state["pending_attempts"].items()
                if attempt["card_id"] in current_cards
            }
            removed_cards = len(state["cards"]) - len(retained_cards)
            removed_pending_attempts = (
                len(state["pending_attempts"]) - len(retained_attempts)
            )

            if not (removed_log_records or removed_cards or removed_pending_attempts):
                if replayed_changed:
                    self._write(state)
                self._calibration_verified = True
                self._known_current_cards = frozenset(current_cards)
                return {
                    "removed_cards": 0,
                    "removed_pending_attempts": 0,
                    "removed_log_records": 0,
                    "retained_log_records": len(retained_records),
                }

            if removed_log_records:
                if self._log_signature() != validated_log_signature:
                    raise StoreError(
                        "review-log.jsonl changed while it was being compacted"
                    )
                for record in retained_records:
                    # A recorded forecast was made from the posterior that
                    # existed before deletion. Removing interleaved evidence
                    # changes that posterior, so retaining the forecast would
                    # make the compacted log fail validation and would report
                    # a counterfactual performance score. Legacy replay
                    # reconstructs model evidence from the surviving card
                    # history without treating it as an out-of-sample forecast.
                    record.pop("calibration_observation", None)
                    record.pop("calibration_event_version", None)
                encoded = b"".join(
                    (
                        json.dumps(record, ensure_ascii=False) + "\n"
                    ).encode("utf-8")
                    for record in retained_records
                )
                # Rewrite history before state. If the following state write is
                # interrupted, the next startup replays this compacted log and
                # completes the same cleanup.
                _atomic_bytes(self.log_path, encoded)

            state["cards"] = retained_cards
            state["pending_attempts"] = retained_attempts
            if removed_log_records:
                state.pop("calibration", None)
                self._calibration_verified = False
                self._sync_state_with_log(state, force_rebuild=True)
            self._write(state)
            self._calibration_verified = True
            self._known_current_cards = frozenset(current_cards)
            return {
                "removed_cards": removed_cards,
                "removed_pending_attempts": removed_pending_attempts,
                "removed_log_records": removed_log_records,
                "retained_log_records": len(retained_records),
            }

    def _calibration_for_state(self, state: dict[str, Any]) -> dict[str, Any]:
        _, calibration, _ = self._sync_state_with_log(state)
        state["calibration"] = calibration
        return calibration

    def _append_log(self, record: dict[str, Any]) -> tuple[str, int]:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        encoded = json.dumps(record, ensure_ascii=False)
        encoded_bytes = encoded.encode("utf-8")
        with self.log_path.open("ab+") as stream:
            stream.seek(0, os.SEEK_END)
            size = stream.tell()
            separator = b""
            if size:
                stream.seek(-1, os.SEEK_END)
                if stream.read(1) != b"\n":
                    separator = b"\n"
                stream.seek(0, os.SEEK_END)
            payload = separator + encoded_bytes + b"\n"
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        return encoded, len(payload)

    @staticmethod
    def _grade_response(card_state: dict[str, Any], grade: int) -> dict[str, Any]:
        return {
            **card_state,
            "retry_in_session": grade == 0,
            "retry_after_items": 3 if grade == 0 else None,
            "note": "Intervals self-calibrate to delayed self-grades after enough evidence; this remains an engineering model, not a validated measure of mastery.",
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
        statement_prompt = (
            f"Define {title}."
            if entry["kind"] == "df"
            else f"State {title}."
            if entry["kind"] in {"ax", "th"}
            else f"State {title} precisely from memory. Include every hypothesis and conclusion."
        )
        prompts = {
            "statement": statement_prompt,
            "example": f"Give an example of {title} and a near-miss. Explain the decisive difference.",
            "discriminate": f"State {title}, then give an example and a nonexample with justification.",
            "explain": f"Explain {title} in your own words. Why does it matter, and what would fail without it?",
            "proof-plan": f"Prove {title}.",
            "solve": "Solve the following problem.",
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
            self._prune_if_library_changed()
            state = self._read()
            _, _, changed = self._sync_state_with_log(state)
            if changed:
                # A durable log entry wins over stale state after an interrupted
                # atomic write, even if the browser never retries that request.
                self._write(state)
            self._calibration_verified = True
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

    @staticmethod
    def _bounded_report_range(
        start: datetime | None,
        end: datetime | None,
        *,
        now: datetime,
    ) -> tuple[datetime, datetime]:
        if now.tzinfo is None or now.utcoffset() is None:
            raise StoreError("the reporting clock has no timezone")
        now = now.astimezone(timezone.utc)
        try:
            if start is None and end is None:
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end = start + DEFAULT_CALENDAR_RANGE
            elif start is None:
                start = end - DEFAULT_CALENDAR_RANGE if end is not None else None
            elif end is None:
                end = start + DEFAULT_CALENDAR_RANGE
        except OverflowError as exc:
            raise StoreError("review calendar range is outside supported dates") from exc
        if start is None or end is None:
            raise StoreError("review calendar range is incomplete")
        if start.tzinfo is None or start.utcoffset() is None:
            raise StoreError("review calendar start must include a timezone")
        if end.tzinfo is None or end.utcoffset() is None:
            raise StoreError("review calendar end must include a timezone")
        start = start.astimezone(timezone.utc)
        end = end.astimezone(timezone.utc)
        if end <= start:
            raise StoreError("review calendar end must be after start")
        if end - start > MAX_REPORT_RANGE:
            raise StoreError("review calendar range cannot exceed 366 days")
        return start, end

    @staticmethod
    def _reporting_zone(name: str) -> ZoneInfo:
        if (
            not isinstance(name, str)
            or not name
            or name != name.strip()
            or len(name) > MAX_TIME_ZONE_LENGTH
        ):
            raise StoreError("review calendar timezone is invalid")
        try:
            return ZoneInfo(name)
        except (ZoneInfoNotFoundError, ValueError, UnicodeError) as exc:
            raise StoreError("review calendar timezone is unknown") from exc

    @staticmethod
    def _empty_history_bucket() -> dict[str, Any]:
        return {
            "attempts": 0,
            "elapsed_ms": 0,
            "grades": {name: 0 for name in GRADE_NAMES},
            "good_or_easy_self_grades": 0,
            "again_lapses": 0,
        }

    @staticmethod
    def _reported_history_bucket(bucket: dict[str, Any]) -> dict[str, Any]:
        attempts = bucket["attempts"]
        return {
            **bucket,
            "minutes": round(bucket["elapsed_ms"] / 60_000, 2),
            "good_or_easy_self_grade_rate": (
                round(bucket["good_or_easy_self_grades"] / attempts, 6)
                if attempts
                else None
            ),
        }

    @classmethod
    def _schedule_delay(
        cls, point: datetime, schedule: dict[str, Any]
    ) -> tuple[float, float] | None:
        last_reviewed = cls._aware_datetime(
            schedule.get("last_reviewed_at"), "review time"
        )
        stability_days = cls._finite_card_number(
            schedule.get("stability_days"), "review stability", minimum=0.0
        )
        if stability_days <= 0.0 or point < last_reviewed:
            return None
        delay_days = (point - last_reviewed).total_seconds() / 86_400.0
        return delay_days, delay_days / stability_days

    def calendar(
        self,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        include_inactive: bool = False,
        timezone_name: str = "UTC",
    ) -> dict[str, Any]:
        """Report due events; compact stale review data after an out-of-band library edit."""
        now = _now()
        start, end = self._bounded_report_range(start, end, now=now)
        now = now.astimezone(timezone.utc)
        reporting_zone = self._reporting_zone(timezone_name)

        daily: dict[str, dict[str, Any]] = {}
        day = start.astimezone(reporting_zone).date()
        final_day = (end - timedelta(microseconds=1)).astimezone(reporting_zone).date()
        while day <= final_day:
            daily[day.isoformat()] = self._empty_history_bucket()
            if day == final_day:
                break
            day += timedelta(days=1)
        total = self._empty_history_bucket()

        def record_history(record: dict[str, Any]) -> None:
            if record["card_id"] not in current_cards:
                return
            schedule = record["schedule"]
            completed_at = self._aware_datetime(
                schedule["last_reviewed_at"], "review completion time"
            ).astimezone(timezone.utc)
            if not start <= completed_at < end:
                return
            grade = record["grade"]
            elapsed_ms = schedule["last_elapsed_ms"]
            local_date = completed_at.astimezone(reporting_zone).date().isoformat()
            for bucket in (total, daily[local_date]):
                bucket["attempts"] += 1
                bucket["elapsed_ms"] += elapsed_ms
                bucket["grades"][GRADE_NAMES[grade]] += 1
                if grade >= 2:
                    bucket["good_or_easy_self_grades"] += 1
                if grade == 0:
                    bucket["again_lapses"] += 1

        with self._lock:
            self._prune_if_library_changed()
            all_entries = self.store.ordered_entries(review_only=False)
            active_entries = self.store.ordered_entries(review_only=True)
            entry_by_id = {entry["id"]: entry for entry in all_entries}
            active_entry_ids = {entry["id"] for entry in active_entries}
            authored_order = {
                entry["id"]: index for index, entry in enumerate(all_entries)
            }

            current_cards: set[str] = set()
            active_cards: set[str] = set()
            mode_order: dict[str, int] = {}
            for entry in all_entries:
                modes = entry.get("review_modes") or self.store.default_review_modes(
                    entry["kind"]
                )
                for index, mode in enumerate(modes):
                    if not self.store.review_mode_available(entry, mode):
                        continue
                    card_id = self.card_id(entry["id"], mode)
                    current_cards.add(card_id)
                    mode_order[card_id] = index
                    if entry["id"] in active_entry_ids:
                        active_cards.add(card_id)

            state = self._read()
            _, calibration, _ = self._sync_state_with_log(
                state,
                force_rebuild=True,
                record_visitor=record_history,
            )

            events: list[tuple[datetime, int, int, str, dict[str, Any]]] = []
            for card_id, schedule in state["cards"].items():
                if not schedule:
                    continue
                entry_id, mode = self.split_card_id(card_id)
                entry = entry_by_id.get(entry_id)
                # A direct file edit can briefly leave stale state before startup
                # compacts it. Never surface that deleted entry in reporting.
                if entry is None:
                    continue
                due_at = self._aware_datetime(
                    schedule["due_at"], "review due time"
                ).astimezone(timezone.utc)
                if not start <= due_at < end:
                    continue
                active = card_id in active_cards
                if not active and not include_inactive:
                    continue
                review_enabled = entry_id in active_entry_ids
                if active:
                    inactive_reason = None
                elif card_id not in current_cards:
                    inactive_reason = "mode-unavailable"
                else:
                    inactive_reason = "review-disabled"
                last_reviewed = self._aware_datetime(
                    schedule["last_reviewed_at"], "review time"
                )
                delay_now = self._schedule_delay(now, schedule)
                delay_at_due = self._schedule_delay(due_at, schedule)
                model_estimate = reporting_model_estimate(
                    calibration,
                    mode,
                    delay_days_now=delay_now[0] if delay_now is not None else None,
                    normalized_delay_now=delay_now[1] if delay_now is not None else None,
                    delay_days_at_due=(
                        delay_at_due[0] if delay_at_due is not None else None
                    ),
                    normalized_delay_at_due=(
                        delay_at_due[1] if delay_at_due is not None else None
                    ),
                )
                event = {
                    "card_id": card_id,
                    "entry_id": entry_id,
                    "folder_id": entry["folder_id"],
                    "title": entry["title"],
                    "canonical_tag": entry["canonical_tag"],
                    "kind": entry["kind"],
                    "mode": mode,
                    "mode_label": MODE_LABELS[mode],
                    "due_at": due_at.isoformat(),
                    "last_reviewed_at": last_reviewed.astimezone(timezone.utc).isoformat(),
                    "active": active,
                    "review_enabled": review_enabled,
                    "orphaned": inactive_reason == "mode-unavailable",
                    "inactive_reason": inactive_reason,
                    "schedule_at_last_grade": dict(schedule),
                    "model_estimate": model_estimate,
                }
                events.append(
                    (
                        due_at,
                        authored_order.get(entry_id, len(authored_order)),
                        mode_order.get(card_id, len(MODE_LABELS)),
                        card_id,
                        event,
                    )
                )

        events.sort(key=lambda item: item[:4])
        statistics = self._reported_history_bucket(total)
        statistics["daily_timezone"] = reporting_zone.key
        statistics["daily"] = [
            {"date": date, **self._reported_history_bucket(bucket)}
            for date, bucket in daily.items()
        ]
        return {
            "range": {"start": start.isoformat(), "end": end.isoformat()},
            "events": [item[4] for item in events],
            "statistics": statistics,
            "calibration": calibration_reporting_summary(calibration),
        }

    def stats(self) -> dict[str, Any]:
        with self._lock:
            due = self.queue(limit=10000)
            state = self._read()
            calibration = self._calibration_for_state(state)
            current_cards = self._current_card_ids()
            today = _now().date().isoformat()
            completed_today = sum(
                1
                for card_id, card in state["cards"].items()
                if card_id in current_cards
                and str(card.get("last_reviewed_at", "")).startswith(today)
            )
            minutes = round(
                sum(
                    int(card.get("last_elapsed_ms", 0))
                    for card_id, card in state["cards"].items()
                    if card_id in current_cards
                    and str(card.get("last_reviewed_at", "")).startswith(today)
                )
                / 60_000
            )
        return {
            "due": len(due),
            "completed_today": completed_today,
            "minutes_today": minutes,
            "calibration": calibration_summary(calibration),
        }

    def reveal(self, card_id: str, attempt: dict[str, Any]) -> dict[str, Any]:
        entry_id, mode = self.split_card_id(card_id)
        with self._lock:
            self._prune_if_library_changed()
            # Entry lookup and pending-attempt persistence share the library
            # mutation lock with deletion, so a reveal cannot recreate review
            # state after its entry has been removed.
            entry = self.store.get_entry(entry_id)
            if mode not in entry.get(
                "review_modes", []
            ) or not self.store.review_mode_available(entry, mode):
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
            state = self._read()
            self._sync_state_with_log(state)
            state["pending_attempts"][attempt_id] = created
            self._write(state)
            self._calibration_verified = True
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
        if isinstance(grade, bool) or not isinstance(grade, int) or grade not in range(4):
            raise StoreError("review grade is outside its valid range")
        now = _now()
        with self._lock:
            self._prune_if_library_changed()
            state = self._read()
            logged, model_calibration, changed = self._sync_state_with_log(
                state, attempt_id
            )
            pending = state["pending_attempts"].get(attempt_id)
            if logged is not None:
                if logged.get("card_id") != card_id or logged.get("grade") != grade:
                    raise StoreError("review attempt was already graded differently")
                schedule = logged.get("schedule")
                if not isinstance(schedule, dict):
                    raise StoreError("review log contains an invalid schedule")
                if changed:
                    self._write(state)
                self._calibration_verified = True
                return self._grade_response(schedule, grade)
            if pending is None or pending["card_id"] != card_id:
                raise StoreError("review attempt is missing, expired, or belongs to another card")
            try:
                observation_at = datetime.fromisoformat(str(pending["started_at"]))
            except (KeyError, TypeError, ValueError) as exc:
                raise StoreError("review attempt has an invalid timestamp") from exc
            if observation_at.tzinfo is None:
                raise StoreError("review attempt timestamp has no timezone")
            previous = state["cards"].get(card_id, {})
            completion_at = max(now, observation_at)
            if previous:
                previous_reviewed_at = self._aware_datetime(
                    previous["last_reviewed_at"], "previous review time"
                )
                completion_at = max(completion_at, previous_reviewed_at)
            old_stability = self._finite_card_number(
                previous.get("stability_days", 0.5),
                "review stability",
                minimum=0.0,
            )
            if old_stability == 0.0:
                raise StoreError("review stability must be positive")
            old_difficulty = self._finite_card_number(
                previous.get("difficulty", 5.0),
                "review difficulty",
                minimum=1.0,
                maximum=10.0,
            )
            repetitions = self._card_count(
                previous.get("repetitions", 0), "review repetitions"
            )
            lapses = self._card_count(previous.get("lapses", 0), "review lapses")

            _, mode = self.split_card_id(card_id)

            if grade == 0:
                stability = min(MAX_INTERVAL_DAYS, max(0.25, old_stability * 0.45))
                difficulty = min(10.0, old_difficulty + 0.7)
                due = completion_at + timedelta(minutes=10)
                _, scheduler = schedule_interval(model_calibration, mode, stability, 1)
                scheduler.update(
                    {
                        "calibrated_interval_used": False,
                        "interval_days": None,
                        "interval_minutes": 10,
                        "reason": "again",
                    }
                )
                lapses += 1
            elif grade == 1:
                stability = min(MAX_INTERVAL_DAYS, max(1.0, old_stability * 1.35))
                difficulty = min(10.0, old_difficulty + 0.2)
                interval_days, scheduler = schedule_interval(model_calibration, mode, stability, 1)
                due = completion_at + timedelta(days=interval_days)
                scheduler["calibrated_interval_used"] = scheduler["calibrated"]
                repetitions += 1
            elif grade == 2:
                stability = min(
                    MAX_INTERVAL_DAYS,
                    max(2.0, old_stability * (2.25 - old_difficulty * 0.035)),
                )
                difficulty = max(1.0, old_difficulty - 0.15)
                interval_days, scheduler = schedule_interval(model_calibration, mode, stability, 1)
                due = completion_at + timedelta(days=interval_days)
                scheduler["calibrated_interval_used"] = scheduler["calibrated"]
                repetitions += 1
            else:
                stability = min(
                    MAX_INTERVAL_DAYS,
                    max(4.0, old_stability * (3.1 - old_difficulty * 0.045)),
                )
                difficulty = max(1.0, old_difficulty - 0.35)
                interval_days, scheduler = schedule_interval(model_calibration, mode, stability, 2)
                due = completion_at + timedelta(days=interval_days)
                scheduler["calibrated_interval_used"] = scheduler["calibrated"]
                repetitions += 1

            calibration_observation = observe_review(
                model_calibration,
                mode,
                previous,
                observation_at,
                grade,
                card_id=card_id,
            )

            confidence = pending.get("confidence")
            confidence_calibration = None
            if confidence is not None:
                expected = 1 if grade == 0 else 2 if grade < 3 else 3
                confidence_calibration = int(confidence) - expected
                if grade == 0 and confidence == 3:
                    difficulty = min(10.0, difficulty + 0.35)

            card_state = {
                "due_at": due.isoformat(),
                "last_reviewed_at": completion_at.isoformat(),
                "last_grade": grade,
                "last_elapsed_ms": int(pending.get("elapsed_ms", 0)),
                "stability_days": round(stability, 3),
                "difficulty": round(difficulty, 3),
                "repetitions": repetitions,
                "lapses": lapses,
                "last_confidence": confidence,
                "last_calibration": confidence_calibration,
                "scheduler": scheduler,
            }
            log_record = {
                **pending,
                "graded_at": now.isoformat(),
                "grade": grade,
                "schedule": card_state,
                "calibration_event_version": CALIBRATION_VERSION,
            }
            if calibration_observation:
                log_record["calibration_observation"] = calibration_observation
            # Make the audit record durable before consuming the pending attempt.
            # If the following atomic state write fails, retrying this request
            # recovers from the log without appending a duplicate event.
            encoded_record, added_bytes = self._append_log(log_record)
            model_calibration["processed_log_records"] += 1
            model_calibration["last_log_attempt_id"] = attempt_id
            model_calibration["processed_log_digest"] = _extend_log_digest(
                model_calibration["processed_log_digest"], encoded_record
            )
            state["cards"][card_id] = card_state
            state["calibration"] = model_calibration
            state["pending_attempts"].pop(attempt_id, None)
            self._write(state)
            self._cache_appended_record(
                log_record,
                encoded_record,
                added_bytes,
                model_calibration,
                state["cards"],
            )
        return self._grade_response(card_state, grade)
