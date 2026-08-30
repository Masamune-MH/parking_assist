import unittest
from base64 import b64decode
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


class AssistanceUiTests(unittest.TestCase):
    @patch("ui.tts.st.iframe")
    @patch(
        "services.llm_service.get_parking_guidance",
        return_value="Mock parking guidance.",
    )
    @patch(
        "services.firebase_service.get_parking_data",
        return_value={"left": 66, "center": 64, "right": 66},
    )
    def test_initial_ai_card_appears_without_manual_action(
        self,
        _get_parking_data,
        _get_parking_guidance,
        speech_iframe,
    ) -> None:
        dashboard = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
        dashboard.run()

        dashboard.button(key="get_parking_assistance").click().run()

        self.assertEqual(dashboard.session_state["ai_result"]["suggestion"], "Mock parking guidance.")
        self.assertIn("Mock parking guidance.", str(dashboard))
        self.assertNotIn("Generate New", str(dashboard))
        self.assertNotIn("Change Language", str(dashboard))
        self.assertNotIn("Choose your language", str(dashboard))
        self.assertEqual(dashboard.button(key="assistance_mute_toggle").label, "Mute")
        self.assertEqual(
            dashboard.button(key="assistance_pause_toggle").label,
            "Pause Assistance",
        )
        self.assertEqual(dashboard.session_state["ai_spoken_response_id"], 1)
        speech_iframe.assert_called_once()

        dashboard.run()
        speech_iframe.assert_called_once()

    @patch("ui.tts.st.iframe")
    @patch(
        "services.llm_service.get_parking_guidance",
        return_value="Japanese parking guidance.",
    )
    @patch(
        "services.firebase_service.get_parking_data",
        return_value={"left": 66, "center": 64, "right": 66},
    )
    def test_fixed_english_flow_sets_the_speech_locale(
        self,
        _get_parking_data,
        _get_parking_guidance,
        speech_iframe,
    ) -> None:
        dashboard = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
        dashboard.run()

        dashboard.button(key="get_parking_assistance").click().run()

        iframe_source = speech_iframe.call_args.args[0]
        encoded_markup = iframe_source.split(",", 1)[1]
        markup = b64decode(encoded_markup).decode("utf-8")
        self.assertIn('speechLocale = "en-US"', markup)

    @patch("ui.tts.st.iframe")
    @patch(
        "services.llm_service.get_parking_guidance",
        return_value="Silent parking guidance.",
    )
    @patch(
        "services.firebase_service.get_parking_data",
        return_value={"left": 66, "center": 64, "right": 66},
    )
    def test_mute_skips_new_response_speech(
        self,
        _get_parking_data,
        _get_parking_guidance,
        speech_iframe,
    ) -> None:
        dashboard = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
        dashboard.run()

        dashboard.session_state["tts_enabled"] = False
        dashboard.button(key="get_parking_assistance").click().run()

        self.assertFalse(dashboard.session_state["tts_enabled"])
        self.assertEqual(dashboard.session_state["ai_spoken_response_id"], 1)
        speech_iframe.assert_not_called()


if __name__ == "__main__":
    unittest.main()
