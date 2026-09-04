import unittest

from services.situation_service import (
    analyze_situation,
    decide_guidance_category,
    get_current_situation,
    get_sensor_status,
)


class SituationServiceTests(unittest.TestCase):
    def test_critical_nearest_sensor(self) -> None:
        result = get_current_situation(
            {"Left": 120, "Center": 85, "Right": 8},
            "English",
        )

        self.assertEqual(result["nearest_direction"], "right")
        self.assertEqual(result["nearest_distance"], 8)
        self.assertEqual(result["overall_status"], "critical")
        self.assertEqual(
            result["current_situation"],
            "Critical obstacle proximity detected on the right side at 8 cm.",
        )

    def test_warning_nearest_sensor(self) -> None:
        result = analyze_situation({"Left": 15, "Center": 60, "Right": 90})

        self.assertEqual(result["nearest_direction"], "left")
        self.assertEqual(result["nearest_distance"], 15)
        self.assertEqual(result["overall_status"], "warning")
        self.assertEqual(result["sensor_readings"]["left"]["status"], "warning")

    def test_safe_readings(self) -> None:
        result = get_current_situation(
            {"Left": 40, "Center": 50, "Right": 70},
            "Tiếng Việt",
        )

        self.assertEqual(result["overall_status"], "safe")
        self.assertIn("an toàn", result["current_situation"])

    def test_threshold_boundaries(self) -> None:
        self.assertEqual(get_sensor_status(10), "critical")
        self.assertEqual(get_sensor_status(11), "warning")
        self.assertEqual(get_sensor_status(20), "warning")
        self.assertEqual(get_sensor_status(21), "safe")

    def test_invalid_readings_are_unavailable(self) -> None:
        result = get_current_situation(
            {"Left": None, "Center": "invalid", "Right": 8},
            "Japanese",
        )

        self.assertEqual(result["sensor_readings"]["left"]["status"], "unknown")
        self.assertEqual(result["sensor_readings"]["center"]["status"], "unknown")
        self.assertEqual(result["nearest_direction"], "right")
        self.assertEqual(result["overall_status"], "critical")


class GuidanceCategoryTests(unittest.TestCase):
    def test_critical_distance_beats_everything(self) -> None:
        self.assertEqual(decide_guidance_category(9, 50, 50, angle_deg=None), "stop")
        self.assertEqual(decide_guidance_category(50, 9, 50, angle_deg=30), "stop")

    def test_small_tilt_is_treated_as_straight(self) -> None:
        self.assertEqual(
            decide_guidance_category(40, 40, 40, angle_deg=None), "continue_straight"
        )
        self.assertEqual(
            decide_guidance_category(40, 40, 40, angle_deg=4.9), "continue_straight"
        )
        self.assertEqual(
            decide_guidance_category(40, 40, 40, angle_deg=-4.9), "continue_straight"
        )

    def test_moderate_tilt_gives_minor_steering(self) -> None:
        self.assertEqual(decide_guidance_category(40, 40, 40, angle_deg=6), "steer_left")
        self.assertEqual(decide_guidance_category(40, 40, 40, angle_deg=-6), "steer_right")

    def test_large_tilt_with_room_stays_minor_steering(self) -> None:
        # Angle is large but the near side (right, since angle > 0) still has
        # plenty of clearance, so steering alone is still workable.
        self.assertEqual(
            decide_guidance_category(80, 40, 40, angle_deg=20), "steer_left"
        )

    def test_large_tilt_with_tight_clearance_needs_correction(self) -> None:
        self.assertEqual(
            decide_guidance_category(80, 40, 12, angle_deg=20), "correction_maneuver"
        )
        self.assertEqual(
            decide_guidance_category(12, 40, 80, angle_deg=-20), "correction_maneuver"
        )


if __name__ == "__main__":
    unittest.main()
