from pathlib import Path

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
    st.html(path)


def initialize_state() -> None:
    if "view" not in st.session_state:
        st.session_state.view = "home"

    if "language" not in st.session_state:
        st.session_state.language = None

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

    sensor_data = {
        "left": 30,
        "center": 30,
        "right": 30,
    }
    assistance_sensor_data = {
        "left": 120,
        "center": 85,
        "right": 8,
    }

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
            assistance_view(assistance_sensor_data)
        else:
            st.session_state.view = "home"
            st.rerun()

    app_footer()


if __name__ == "__main__":
    main()
