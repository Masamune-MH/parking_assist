import unittest
from unittest.mock import patch

import app


class AiRequestFlowTests(unittest.TestCase):
    @patch("app.get_parking_guidance", return_value="Reverse slowly.")
    def test_request_uses_the_supplied_live_snapshot_once(
        self,
        get_parking_guidance,
    ) -> None:
        sensor_snapshot = {"left": 50, "center": 18, "right": 9}
        objective_condition = {
            "nearest_direction": "right",
            "nearest_distance": 9,
            "overall_status": "critical",
        }
        result = app.request_ai_suggestion(
            sensor_snapshot,
            objective_condition,
            "English",
        )

        self.assertEqual(result, "Reverse slowly.")
        get_parking_guidance.assert_called_once_with(
            sensor_snapshot,
            objective_condition,
            language="English",
        )

    @patch("app.get_parking_guidance", return_value="Use the new reading.")
    def test_request_does_not_read_firebase_again(
        self,
        get_parking_guidance,
    ) -> None:
        first_snapshot = {"left": 60, "center": 40, "right": 14}
        second_snapshot = {"left": 60, "center": 40, "right": 7}
        first_condition = {
            "nearest_direction": "right",
            "nearest_distance": 14,
            "overall_status": "warning",
        }
        second_condition = {
            "nearest_direction": "right",
            "nearest_distance": 7,
            "overall_status": "critical",
        }

        app.request_ai_suggestion(first_snapshot, first_condition, "English")
        app.request_ai_suggestion(second_snapshot, second_condition, "English")

        self.assertEqual(get_parking_guidance.call_count, 2)
        self.assertEqual(get_parking_guidance.call_args_list[1].args[0], second_snapshot)
        self.assertEqual(get_parking_guidance.call_args_list[1].args[1], second_condition)


if __name__ == "__main__":
    unittest.main()
