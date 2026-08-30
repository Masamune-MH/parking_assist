import unittest
from base64 import b64decode
from unittest.mock import patch

from config.languages import get_speech_locale
from ui.tts import build_speech_markup, speak_ai_response


class TtsTests(unittest.TestCase):
    def test_fixed_english_configuration_provides_browser_speech_locale(self) -> None:
        self.assertEqual(get_speech_locale("English"), "en-US")
        self.assertEqual(get_speech_locale(None), "en-US")

    def test_speech_markup_keeps_response_text_inside_javascript_value(self) -> None:
        markup = build_speech_markup("Text </script><script>alert(1)</script>", "English")

        self.assertIn('speechLocale = "en-US"', markup)
        self.assertIn("<\\/script>", markup)

    @patch("ui.tts.st.iframe")
    def test_speech_uses_a_hidden_data_iframe(self, iframe) -> None:
        speak_ai_response("Use the configured language.", "English")

        source = iframe.call_args.args[0]
        encoded_markup = source.split(",", 1)[1]
        markup = b64decode(encoded_markup).decode("utf-8")
        self.assertIn('speechLocale = "en-US"', markup)
        iframe.assert_called_once_with(source, height=1, width=1, tab_index=-1)


if __name__ == "__main__":
    unittest.main()
