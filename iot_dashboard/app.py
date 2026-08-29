from pathlib import Path
from config.languages import DEFAULT_LANGUAGE, normalize_language
from services.llm_service import get_parking_guidance
from services.firebase_service import get_parking_data
from services.situation_service import get_current_situation
import streamlit as st

from ui.components import (
    app_footer,
    app_header,
    assistance_view,
    home_view,
    language_selection_view,
    render_live_assistance,
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
        st.session_state.language = DEFAULT_LANGUAGE
    else:
        st.session_state.language = normalize_language(st.session_state.language)

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

    sensor_column, content_column = st.columns([0.28, 1], gap="small")

    with sensor_column:
        sensor_panel_container = st.empty()

    current_situation_container = None
    visualization_container = None
    with content_column:
        app_header(show_navigation=st.session_state.view == "assistance")

        if st.session_state.view == "home":
            home_view()
        elif st.session_state.view == "language":
            language_selection_view()
        elif st.session_state.view == "assistance":
            current_lang = normalize_language(st.session_state.get("language"))

            if st.session_state.ai_result is None:
                initial_sensor_data = get_parking_data()
                initial_situation = get_current_situation(
                    initial_sensor_data,
                    current_lang,
                )
                readings = initial_situation["sensor_readings"]
                left_distance = readings["left"]["distance"]
                center_distance = readings["center"]["distance"]
                right_distance = readings["right"]["distance"]
                advice = get_parking_guidance(
                    left_distance if left_distance is not None else 30,
                    center_distance if center_distance is not None else 30,
                    right_distance if right_distance is not None else 30,
                    language=current_lang
                )
                st.session_state.ai_result = {
                    "suggestion": advice
                }

            current_situation_container, visualization_container = assistance_view()
        else:
            st.session_state.view = "home"
            st.rerun()

    @st.fragment(run_every="2s")
    def refresh_live_sensor_section() -> None:
        # Keep automatic reruns limited to Firebase data and deterministic UI.
        live_sensor_data = get_parking_data()

        with sensor_panel_container:
            sensor_panel(live_sensor_data)

        if (
            st.session_state.view == "assistance"
            and current_situation_container is not None
            and visualization_container is not None
        ):
            live_language = normalize_language(st.session_state.get("language"))
            live_situation = get_current_situation(live_sensor_data, live_language)
            render_live_assistance(
                live_sensor_data,
                live_situation,
                current_situation_container,
                visualization_container,
            )

    refresh_live_sensor_section()

    app_footer()


if __name__ == "__main__":
    main()
