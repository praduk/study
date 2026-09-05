from __future__ import annotations

import math
from datetime import datetime
from typing import Any

# The model predicts the learner's probability of assigning Good or Easy.  At
# the neutral interval scale (1.0), the prior curve reaches the scheduling
# target when elapsed time equals the card's current stability.
CALIBRATION_VERSION = 2
CALIBRATION_MODEL = "discounted-bayesian-self-grade-v2"
V1_CALIBRATION_MODEL = "discounted-bayesian-retention-v1"
LEGACY_CALIBRATION_MODEL = "discounted-bayesian-half-life-v1"
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
MAX_NORMALIZED_DELAY = 64.0
MIN_RAW_OBSERVATIONS = 24
MIN_EFFECTIVE_OBSERVATIONS = 20.0
MIN_EFFECTIVE_EXPOSURE = 12.0
MIN_DISTINCT_CARDS = 8
MAX_POSTERIOR_LOG_SCALE_SD = 0.65
MAX_BOUNDARY_MASS = 0.05
MIN_SCHEDULE_FACTOR = 0.50
MAX_SCHEDULE_FACTOR = 2.00
MAX_INTERVAL_DAYS = 3650
FORECAST_BIN_COUNT = 10
FORECAST_LOG_EPSILON = 1e-15


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
        "observed_card_ids": [],
        "last_observed_at": None,
    }


def new_forecast_evaluation() -> dict[str, Any]:
    return {
        "count": 0,
        "brier_sum": 0.0,
        "log_loss_sum": 0.0,
        "bins": [
            {
                "count": 0,
                "predicted_sum": 0.0,
                "successes": 0,
            }
            for _ in range(FORECAST_BIN_COUNT)
        ],
    }


def new_calibration_state() -> dict[str, Any]:
    return {
        "version": CALIBRATION_VERSION,
        "target_grade": "good-or-easy",
        "target_probability": TARGET_SUCCESS,
        "history_discount": HISTORY_DISCOUNT,
        "processed_log_records": 0,
        "last_log_attempt_id": None,
        "processed_log_digest": None,
        "models": {key: new_model_state() for key in MODEL_KEYS},
        "forecast_evaluation": new_forecast_evaluation(),
    }


def _finite_number(value: Any, name: str, *, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} is not numeric")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} is outside its valid range") from exc
    if not math.isfinite(result) or result < minimum:
        raise ValueError(f"{name} is outside its valid range")
    return result


