from __future__ import annotations

import math
from datetime import datetime
from typing import Any

# The model predicts the learner's probability of assigning Good or Easy.  At
# the neutral interval scale (1.0), the prior curve reaches the scheduling
# target when elapsed time equals the card's current stability.
CALIBRATION_VERSION = 1
CALIBRATED_MODES = ("statement", "proof-plan", "solve")
POOLED_MODEL = "pooled"
MODEL_KEYS = (POOLED_MODEL, *CALIBRATED_MODES)
TARGET_SUCCESS = 0.90
RESPONSE_FLOOR = 0.02
BASE_DECAY = -math.log((TARGET_SUCCESS - RESPONSE_FLOOR) / (1.0 - 2.0 * RESPONSE_FLOOR))

# A log-spaced grid makes the posterior exact on a small, bounded parameter
# space without adding a numerical dependency.  The interval scale is kept
# deliberately broad; the scheduler applies tighter operational bounds below.
GRID_SIZE = 161
MIN_INTERVAL_SCALE = 1.0 / 8.0
MAX_INTERVAL_SCALE = 8.0
_LOG_SCALE_MIN = math.log(MIN_INTERVAL_SCALE)
_LOG_SCALE_STEP = (math.log(MAX_INTERVAL_SCALE) - _LOG_SCALE_MIN) / (GRID_SIZE - 1)
INTERVAL_SCALE_GRID = tuple(
    math.exp(_LOG_SCALE_MIN + index * _LOG_SCALE_STEP) for index in range(GRID_SIZE)
)
PRIOR_LOG_SD = 0.70

# Discounting is a small power-prior "forgetting" step.  It lets recent grades
# eventually outweigh very old grading behavior while retaining about 200
# observations' effective weight.
HISTORY_DISCOUNT = 0.995
MIN_DELAY_DAYS = 0.25
MIN_RAW_OBSERVATIONS = 24
MIN_EFFECTIVE_OBSERVATIONS = 20.0
MIN_EFFECTIVE_EXPOSURE = 12.0
MIN_SCHEDULE_FACTOR = 0.50
MAX_SCHEDULE_FACTOR = 2.00
MAX_INTERVAL_DAYS = 3650


def _normalise_log_weights(values: list[float]) -> list[float]:
    maximum = max(values)
    total = sum(math.exp(value - maximum) for value in values)
    offset = maximum + math.log(total)
    return [value - offset for value in values]


PRIOR_LOG_WEIGHTS = tuple(
    _normalise_log_weights(
        [
            -0.5 * (math.log(scale) / PRIOR_LOG_SD) ** 2
            for scale in INTERVAL_SCALE_GRID
        ]
    )
)


def new_model_state() -> dict[str, Any]:
    return {
        "log_weights": list(PRIOR_LOG_WEIGHTS),
        "observations": 0,
        "successes": 0,
        "effective_observations": 0.0,
        "effective_successes": 0.0,
        "effective_exposure": 0.0,
        "last_observed_at": None,
    }


def new_calibration_state() -> dict[str, Any]:
    return {
        "version": CALIBRATION_VERSION,
        "target_grade": "good-or-easy",
        "target_probability": TARGET_SUCCESS,
        "history_discount": HISTORY_DISCOUNT,
        "models": {key: new_model_state() for key in MODEL_KEYS},
    }


def _finite_number(value: Any, name: str, *, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} is not numeric")
    result = float(value)
    if not math.isfinite(result) or result < minimum:
        raise ValueError(f"{name} is outside its valid range")
    return result


