"""Pure rules for deciding when automatic AI assistance is needed."""

from math import isfinite
from typing import Mapping

from services.situation_service import calculate_vehicle_angle, decide_guidance_category


SENSOR_CHANGE_THRESHOLD_CM = 10.0
LLM_COOLDOWN_SECONDS = 8.0
SENSOR_DIRECTIONS = ("left", "center", "right")


def sensor_snapshot_from_situation(situation: Mapping[str, object]) -> dict[str, object]:
    readings = situation.get("sensor_readings")
    readings_by_direction = readings if isinstance(readings, Mapping) else {}

    snapshot: dict[str, object] = {}
    for direction in SENSOR_DIRECTIONS:
        reading = readings_by_direction.get(direction)
        snapshot[direction] = reading.get("distance") if isinstance(reading, Mapping) else None

    return snapshot


def objective_condition_from_situation(situation: Mapping[str, object]) -> dict[str, object]:
    snapshot = sensor_snapshot_from_situation(situation)
    return {
        "nearest_direction": situation.get("nearest_direction"),
        "nearest_distance": situation.get("nearest_distance"),
        "overall_status": situation.get("overall_status"),
        "angle_deg": calculate_vehicle_angle(snapshot["left"], snapshot["right"]),
    }


def _distance(value: object) -> float | None:
    if isinstance(value, bool):
        return None

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return None

    if not isfinite(numeric_value) or numeric_value < 0:
        return None

    return numeric_value


def has_complete_sensor_snapshot(snapshot: Mapping[str, object]) -> bool:
    return all(_distance(snapshot.get(direction)) is not None for direction in SENSOR_DIRECTIONS)


def _guidance_category(
    snapshot: Mapping[str, object],
    condition: Mapping[str, object],
) -> str | None:
    left = _distance(snapshot.get("left"))
    center = _distance(snapshot.get("center"))
    right = _distance(snapshot.get("right"))
    if left is None or center is None or right is None:
        return None

    angle_deg = condition.get("angle_deg")
    return decide_guidance_category(
        left,
        center,
        right,
        angle_deg if isinstance(angle_deg, (int, float)) else None,
    )


def has_significant_change(
    current_snapshot: Mapping[str, object],
    current_condition: Mapping[str, object],
    previous_snapshot: Mapping[str, object] | None,
    previous_condition: Mapping[str, object] | None,
) -> bool:
    """Compare latest objective readings against the AI response snapshot."""
    if not isinstance(previous_snapshot, Mapping) or not isinstance(previous_condition, Mapping):
        return True

    if current_condition.get("overall_status") != previous_condition.get("overall_status"):
        return True

    if current_condition.get("nearest_direction") != previous_condition.get("nearest_direction"):
        return True

    # Distances can shift under the per-sensor threshold on both sides at once
    # (e.g. left/right swapping which one is closer), flipping which way the
    # driver should steer without tripping any of the checks above.
    if _guidance_category(current_snapshot, current_condition) != _guidance_category(
        previous_snapshot, previous_condition
    ):
        return True

    for direction in SENSOR_DIRECTIONS:
        current_distance = _distance(current_snapshot.get(direction))
        previous_distance = _distance(previous_snapshot.get(direction))
        if current_distance is None or previous_distance is None:
            continue

        if abs(current_distance - previous_distance) >= SENSOR_CHANGE_THRESHOLD_CM:
            return True

    return False


def cooldown_elapsed(
    last_request_time: object,
    now: float,
    cooldown_seconds: float = LLM_COOLDOWN_SECONDS,
) -> bool:
    if not isinstance(last_request_time, (int, float)):
        return True

    return now - float(last_request_time) >= cooldown_seconds


def should_generate_assistance(
    current_snapshot: Mapping[str, object],
    current_condition: Mapping[str, object],
    previous_snapshot: Mapping[str, object] | None,
    previous_condition: Mapping[str, object] | None,
    last_request_time: object,
    now: float,
) -> bool:
    if not has_complete_sensor_snapshot(current_snapshot):
        return False

    if not cooldown_elapsed(last_request_time, now):
        return False

    return has_significant_change(
        current_snapshot,
        current_condition,
        previous_snapshot,
        previous_condition,
    )
