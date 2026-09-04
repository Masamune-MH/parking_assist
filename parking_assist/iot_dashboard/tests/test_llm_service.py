import unittest
from unittest.mock import Mock, patch

from services.llm_service import (
    DEFAULT_OPENROUTER_MODEL,
    build_parking_guidance_prompt,
    get_openrouter_model,
    get_parking_guidance,
)


class LlmServiceTests(unittest.TestCase):
    @patch.dict(
        "services.llm_service.os.environ",
        {"OPENROUTER_MODEL": "test/override-model"},
    )
    def test_model_can_be_overridden_by_environment(self) -> None:
        self.assertNotEqual(DEFAULT_OPENROUTER_MODEL, "test/override-model")
        self.assertEqual(get_openrouter_model(), "test/override-model")

    def test_prompt_phrases_the_decided_category_without_raw_numbers(self) -> None:
        prompt = build_parking_guidance_prompt("correction_maneuver", "English")

        self.assertIn("pull forward a little, straighten the wheel", prompt)
        self.assertIn("Do not mention specific distances, degrees, or which side", prompt)
        self.assertIn("Do not invent obstacle types", prompt)
        self.assertIn("Respond only in the selected language.", prompt)

    @patch("services.llm_service.get_openrouter_api_key", return_value=None)
    def test_openrouter_configuration_error_returns_category_fallback(
        self,
        _get_openrouter_api_key,
    ) -> None:
        # right=8cm is under the critical-stop threshold, so the category is "stop".
        response = get_parking_guidance(
            {"left": 120, "center": 85, "right": 8},
            {
                "nearest_direction": "right",
                "nearest_distance": 8,
                "overall_status": "critical",
                "angle_deg": None,
            },
            "English",
        )

        self.assertEqual(response, "Stop now, you're very close to an obstacle.")

    @patch("services.llm_service.requests.post", side_effect=OSError)
    @patch("services.llm_service.get_openrouter_api_key", return_value="test-key")
    def test_openrouter_network_error_returns_category_fallback(
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
                "angle_deg": None,
            },
            "English",
        )

        self.assertEqual(response, "Stop now, you're very close to an obstacle.")

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
        self.assertEqual(post.call_args.kwargs["json"]["max_tokens"], 120)
        self.assertEqual(
            post.call_args.kwargs["json"]["reasoning"],
            {"effort": "none", "exclude": True},
        )


if __name__ == "__main__":
    unittest.main()