def validate_calibration_state(value: Any) -> dict[str, Any]:
    """Return a normalised copy of persisted calibration state or raise ValueError."""
    if not isinstance(value, dict) or value.get("version") != CALIBRATION_VERSION:
        raise ValueError("unsupported calibration state")
    models = value.get("models")
    if not isinstance(models, dict):
        raise TypeError("calibration models are missing")

    result = new_calibration_state()
    for key in MODEL_KEYS:
        candidate = models.get(key)
        if not isinstance(candidate, dict):
            raise TypeError(f"calibration model {key} is missing")
        weights = candidate.get("log_weights")
        if not isinstance(weights, list) or len(weights) != GRID_SIZE:
            raise ValueError(f"calibration model {key} has invalid weights")
        numeric_weights = [
            _finite_number(item, f"calibration model {key} weight", minimum=-math.inf)
            for item in weights
        ]
        observations = candidate.get("observations")
        successes = candidate.get("successes")
        if isinstance(observations, bool) or not isinstance(observations, int) or observations < 0:
            raise ValueError(f"calibration model {key} has invalid observations")
        if (
            isinstance(successes, bool)
            or not isinstance(successes, int)
            or successes < 0
            or successes > observations
        ):
            raise ValueError(f"calibration model {key} has invalid successes")
        last_observed_at = candidate.get("last_observed_at")
        if last_observed_at is not None and not isinstance(last_observed_at, str):
            raise ValueError(f"calibration model {key} has invalid timestamp")
        result["models"][key] = {
            "log_weights": _normalise_log_weights(numeric_weights),
            "observations": observations,
            "successes": successes,
            "effective_observations": _finite_number(
                candidate.get("effective_observations", 0.0),
                f"calibration model {key} effective observations",
            ),
            "effective_successes": _finite_number(
                candidate.get("effective_successes", 0.0),
                f"calibration model {key} effective successes",
            ),
            "effective_exposure": _finite_number(
                candidate.get("effective_exposure", 0.0),
                f"calibration model {key} effective exposure",
            ),
            "last_observed_at": last_observed_at,
        }
    return result


def success_probability(normalized_delay: float, interval_scale: float) -> float:
    """Probability of a Good/Easy grade after a delay measured in stability units."""
    exponent = -BASE_DECAY * max(0.0, normalized_delay) / interval_scale
    return RESPONSE_FLOOR + (1.0 - 2.0 * RESPONSE_FLOOR) * math.exp(exponent)


def _posterior_weights(model: dict[str, Any]) -> list[float]:
    return [math.exp(value) for value in model["log_weights"]]


def posterior_predictive_success(model: dict[str, Any], normalized_delay: float) -> float:
    return sum(
        weight * success_probability(normalized_delay, scale)
        for weight, scale in zip(_posterior_weights(model), INTERVAL_SCALE_GRID, strict=True)
    )


def _observe_model(
    model: dict[str, Any], normalized_delay: float, success: bool, observed_at: datetime
) -> None:
    discounted = [
        HISTORY_DISCOUNT * old + (1.0 - HISTORY_DISCOUNT) * prior
        for old, prior in zip(model["log_weights"], PRIOR_LOG_WEIGHTS, strict=True)
    ]
    updated: list[float] = []
    for log_weight, scale in zip(discounted, INTERVAL_SCALE_GRID, strict=True):
        probability = success_probability(normalized_delay, scale)
        likelihood = math.log(probability) if success else math.log1p(-probability)
        updated.append(log_weight + likelihood)
    model["log_weights"] = _normalise_log_weights(updated)
    model["observations"] += 1
    model["successes"] += int(success)
    model["effective_observations"] = (
        HISTORY_DISCOUNT * model["effective_observations"] + 1.0
    )
    model["effective_successes"] = HISTORY_DISCOUNT * model["effective_successes"] + int(
        success
    )
    # One severely overdue review must not, by itself, unlock calibration.
    model["effective_exposure"] = (
        HISTORY_DISCOUNT * model["effective_exposure"] + min(normalized_delay, 4.0)
    )
    model["last_observed_at"] = observed_at.isoformat()


