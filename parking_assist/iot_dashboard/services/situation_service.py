"""Deterministic sensor analysis for the Current Situation card."""

from math import atan2, degrees, isfinite
from typing import Mapping

from config.languages import get_angle_template, get_direction_label, get_situation_template


SENSOR_DIRECTIONS = ("left", "center", "right")
CRITICAL_DISTANCE_CM = 10
WARNING_DISTANCE_CM = 20

# Straight-line spacing between the left and right ultrasonic sensors,
# measured on the physical rig (2 x 21.5cm between adjacent sensors).
SENSOR_BASELINE_CM = 43.0

# Below this tilt, the vehicle is treated as parallel to the obstacle.
ANGLE_STRAIGHT_THRESHOLD_DEG = 3.0

# Thresholds for the deterministic driving-guidance decision.
GUIDANCE_STOP_DISTANCE_CM = 10
GUIDANCE_MINOR_ANGLE_DEG = 5
GUIDANCE_CORRECTION_ANGLE_DEG = 15
GUIDANCE_CORRECTION_NEAR_DISTANCE_CM = 15

GUIDANCE_STOP = "stop"
GUIDANCE_CORRECTION_MANEUVER = "correction_maneuver"
GUIDANCE_STEER_LEFT = "steer_left"
GUIDANCE_STEER_RIGHT = "steer_right"
GUIDANCE_CONTINUE_STRAIGHT = "continue_straight"

_STATUS_PRIORITY = {
    "unknown": 0,
    "safe": 1,
    "warning": 2,
    "critical": 3,
}


def normalize_distance(value: object) -> int | float | None:
    """Return a valid non-negative distance in centimetres, if available."""
    if isinstance(value, bool):
        return None

    try:
        distance = float(value)
    except (TypeError, ValueError):
        return None

    if not isfinite(distance) or distance < 0:
        return None

    return int(distance) if distance.is_integer() else distance


def format_distance(distance: int | float | None) -> str:
    if distance is None:
        return "--"

    numeric_distance = float(distance)
    if numeric_distance.is_integer():
        return str(int(numeric_distance))

    return f"{numeric_distance:.1f}"


def get_sensor_status(distance: object) -> str:
    """Apply the single source of truth for sensor risk thresholds."""
    normalized_distance = normalize_distance(distance)
    if normalized_distance is None:
        return "unknown"

    if normalized_distance <= CRITICAL_DISTANCE_CM:
        return "critical"

    if normalized_distance <= WARNING_DISTANCE_CM:
        return "warning"

    return "safe"


def _sensor_value(sensor_values: Mapping[str, object], direction: str) -> object:
    if direction in sensor_values:
        return sensor_values[direction]

    title_case_direction = direction.title()
    if title_case_direction in sensor_values:
        return sensor_values[title_case_direction]

    for key, value in sensor_values.items():
        if isinstance(key, str) and key.casefold() == direction:
            return value

    return None


def analyze_situation(sensor_values: Mapping[str, object] | None) -> dict[str, object]:
    """Return objective data only; this function performs no network or LLM calls."""
    readings_source = sensor_values if isinstance(sensor_values, Mapping) else {}
    sensor_readings: dict[str, dict[str, int | float | str | None]] = {}

    for direction in SENSOR_DIRECTIONS:
        distance = normalize_distance(_sensor_value(readings_source, direction))
        sensor_readings[direction] = {
            "distance": distance,
            "status": get_sensor_status(distance),
        }

    valid_readings = [
        (direction, reading)
        for direction, reading in sensor_readings.items()
        if reading["distance"] is not None
    ]

    if not valid_readings:
        objective_condition = {
            "direction": None,
            "distance": None,
            "status": "unknown",
        }
    else:
        nearest_direction, nearest_reading = min(
            valid_readings,
            key=lambda item: float(item[1]["distance"]),
        )
        overall_status = max(
            (str(reading["status"]) for _, reading in valid_readings),
            key=lambda status: _STATUS_PRIORITY[status],
        )
        objective_condition = {
            "direction": nearest_direction,
            "distance": nearest_reading["distance"],
            "status": overall_status,
        }

    return {
        "sensor_readings": sensor_readings,
        "objective_condition": objective_condition,
        "nearest_direction": objective_condition["direction"],
        "nearest_distance": objective_condition["distance"],
        "overall_status": objective_condition["status"],
    }


