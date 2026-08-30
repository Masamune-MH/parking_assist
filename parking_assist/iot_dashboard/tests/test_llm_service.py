import unittest
from unittest.mock import Mock, patch

from services.llm_service import build_parking_guidance_prompt, get_parking_guidance


class LlmServiceTests(unittest.TestCase):
    def test_prompt_uses_python_supplied_snapshot_and_condition(self) -> None:
        prompt = build_parking_guidance_prompt(
            {"left": 120, "center": 85, "right": 8},
            {
                "nearest_direction": "right",
                "nearest_distance": 8,
                "overall_status": "critical",
            },
            "English",
        )

        self.assertIn("Right distance: 8 cm", prompt)
        self.assertIn("Nearest direction: right", prompt)
        self.assertIn("Overall risk level: critical", prompt)
        self.assertIn("Do not invent obstacle types.", prompt)
        self.assertIn("Do not override, reinterpret, or contradict", prompt)
        self.assertIn("Respond only in the selected language.", prompt)

    @patch("services.llm_service.get_openrouter_api_key", return_value=None)
    def test_openrouter_configuration_error_returns_localized_message(
        self,
        _get_openrouter_api_key,
    ) -> None:
        response = get_parking_guidance(
            {"left": 120, "center": 85, "right": 8},
            {
                "nearest_direction": "right",
                "nearest_distance": 8,
                "overall_status": "critical",
            },
            "English",
        )

        self.assertEqual(
            response,
            "Unable to generate parking assistance right now. Please try again.",
        )

    @patch("services.llm_service.requests.post", side_effect=OSError)
    @patch("services.llm_service.get_openrouter_api_key", return_value="test-key")
    def test_openrouter_network_error_returns_localized_message(
        self,
        _get_openrouter_api_key,
        _post,
    ) -> None:
        response = get_parking_guidance(
            {"left": 120, "center": 85, "right": 8},
            {
                "nearest_direction": "right",
                "nearest_distance": 8,
                "overall_status": "critical",
            },
            "English",
        )

        self.assertEqual(
            response,
            "Unable to generate parking assistance right now. Please try again.",
        )

    @patch("services.llm_service.requests.post")
    @patch("services.llm_service.get_openrouter_api_key", return_value="test-key")
    def test_openrouter_request_has_a_five_second_timeout(
        self,
        _get_openrouter_api_key,
        post,
    ) -> None:
        response = Mock()
        response.json.return_value = {
            "choices": [{"message": {"content": "Keep moving slowly."}}]
        }
        post.return_value = response

        get_parking_guidance(
            {"left": 60, "center": 40, "right": 14},
            {
                "nearest_direction": "right",
                "nearest_distance": 14,
                "overall_status": "warning",
            },
            "English",
        )

        self.assertEqual(post.call_args.kwargs["timeout"], 5)


if __name__ == "__main__":
    unittest.main()