def observe_review(
    calibration: dict[str, Any],
    mode: str,
    previous_card_state: dict[str, Any],
    graded_at: datetime,
    grade: int,
) -> dict[str, Any] | None:
    """Update pooled and task-specific posteriors from one genuinely delayed review."""
    if mode not in CALIBRATED_MODES:
        return None
    try:
        stability = float(previous_card_state["stability_days"])
        previous_time = datetime.fromisoformat(str(previous_card_state["last_reviewed_at"]))
    except (KeyError, TypeError, ValueError):
        return None
    if (
        not math.isfinite(stability)
        or stability <= 0.0
        or previous_time.tzinfo is None
        or graded_at.tzinfo is None
    ):
        return None
    delay_days = (graded_at - previous_time).total_seconds() / 86_400.0
    if not math.isfinite(delay_days) or delay_days < MIN_DELAY_DAYS:
        return None
    normalized_delay = delay_days / stability
    success = grade >= 2
    selected = _select_model(calibration, mode)
    if selected is None:
        source = "prior"
        prediction_model = calibration["models"][POOLED_MODEL]
    else:
        source, prediction_model = selected
    prediction = posterior_predictive_success(prediction_model, normalized_delay)
    _observe_model(calibration["models"][POOLED_MODEL], normalized_delay, success, graded_at)
    _observe_model(calibration["models"][mode], normalized_delay, success, graded_at)
    return {
        "model": "discounted-bayesian-half-life-v1",
        "mode": mode,
        "source": source,
        "delay_days": round(delay_days, 6),
        "normalized_delay": round(normalized_delay, 6),
        "predicted_good_or_easy": round(prediction, 6),
        "good_or_easy": success,
    }


def model_is_ready(model: dict[str, Any]) -> bool:
    return (
        model["observations"] >= MIN_RAW_OBSERVATIONS
        and model["effective_observations"] >= MIN_EFFECTIVE_OBSERVATIONS
        and model["effective_exposure"] >= MIN_EFFECTIVE_EXPOSURE
    )


def _select_model(calibration: dict[str, Any], mode: str) -> tuple[str, dict[str, Any]] | None:
    mode_model = calibration["models"].get(mode)
    if mode_model is not None and model_is_ready(mode_model):
        return mode, mode_model
    pooled = calibration["models"][POOLED_MODEL]
    if model_is_ready(pooled):
        return POOLED_MODEL, pooled
    return None


def _posterior_interval_factor(model: dict[str, Any]) -> tuple[float, str | None]:
    lower = MIN_SCHEDULE_FACTOR
    upper = MAX_SCHEDULE_FACTOR
    if posterior_predictive_success(model, lower) <= TARGET_SUCCESS:
        return lower, "shorter"
    if posterior_predictive_success(model, upper) >= TARGET_SUCCESS:
        return upper, "longer"
    for _ in range(48):
        middle = (lower + upper) / 2.0
        if posterior_predictive_success(model, middle) >= TARGET_SUCCESS:
            lower = middle
        else:
            upper = middle
    return (lower + upper) / 2.0, None


def schedule_interval(
    calibration: dict[str, Any], mode: str, stability_days: float, minimum_days: int
) -> tuple[int, dict[str, Any]]:
    selected = _select_model(calibration, mode)
    source = "fallback"
    factor = 1.0
    bounded_direction = None
    model = calibration["models"].get(mode, calibration["models"][POOLED_MODEL])
    if selected is not None:
        source, model = selected
        factor, bounded_direction = _posterior_interval_factor(model)
    interval = max(minimum_days, min(MAX_INTERVAL_DAYS, round(stability_days * factor)))
    return interval, {
        "model": "discounted-bayesian-half-life-v1",
        "target_grade": "good-or-easy",
        "target_probability": TARGET_SUCCESS,
        "calibrated": selected is not None,
        "source": source,
        "observations": model["observations"],
        "effective_observations": round(model["effective_observations"], 3),
        "interval_factor": round(factor, 4),
        "interval_days": interval,
        "bounded_direction": bounded_direction,
    }


def calibration_summary(calibration: dict[str, Any]) -> dict[str, Any]:
    models: dict[str, Any] = {}
    for key in MODEL_KEYS:
        model = calibration["models"][key]
        models[key] = {
            "observations": model["observations"],
            "successes": model["successes"],
            "effective_observations": round(model["effective_observations"], 3),
            "effective_exposure": round(model["effective_exposure"], 3),
            "ready": model_is_ready(model),
        }
    return {
        "model": "discounted-bayesian-half-life-v1",
        "target_grade": "good-or-easy",
        "target_probability": TARGET_SUCCESS,
        "minimum_observations": MIN_RAW_OBSERVATIONS,
        "minimum_delay_hours": int(MIN_DELAY_DAYS * 24),
        "models": models,
    }
