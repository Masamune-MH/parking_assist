import unittest

from services.situation_service import (
    analyze_situation,
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
            "English",
        )

        self.assertEqual(result["overall_status"], "safe")
        self.assertIn("All available obstacle-distance readings are safe.", result["current_situation"])

    def test_threshold_boundaries(self) -> None:
        self.assertEqual(get_sensor_status(10), "critical")
        self.assertEqual(get_sensor_status(11), "warning")
        self.assertEqual(get_sensor_status(20), "warning")
        self.assertEqual(get_sensor_status(21), "safe")

    def test_invalid_readings_are_unavailable(self) -> None:
        result = get_current_situation(
            {"Left": None, "Center": "invalid", "Right": 8},
            "English",
        )

        self.assertEqual(result["sensor_readings"]["left"]["status"], "unknown")
        self.assertEqual(result["sensor_readings"]["center"]["status"], "unknown")
        self.assertEqual(result["nearest_direction"], "right")
        self.assertEqual(result["overall_status"], "critical")


if __name__ == "__main__":
    unittest.main()
