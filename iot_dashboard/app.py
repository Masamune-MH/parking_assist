from pathlib import Path
from services.llm_service import get_parking_guidance
from services.firebase_service import get_parking_data
import streamlit as st

from ui.components import (
    app_footer,
    app_header,
    assistance_view,
    home_view,
    language_selection_view,
    sensor_panel,
)


BASE_DIR = Path(__file__).parent


def load_css(path: Path) -> None:
    with open(path, "r", encoding="utf-8") as f:
        css_content = f.read()
        st.html(f"<style>{css_content}</style>")


def initialize_state() -> None:
    if "view" not in st.session_state:
        st.session_state.view = "home"

    if "language" not in st.session_state:
        st.session_state["language"] = "English"

    if "ai_result" not in st.session_state:
        st.session_state.ai_result = None

    if "audio_enabled" not in st.session_state:
        st.session_state.audio_enabled = True


def main() -> None:
    st.set_page_config(
        page_title="ParkAssist LLM",
        page_icon="P",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    load_css(BASE_DIR / "assets" / "styles.css")
    initialize_state()

    # Get real-time sensor data from Firebase
    sensor_data = get_parking_data()
    assistance_sensor_data = get_parking_data()

    sensor_column, content_column = st.columns([0.28, 1], gap="small")

    with sensor_column:
        sensor_panel(sensor_data)

    with content_column:
        app_header()

        if st.session_state.view == "home":
            home_view()
        elif st.session_state.view == "language":
            language_selection_view()
        elif st.session_state.view == "assistance":
            current_lang = st.session_state.get("language", "English")
        
            if st.session_state.ai_result is None:
                advice = get_parking_guidance(
                    assistance_sensor_data["left"],
                    assistance_sensor_data["center"],
                    assistance_sensor_data["right"],
                    language=current_lang
                )
                st.session_state.ai_result = {
                    "current_situation": advice,
                    "suggestion": advice
                }
            
            assistance_view(assistance_sensor_data)
        else:
            st.session_state.view = "home"
            st.rerun()

    app_footer()


if __name__ == "__main__":
    main()
