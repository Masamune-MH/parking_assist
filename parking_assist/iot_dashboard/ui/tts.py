import base64
import json
from typing import Mapping

import streamlit as st

from config.languages import get_speech_locale


def _javascript_string(value: str) -> str:
    """Serialize untrusted response text safely for an inline JavaScript value."""
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def build_speech_markup(text: str, language: str) -> str:
    locale = get_speech_locale(language)
    return f"""
    <!doctype html>
    <html>
      <body>
        <script>
          const speechText = {_javascript_string(text)};
          const speechLocale = {_javascript_string(locale)};
          const synth = window.speechSynthesis;

          if (synth && window.SpeechSynthesisUtterance) {{
            synth.cancel();
            synth.resume();

            const utterance = new SpeechSynthesisUtterance(speechText);
            utterance.lang = speechLocale;
            utterance.rate = 2.0;
            const matchingVoice = synth.getVoices().find((voice) =>
              voice.lang.toLowerCase() === speechLocale.toLowerCase() ||
              voice.lang.toLowerCase().startsWith(speechLocale.slice(0, 2).toLowerCase())
            );

            if (matchingVoice) {{
              utterance.voice = matchingVoice;
            }}

            synth.speak(utterance);
          }}
        </script>
      </body>
    </html>
    """


def build_cancellation_markup() -> str:
    return """
    <!doctype html>
    <html>
      <body>
        <script>
          if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
          }
        </script>
      </body>
    </html>
    """


def _render_hidden_iframe(markup: str) -> None:
    encoded_markup = base64.b64encode(markup.encode("utf-8")).decode("ascii")
    st.iframe(
        f"data:text/html;base64,{encoded_markup}",
        height=1,
        width=1,
        tab_index=-1,
    )


def speak_ai_response(text: str, language: str) -> None:
    _render_hidden_iframe(build_speech_markup(text, language))


def cancel_active_speech() -> None:
    _render_hidden_iframe(build_cancellation_markup())


def queue_ai_response_speech(
    response_id: int,
    text: str,
    language: str,
    enabled: bool,
) -> None:
    if enabled and text:
        st.session_state.ai_pending_speech = {
            "response_id": response_id,
            "text": text,
            "language": language,
        }
        st.session_state.ai_spoken_response_id = None
        return

    st.session_state.ai_pending_speech = None
    st.session_state.ai_spoken_response_id = response_id


def render_pending_ai_speech() -> bool:
    pending = st.session_state.get("ai_pending_speech")
    if not isinstance(pending, Mapping):
        return False

    response_id = pending.get("response_id")
    text = pending.get("text")
    language = pending.get("language")
    if not isinstance(response_id, int) or not isinstance(text, str) or not text:
        st.session_state.ai_pending_speech = None
        return False

    if (
        not st.session_state.get("tts_enabled", True)
        or st.session_state.get("ai_spoken_response_id") == response_id
    ):
        st.session_state.ai_pending_speech = None
        st.session_state.ai_spoken_response_id = response_id
        return False

    try:
        speak_ai_response(text, str(language))
    finally:
        # The component is emitted once, so subsequent app or fragment reruns do not replay it.
        st.session_state.ai_pending_speech = None
        st.session_state.ai_spoken_response_id = response_id

    return True