def format_current_situation(
    objective_condition: Mapping[str, object],
    language: str | None,
) -> str:
    """Format objective analysis through the local language configuration."""
    status = str(objective_condition.get("status", "unknown"))
    direction = objective_condition.get("direction")
    distance = objective_condition.get("distance")

    if status == "unknown" or not isinstance(direction, str) or distance is None:
        return get_situation_template(language, "unavailable")

    return get_situation_template(language, status).format(
        direction=get_direction_label(language, direction),
        distance=format_distance(normalize_distance(distance)),
    )


def get_current_situation(
    sensor_values: Mapping[str, object] | None,
    language: str | None,
) -> dict[str, object]:
    """Combine objective sensor analysis with its localized display text."""
    situation = analyze_situation(sensor_values)
    situation["current_situation"] = format_current_situation(
        situation["objective_condition"],
        language,
    )
    return situation


def calculate_vehicle_angle(
    left: int | float | None,
    right: int | float | None,
) -> float | None:
    """Estimate the vehicle's tilt, in degrees, relative to the surface behind it.

    Positive angle: the right side is closer to the obstacle (steer left to
    straighten out). Negative angle: the left side is closer (steer right).
    Assumes a flat surface behind the car and sensors aimed straight back.
    """
    if left is None or right is None:
        return None

    return degrees(atan2(left - right, SENSOR_BASELINE_CM))


def format_vehicle_angle(
    left: int | float | None,
    right: int | float | None,
    language: str | None,
) -> dict[str, object]:
    """Combine the angle estimate with its localized display text."""
    angle = calculate_vehicle_angle(left, right)

    if angle is None:
        return {
            "angle": None,
            "text": get_angle_template(language, "unavailable"),
        }

    if abs(angle) < ANGLE_STRAIGHT_THRESHOLD_DEG:
        text = get_angle_template(language, "straight")
    elif angle > 0:
        text = get_angle_template(language, "tilted_right").format(
            angle=f"{abs(angle):.1f}"
        )
    else:
        text = get_angle_template(language, "tilted_left").format(
            angle=f"{abs(angle):.1f}"
        )

    return {"angle": round(angle, 1), "text": text}


def get_vehicle_angle(
    sensor_values: Mapping[str, object] | None,
    language: str | None,
) -> dict[str, object]:
    """Read left/right sensor values and return the angle estimate + display text."""
    readings_source = sensor_values if isinstance(sensor_values, Mapping) else {}
    left = normalize_distance(_sensor_value(readings_source, "left"))
    right = normalize_distance(_sensor_value(readings_source, "right"))
    return format_vehicle_angle(left, right, language)


def decide_guidance_category(
    left: float,
    center: float,
    right: float,
    angle_deg: float | None,
) -> str:
    """Deterministically pick which driving instruction applies right now.

    This is the single source of truth for *what* to tell the driver; the LLM
    is only responsible for phrasing the chosen category naturally, not for
    re-deriving it from the raw numbers.
    """
    if min(left, center, right) < GUIDANCE_STOP_DISTANCE_CM:
        return GUIDANCE_STOP

    if angle_deg is not None and abs(angle_deg) >= GUIDANCE_CORRECTION_ANGLE_DEG:
        near_side_distance = right if angle_deg > 0 else left
        if near_side_distance < GUIDANCE_CORRECTION_NEAR_DISTANCE_CM:
            return GUIDANCE_CORRECTION_MANEUVER

    if angle_deg is not None and angle_deg >= GUIDANCE_MINOR_ANGLE_DEG:
        return GUIDANCE_STEER_LEFT

    if angle_deg is not None and angle_deg <= -GUIDANCE_MINOR_ANGLE_DEG:
        return GUIDANCE_STEER_RIGHT

    return GUIDANCE_CONTINUE_STRAIGHT