def _validate_forecast_evaluation(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError("forecast evaluation is missing")
    count = value.get("count")
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError("forecast evaluation count is invalid")
    brier_sum = _finite_number(value.get("brier_sum"), "forecast Brier sum")
    log_loss_sum = _finite_number(value.get("log_loss_sum"), "forecast log-loss sum")
    if brier_sum > count + 1e-12:
        raise ValueError("forecast Brier sum is inconsistent")
    bins = value.get("bins")
    if not isinstance(bins, list) or len(bins) != FORECAST_BIN_COUNT:
        raise ValueError("forecast reliability bins are invalid")
    checked_bins: list[dict[str, Any]] = []
    binned_count = 0
    binned_brier_inputs = 0.0
    for index, item in enumerate(bins):
        if not isinstance(item, dict):
            raise TypeError(f"forecast reliability bin {index} is invalid")
        bin_count = item.get("count")
        successes = item.get("successes")
        if isinstance(bin_count, bool) or not isinstance(bin_count, int) or bin_count < 0:
            raise ValueError(f"forecast reliability bin {index} count is invalid")
        if (
            isinstance(successes, bool)
            or not isinstance(successes, int)
            or successes < 0
            or successes > bin_count
        ):
            raise ValueError(f"forecast reliability bin {index} successes are invalid")
        predicted_sum = _finite_number(
            item.get("predicted_sum"), f"forecast reliability bin {index} prediction sum"
        )
        lower = index / FORECAST_BIN_COUNT
        upper = (index + 1) / FORECAST_BIN_COUNT
        if predicted_sum < lower * bin_count - 1e-12:
            raise ValueError(f"forecast reliability bin {index} predictions are invalid")
        if predicted_sum > upper * bin_count + 1e-12:
            raise ValueError(f"forecast reliability bin {index} predictions are invalid")
        checked_bins.append(
            {
                "count": bin_count,
                "predicted_sum": predicted_sum,
                "successes": successes,
            }
        )
        binned_count += bin_count
        binned_brier_inputs += predicted_sum
    if binned_count != count:
        raise ValueError("forecast reliability-bin count is inconsistent")
    if count == 0 and (brier_sum != 0.0 or log_loss_sum != 0.0 or binned_brier_inputs != 0.0):
        raise ValueError("empty forecast evaluation is inconsistent")
    return {
        "count": count,
        "brier_sum": brier_sum,
        "log_loss_sum": log_loss_sum,
        "bins": checked_bins,
    }


def validate_calibration_state(value: Any) -> dict[str, Any]:
    """Return a normalised copy of persisted calibration state or raise ValueError."""
    if (
        not isinstance(value, dict)
        or isinstance(value.get("version"), bool)
        or value.get("version") != CALIBRATION_VERSION
    ):
        raise ValueError("unsupported calibration state")
    models = value.get("models")
    if not isinstance(models, dict):
        raise TypeError("calibration models are missing")

    result = new_calibration_state()
    processed_log_records = value.get("processed_log_records")
    if (
        isinstance(processed_log_records, bool)
        or not isinstance(processed_log_records, int)
        or processed_log_records < 0
    ):
        raise ValueError("calibration log checkpoint is invalid")
    last_log_attempt_id = value.get("last_log_attempt_id")
    if last_log_attempt_id is not None and not isinstance(last_log_attempt_id, str):
        raise TypeError("calibration log checkpoint has an invalid attempt ID")
    if (processed_log_records == 0) != (last_log_attempt_id is None):
        raise ValueError("calibration log checkpoint is inconsistent")
    processed_log_digest = value.get("processed_log_digest")
    if processed_log_digest is not None and (
        not isinstance(processed_log_digest, str)
        or len(processed_log_digest) != 64
        or any(character not in "0123456789abcdef" for character in processed_log_digest)
    ):
        raise ValueError("calibration log checkpoint has an invalid digest")
    if (processed_log_records == 0) != (processed_log_digest is None):
        raise ValueError("calibration log checkpoint digest is inconsistent")
    result["processed_log_records"] = processed_log_records
    result["last_log_attempt_id"] = last_log_attempt_id
    result["processed_log_digest"] = processed_log_digest
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
        maximum_weight = max(numeric_weights)
        log_total = maximum_weight + math.log(
            sum(math.exp(item - maximum_weight) for item in numeric_weights)
        )
        if abs(log_total) > 1e-9:
            raise ValueError(f"calibration model {key} weights are not normalised")
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
        observed_card_ids = candidate.get("observed_card_ids")
        if not isinstance(observed_card_ids, list) or any(
            not isinstance(card_id, str) or not card_id for card_id in observed_card_ids
        ):
            raise ValueError(f"calibration model {key} has invalid observed cards")
        if len(set(observed_card_ids)) != len(observed_card_ids):
            raise ValueError(f"calibration model {key} repeats an observed card")
        if len(observed_card_ids) > observations:
            raise ValueError(f"calibration model {key} observed-card count is inconsistent")
        result["models"][key] = {
            # Validation must be idempotent. Re-normalising an already
            # normalised float vector creates tiny drift on every request.
            "log_weights": numeric_weights,
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
            "observed_card_ids": list(observed_card_ids),
            "last_observed_at": last_observed_at,
        }
    forecast_evaluation = _validate_forecast_evaluation(value.get("forecast_evaluation"))
    if forecast_evaluation["count"] > result["models"][POOLED_MODEL]["observations"]:
        raise ValueError("forecast evaluation count exceeds qualified observations")
    result["forecast_evaluation"] = forecast_evaluation
    return result


def success_probability(normalized_delay: float, interval_scale: float) -> float:
    """Probability of a Good/Easy grade after a delay measured in stability units."""
    exponent = -BASE_DECAY * max(0.0, normalized_delay) / interval_scale
    return RESPONSE_FLOOR + (1.0 - 2.0 * RESPONSE_FLOOR) * math.exp(exponent)


def _posterior_weights(model: dict[str, Any]) -> list[float]:
    return [math.exp(value) for value in model["log_weights"]]


def posterior_log_scale_sd(model: dict[str, Any]) -> float:
    weights = _posterior_weights(model)
    log_scales = [math.log(scale) for scale in INTERVAL_SCALE_GRID]
    mean = sum(weight * value for weight, value in zip(weights, log_scales, strict=True))
    variance = sum(
        weight * (value - mean) ** 2
        for weight, value in zip(weights, log_scales, strict=True)
    )
    return math.sqrt(max(0.0, variance))


def posterior_predictive_success(model: dict[str, Any], normalized_delay: float) -> float:
    return sum(
        weight * success_probability(normalized_delay, scale)
        for weight, scale in zip(_posterior_weights(model), INTERVAL_SCALE_GRID, strict=True)
    )


def posterior_interval_scale_summary(model: dict[str, Any]) -> dict[str, Any]:
    """Summarise the bounded interval-scale posterior without exposing its grid."""
    weights = _posterior_weights(model)

    def quantile(probability: float) -> float:
        cumulative = 0.0
        for weight, scale in zip(weights, INTERVAL_SCALE_GRID, strict=True):
            cumulative += weight
            if cumulative >= probability:
                return scale
        return INTERVAL_SCALE_GRID[-1]

    median = quantile(0.5)
    return {
        "median": round(median, 4),
        "credible_interval_90": {
            "lower": round(quantile(0.05), 4),
            "upper": round(quantile(0.95), 4),
        },
    }


def posterior_boundary_summary(model: dict[str, Any]) -> dict[str, Any]:
    weights = _posterior_weights(model)
    lower = weights[0]
    upper = weights[-1]
    return {
        "lower": round(lower, 6),
        "upper": round(upper, 6),
        "boundary_limited": lower >= MAX_BOUNDARY_MASS or upper >= MAX_BOUNDARY_MASS,
    }


def _observe_forecast(calibration: dict[str, Any], prediction: float, success: bool) -> None:
    evaluation = calibration["forecast_evaluation"]
    error = prediction - float(success)
    bounded_prediction = min(
        1.0 - FORECAST_LOG_EPSILON,
        max(FORECAST_LOG_EPSILON, prediction),
    )
    log_loss = (
        -math.log(bounded_prediction)
        if success
        else -math.log1p(-bounded_prediction)
    )
    evaluation["count"] += 1
    evaluation["brier_sum"] += error * error
    evaluation["log_loss_sum"] += log_loss
    bin_index = min(FORECAST_BIN_COUNT - 1, int(prediction * FORECAST_BIN_COUNT))
    bucket = evaluation["bins"][bin_index]
    bucket["count"] += 1
    bucket["predicted_sum"] += prediction
    bucket["successes"] += int(success)


def _observe_model(
    model: dict[str, Any],
    normalized_delay: float,
    success: bool,
    observed_at: datetime,
    card_id: str,
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
    if card_id not in model["observed_card_ids"]:
        model["observed_card_ids"].append(card_id)
    model["last_observed_at"] = observed_at.isoformat()


def observe_review(
    calibration: dict[str, Any],
    mode: str,
    previous_card_state: dict[str, Any],
    observed_at: datetime,
    grade: int,
    *,
    card_id: str,
    evaluate_forecast: bool = True,
) -> dict[str, Any] | None:
    """Update pooled and task-specific posteriors from one genuinely delayed review."""
    if not isinstance(card_id, str) or not card_id:
        raise ValueError("calibration observation card is invalid")
    if mode not in CALIBRATED_MODES:
        return None
    try:
        stability = float(previous_card_state["stability_days"])
        previous_time = datetime.fromisoformat(str(previous_card_state["last_reviewed_at"]))
    except (KeyError, TypeError, ValueError, OverflowError):
        return None
    if (
        not math.isfinite(stability)
        or stability <= 0.0
        or previous_time.tzinfo is None
        or observed_at.tzinfo is None
    ):
        return None
    delay_days = (observed_at - previous_time).total_seconds() / 86_400.0
    if not math.isfinite(delay_days) or delay_days < MIN_DELAY_DAYS:
        return None
    normalized_delay = delay_days / stability
    if not math.isfinite(normalized_delay) or normalized_delay <= 0.0:
        return None
    delay_was_capped = normalized_delay > MAX_NORMALIZED_DELAY
    normalized_delay = min(normalized_delay, MAX_NORMALIZED_DELAY)
    success = grade >= 2
    selected = _select_model(calibration, mode)
    if selected is None:
        source = "pooled-collecting"
        prediction_model = calibration["models"][POOLED_MODEL]
    else:
        source, prediction_model = selected
    prediction = round(posterior_predictive_success(prediction_model, normalized_delay), 6)
    if evaluate_forecast:
        _observe_forecast(calibration, prediction, success)
    _observe_model(
        calibration["models"][POOLED_MODEL],
        normalized_delay,
        success,
        observed_at,
        card_id,
    )
    _observe_model(
        calibration["models"][mode],
        normalized_delay,
        success,
        observed_at,
        card_id,
    )
    return {
        "version": CALIBRATION_VERSION,
        "model": CALIBRATION_MODEL,
        "mode": mode,
        "card_id": card_id,
        "source": source,
        "delay_days": round(delay_days, 6),
        # This value is replayed as model evidence. Preserve full JSON float
        # precision rather than quantising the posterior's input.
        "normalized_delay": normalized_delay,
        "delay_was_capped": delay_was_capped,
        "predicted_good_or_easy": prediction,
        "good_or_easy": success,
    }


def validate_recorded_observation(
    value: Any, *, mode: str, grade: int
) -> tuple[int | None, float, float, bool, bool, float]:
    """Validate a versioned log observation and return its model inputs."""
    if not isinstance(value, dict):
        raise TypeError("calibration observation is not an object")
    version = value.get("version")
    if isinstance(version, bool) or version not in (None, 1, CALIBRATION_VERSION):
        raise ValueError("unsupported calibration observation")
    allowed_models = (
        {CALIBRATION_MODEL}
        if version == CALIBRATION_VERSION
        else {V1_CALIBRATION_MODEL}
        if version == 1
        else {LEGACY_CALIBRATION_MODEL}
    )
    if value.get("model") not in allowed_models or value.get("mode") != mode:
        raise ValueError("calibration observation does not match its review card")
    if mode not in CALIBRATED_MODES:
        raise ValueError("calibration observation has an unsupported review mode")
    recorded_normalized_delay = _finite_number(
        value.get("normalized_delay"), "calibration normalized delay"
    )
    if recorded_normalized_delay <= 0.0:
        raise ValueError("calibration normalized delay is outside its valid range")
    if version is None:
        normalized_delay = min(recorded_normalized_delay, MAX_NORMALIZED_DELAY)
    elif recorded_normalized_delay > MAX_NORMALIZED_DELAY:
        raise ValueError("calibration normalized delay is outside its valid range")
    else:
        normalized_delay = recorded_normalized_delay
    delay_days = _finite_number(value.get("delay_days"), "calibration delay")
    if delay_days < MIN_DELAY_DAYS:
        raise ValueError("calibration delay is too short")
    delay_was_capped = value.get("delay_was_capped")
    if version is None and delay_was_capped is None:
        delay_was_capped = recorded_normalized_delay > MAX_NORMALIZED_DELAY
    if not isinstance(delay_was_capped, bool):
        raise TypeError("calibration delay cap marker is invalid")
    if delay_was_capped and normalized_delay != MAX_NORMALIZED_DELAY:
        raise ValueError("calibration capped delay is inconsistent")
    if version is not None and not delay_was_capped and normalized_delay > MAX_NORMALIZED_DELAY:
        raise ValueError("calibration delay cap marker is inconsistent")
    prediction = _finite_number(
        value.get("predicted_good_or_easy"), "calibration prediction"
    )
    if prediction <= 0.0 or prediction >= 1.0:
        raise ValueError("calibration prediction is outside its valid range")
    success = value.get("good_or_easy")
    if not isinstance(success, bool) or success != (grade >= 2):
        raise ValueError("calibration outcome does not match its grade")
    return version, delay_days, normalized_delay, bool(delay_was_capped), success, prediction


def _validate_observation_history(
    *,
    version: int | None,
    delay_days: float,
    normalized_delay: float,
    delay_was_capped: bool,
    delay_cap_was_recorded: bool,
    observed_at: datetime,
    previous_card_state: dict[str, Any] | None,
) -> None:
    if previous_card_state is None:
        if version == CALIBRATION_VERSION:
            raise ValueError("v2 calibration observation has no previous schedule")
        return
    if not isinstance(previous_card_state, dict):
        raise TypeError("calibration observation has an invalid previous schedule")
    try:
        previous_stability = _finite_number(
            previous_card_state["stability_days"], "previous review stability"
        )
        previous_time = datetime.fromisoformat(
            str(previous_card_state["last_reviewed_at"])
        )
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError("calibration observation has an invalid previous schedule") from exc
    if previous_stability <= 0.0 or previous_time.tzinfo is None:
        raise ValueError("calibration observation has an invalid previous schedule")
    expected_delay_days = (observed_at - previous_time).total_seconds() / 86_400.0
    if not math.isfinite(expected_delay_days) or expected_delay_days < MIN_DELAY_DAYS:
        raise ValueError("calibration observation delay does not match its review history")
    expected_raw_normalized = expected_delay_days / previous_stability
    if not math.isfinite(expected_raw_normalized) or expected_raw_normalized <= 0.0:
        raise ValueError("calibration observation delay does not match its review history")
    expected_capped = expected_raw_normalized > MAX_NORMALIZED_DELAY
    expected_normalized = min(expected_raw_normalized, MAX_NORMALIZED_DELAY)
    if not math.isclose(delay_days, expected_delay_days, rel_tol=0.0, abs_tol=5.1e-7):
        raise ValueError("calibration observation delay does not match its review history")
    normalized_tolerance = 5.1e-7 if version is None else 1e-12
    if not math.isclose(
        normalized_delay,
        expected_normalized,
        rel_tol=1e-12,
        abs_tol=normalized_tolerance,
    ):
        raise ValueError("calibration normalized delay does not match its review history")
    if delay_cap_was_recorded and delay_was_capped != expected_capped:
        raise ValueError("calibration delay cap does not match its review history")


def apply_recorded_observation(
    calibration: dict[str, Any],
    value: Any,
    *,
    mode: str,
    grade: int,
    observed_at: datetime,
    card_id: str,
    previous_card_state: dict[str, Any] | None,
) -> None:
    """Replay an explicit observation without reconstructing it from card state."""
    if observed_at.tzinfo is None:
        raise ValueError("calibration observation timestamp has no timezone")
    if not isinstance(card_id, str) or not card_id:
        raise ValueError("calibration observation card is invalid")
    version, delay_days, normalized_delay, delay_was_capped, success, prediction = (
        validate_recorded_observation(value, mode=mode, grade=grade)
    )
    _validate_observation_history(
        version=version,
        delay_days=delay_days,
        normalized_delay=normalized_delay,
        delay_was_capped=delay_was_capped,
        delay_cap_was_recorded="delay_was_capped" in value,
        observed_at=observed_at,
        previous_card_state=previous_card_state,
    )
    if version == CALIBRATION_VERSION:
        if value.get("card_id") != card_id:
            raise ValueError("calibration observation does not match its review card")
        selected = _select_model(calibration, mode)
        if selected is None:
            expected_source = "pooled-collecting"
            prediction_model = calibration["models"][POOLED_MODEL]
        else:
            expected_source, prediction_model = selected
        expected_prediction = round(
            posterior_predictive_success(prediction_model, normalized_delay), 6
        )
        if value.get("source") != expected_source or not math.isclose(
            prediction,
            expected_prediction,
            rel_tol=0.0,
            abs_tol=5e-7,
        ):
            raise ValueError("calibration prediction does not match its prior model state")
    _observe_forecast(calibration, prediction, success)
    _observe_model(
        calibration["models"][POOLED_MODEL],
        normalized_delay,
        success,
        observed_at,
        card_id,
    )
    _observe_model(
        calibration["models"][mode],
        normalized_delay,
        success,
        observed_at,
        card_id,
    )


def model_is_ready(model: dict[str, Any]) -> bool:
    boundary = posterior_boundary_summary(model)
    return (
        model["observations"] >= MIN_RAW_OBSERVATIONS
        and model["effective_observations"] >= MIN_EFFECTIVE_OBSERVATIONS
        and model["effective_exposure"] >= MIN_EFFECTIVE_EXPOSURE
        and len(model["observed_card_ids"]) >= MIN_DISTINCT_CARDS
        and posterior_log_scale_sd(model) <= MAX_POSTERIOR_LOG_SCALE_SD
        and not boundary["boundary_limited"]
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
    stability_days = _finite_number(stability_days, "stability", minimum=0.0)
    if stability_days <= 0.0:
        raise ValueError("stability must be positive")
    if (
        isinstance(minimum_days, bool)
        or not isinstance(minimum_days, int)
        or minimum_days < 1
        or minimum_days > MAX_INTERVAL_DAYS
    ):
        raise ValueError("minimum interval is outside its valid range")
    selected = _select_model(calibration, mode)
    source = "fallback"
    factor = 1.0
    bounded_direction = None
    model = calibration["models"].get(mode, calibration["models"][POOLED_MODEL])
    if selected is not None:
        source, model = selected
        factor, bounded_direction = _posterior_interval_factor(model)
    if stability_days >= MAX_INTERVAL_DAYS / factor:
        interval = MAX_INTERVAL_DAYS
    else:
        interval = max(minimum_days, round(stability_days * factor))
    return interval, {
        "model": CALIBRATION_MODEL,
        "target_grade": "good-or-easy",
        "target_probability": TARGET_SUCCESS,
        "calibrated": selected is not None,
        "source": source,
        "observations": model["observations"],
        "distinct_cards": len(model["observed_card_ids"]),
        "effective_observations": round(model["effective_observations"], 3),
        "interval_factor": round(factor, 4),
        "interval_days": interval,
        "bounded_direction": bounded_direction,
        "target_attainable": bounded_direction is None if selected is not None else None,
    }


def _model_diagnostics(model: dict[str, Any]) -> dict[str, Any]:
    boundary = posterior_boundary_summary(model)
    suggested_factor, bounded_direction = _posterior_interval_factor(model)
    return {
        "distinct_cards": len(model["observed_card_ids"]),
        "posterior_log_scale_sd": round(posterior_log_scale_sd(model), 4),
        "posterior_interval_scale": posterior_interval_scale_summary(model),
        "posterior_boundary_mass": {
            "lower": boundary["lower"],
            "upper": boundary["upper"],
        },
        "boundary_limited": boundary["boundary_limited"],
        "suggested_interval_factor": round(suggested_factor, 4),
        "bounded_direction": bounded_direction,
        "target_attainable": bounded_direction is None,
    }


def forecast_evaluation_summary(calibration: dict[str, Any]) -> dict[str, Any]:
    evaluation = calibration["forecast_evaluation"]
    count = evaluation["count"]
    predicted_total = sum(bucket["predicted_sum"] for bucket in evaluation["bins"])
    successes = sum(bucket["successes"] for bucket in evaluation["bins"])
    bins: list[dict[str, Any]] = []
    for index, bucket in enumerate(evaluation["bins"]):
        bin_count = bucket["count"]
        bins.append(
            {
                "lower": round(index / FORECAST_BIN_COUNT, 1),
                "upper": round((index + 1) / FORECAST_BIN_COUNT, 1),
                "count": bin_count,
                "mean_predicted_good_or_easy": (
                    round(bucket["predicted_sum"] / bin_count, 6)
                    if bin_count
                    else None
                ),
                "observed_good_or_easy_self_grade_rate": (
                    round(bucket["successes"] / bin_count, 6) if bin_count else None
                ),
            }
        )
    return {
        "count": count,
        "brier_score": round(evaluation["brier_sum"] / count, 6) if count else None,
        "log_loss": round(evaluation["log_loss_sum"] / count, 6) if count else None,
        "mean_predicted_good_or_easy": (
            round(predicted_total / count, 6) if count else None
        ),
        "observed_good_or_easy_self_grade_rate": (
            round(successes / count, 6) if count else None
        ),
        "reliability_bins": bins,
        "interpretation": (
            "Scores evaluate compatible logged pre-outcome Good-or-Easy self-grade "
            "forecasts across model versions; they do not measure objective remembering, "
            "correctness, or mastery."
        ),
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
            **_model_diagnostics(model),
            "ready": model_is_ready(model),
        }
    return {
        "model": CALIBRATION_MODEL,
        "target_grade": "good-or-easy",
        "target_probability": TARGET_SUCCESS,
        "minimum_observations": MIN_RAW_OBSERVATIONS,
        "minimum_distinct_cards": MIN_DISTINCT_CARDS,
        "minimum_delay_hours": int(MIN_DELAY_DAYS * 24),
        "processed_log_records": calibration["processed_log_records"],
        "forecast_evaluation": forecast_evaluation_summary(calibration),
        "models": models,
    }


def reporting_model_estimate(
    calibration: dict[str, Any],
    mode: str,
    *,
    delay_days_now: float | None,
    normalized_delay_now: float | None,
    delay_days_at_due: float | None,
    normalized_delay_at_due: float | None,
) -> dict[str, Any]:
    """Return posterior diagnostics named for the self-grade outcome they model."""
    selected = _select_model(calibration, mode)
    if selected is None:
        source = "fallback"
        posterior_source = mode if mode in calibration["models"] else POOLED_MODEL
        model = calibration["models"][posterior_source]
    else:
        source, model = selected
        posterior_source = source

    def prediction(
        delay_days: float | None, normalized_delay: float | None
    ) -> tuple[float | None, str]:
        if delay_days is None or normalized_delay is None:
            return None, "unavailable"
        checked_delay = _finite_number(delay_days, "delay")
        checked_normalized = _finite_number(normalized_delay, "normalized delay")
        if checked_delay < MIN_DELAY_DAYS:
            return None, "short-delay-excluded"
        if checked_normalized > MAX_NORMALIZED_DELAY:
            return None, "beyond-model-range"
        return round(posterior_predictive_success(model, checked_normalized), 6), "available"

    prediction_now, status_now = prediction(delay_days_now, normalized_delay_now)
    prediction_at_due, status_at_due = prediction(
        delay_days_at_due, normalized_delay_at_due
    )
    diagnostics = _model_diagnostics(model)

    return {
        "model": CALIBRATION_MODEL,
        "target_grade": "good-or-easy",
        "source": source,
        "posterior_source": posterior_source,
        "ready": selected is not None,
        "collecting": selected is None,
        "observations": model["observations"],
        **diagnostics,
        "prediction_domain": {
            "minimum_delay_days": MIN_DELAY_DAYS,
            "minimum_delay_hours": int(MIN_DELAY_DAYS * 24),
            "maximum_normalized_delay": MAX_NORMALIZED_DELAY,
        },
        "predicted_good_or_easy_now": prediction_now,
        "prediction_status_now": status_now,
        "predicted_good_or_easy_at_due": prediction_at_due,
        "prediction_status_at_due": status_at_due,
    }


def calibration_reporting_summary(calibration: dict[str, Any]) -> dict[str, Any]:
    """Return bounded Bayesian diagnostics for reporting, without posterior weights."""
    models: dict[str, Any] = {}
    for key in MODEL_KEYS:
        model = calibration["models"][key]
        observations = model["observations"]
        successes = model["successes"]
        models[key] = {
            "observations": observations,
            "good_or_easy_self_grades": successes,
            "good_or_easy_self_grade_rate": (
                round(successes / observations, 6) if observations else None
            ),
            "effective_observations": round(model["effective_observations"], 3),
            "effective_good_or_easy_self_grades": round(
                model["effective_successes"], 3
            ),
            "effective_exposure": round(model["effective_exposure"], 3),
            **_model_diagnostics(model),
            "last_observed_at": model["last_observed_at"],
            "ready": model_is_ready(model),
        }
    return {
        "model": CALIBRATION_MODEL,
        "target_grade": "good-or-easy",
        "target_probability": TARGET_SUCCESS,
        "observation_scope": (
            "Repeat retrievals started at least six hours after the prior review completed."
        ),
        "history_discount": HISTORY_DISCOUNT,
        "processed_log_records": calibration["processed_log_records"],
        "readiness_requirements": {
            "minimum_observations": MIN_RAW_OBSERVATIONS,
            "minimum_effective_observations": MIN_EFFECTIVE_OBSERVATIONS,
            "minimum_effective_exposure": MIN_EFFECTIVE_EXPOSURE,
            "minimum_distinct_cards": MIN_DISTINCT_CARDS,
            "maximum_posterior_log_scale_sd": MAX_POSTERIOR_LOG_SCALE_SD,
            "maximum_boundary_mass": MAX_BOUNDARY_MASS,
            "minimum_observation_delay_hours": int(MIN_DELAY_DAYS * 24),
        },
        "interpretation": (
            "Posterior predictions estimate Good-or-Easy self-grades; "
            "they are not correctness or mastery estimates."
        ),
        "forecast_evaluation": forecast_evaluation_summary(calibration),
        "models": models,
    }
