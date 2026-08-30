import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


APP_PATH = str(Path(__file__).resolve().parents[1] / "app.py")


class AutomaticAssistanceUiTests(unittest.TestCase):
    @patch("ui.tts.st.iframe")
    def test_pause_blocks_generation_and_mute_skips_speech(self, speech_iframe) -> None:
        sensor_state = {"left": 66, "center": 64, "right": 66}
        calls = []

        def get_sensor_data():
            return dict(sensor_state)

        def get_guidance(snapshot, condition, language):
            calls.append((dict(snapshot), dict(condition), language))
            return f"Guidance {len(calls)}"

        with patch("services.firebase_service.get_parking_data", side_effect=get_sensor_data), patch(
            "services.llm_service.get_parking_guidance",
            side_effect=get_guidance,
        ):
            dashboard = AppTest.from_file(APP_PATH)
            dashboard.run()
            dashboard.button(key="get_parking_assistance").click().run()

            self.assertEqual(len(calls), 1)
            self.assertEqual(speech_iframe.call_count, 1)

            dashboard.button(key="assistance_pause_toggle").click().run()
            sensor_state["center"] = 5
            dashboard.session_state["last_ai_request_time"] = 0
            dashboard.run()
            self.assertTrue(dashboard.session_state["assistance_paused"])
            self.assertEqual(len(calls), 1)

            dashboard.button(key="assistance_pause_toggle").click().run()
            self.assertFalse(dashboard.session_state["assistance_paused"])
            self.assertEqual(len(calls), 2)

            dashboard.button(key="assistance_mute_toggle").click().run()
            speech_iframe.reset_mock()
            sensor_state["right"] = 10
            dashboard.session_state["last_ai_request_time"] = 0
            dashboard.run()
            self.assertFalse(dashboard.session_state["tts_enabled"])
            self.assertEqual(len(calls), 3)
            speech_iframe.assert_not_called()


if __name__ == "__main__":
    unittest.main()
