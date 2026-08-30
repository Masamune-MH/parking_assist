import unittest

from services.assistance_service import (
    LLM_COOLDOWN_SECONDS,
    has_significant_change,
    should_generate_assistance,
)


BASELINE_SNAPSHOT = {"left": 66, "center": 64, "right": 66}
BASELINE_CONDITION = {
    "nearest_direction": "center",
    "nearest_distance": 64,
    "overall_status": "safe",
}


class AssistanceServiceTests(unittest.TestCase):
    def test_first_complete_snapshot_requests_assistance(self) -> None:
        self.assertTrue(
            should_generate_assistance(
                BASELINE_SNAPSHOT,
                BASELINE_CONDITION,
                None,
                None,
                None,
                now=100,
            )
        )

    def test_small_sensor_fluctuation_is_not_significant(self) -> None:
        self.assertFalse(
            has_significant_change(
                {"left": 70, "center": 64, "right": 66},
                BASELINE_CONDITION,
                BASELINE_SNAPSHOT,
                BASELINE_CONDITION,
            )
        )

    def test_sensor_change_at_ten_centimetres_is_significant(self) -> None:
        self.assertTrue(
            has_significant_change(
                {"left": 76, "center": 64, "right": 66},
                BASELINE_CONDITION,
                BASELINE_SNAPSHOT,
                BASELINE_CONDITION,
            )
        )

    def test_risk_or_nearest_side_change_is_significant(self) -> None:
        self.assertTrue(
            has_significant_change(
                {"left": 66, "center": 15, "right": 66},
                {
                    "nearest_direction": "center",
                    "nearest_distance": 15,
                    "overall_status": "warning",
                },
                BASELINE_SNAPSHOT,
                BASELINE_CONDITION,
            )
        )
        self.assertTrue(
            has_significant_change(
                {"left": 50, "center": 64, "right": 66},
                {
                    "nearest_direction": "left",
                    "nearest_distance": 50,
                    "overall_status": "safe",
                },
                BASELINE_SNAPSHOT,
                BASELINE_CONDITION,
            )
        )

    def test_cooldown_blocks_significant_change_until_eight_seconds(self) -> None:
        changed_snapshot = {"left": 76, "center": 64, "right": 66}

        self.assertFalse(
            should_generate_assistance(
                changed_snapshot,
                BASELINE_CONDITION,
                BASELINE_SNAPSHOT,
                BASELINE_CONDITION,
                last_request_time=100,
                now=100 + LLM_COOLDOWN_SECONDS - 0.1,
            )
        )
        self.assertTrue(
            should_generate_assistance(
                changed_snapshot,
                BASELINE_CONDITION,
                BASELINE_SNAPSHOT,
                BASELINE_CONDITION,
                last_request_time=100,
                now=100 + LLM_COOLDOWN_SECONDS,
            )
        )

    def test_incomplete_firebase_reading_defers_assistance(self) -> None:
        self.assertFalse(
            should_generate_assistance(
                {"left": 66, "center": None, "right": 66},
                BASELINE_CONDITION,
                None,
                None,
                None,
                now=100,
            )
        )


if __name__ == "__main__":
    unittest.main()
