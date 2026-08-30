#SyazUpdate30/8/2026

from pathlib import Path
from time import time
from typing import Mapping

import streamlit as st

from config.languages import DEFAULT_LANGUAGE, get_ui_text
from services import firebase_service, llm_service
from services.assistance_service import (
    objective_condition_from_situation,
    sensor_snapshot_from_situation,
    should_generate_assistance,
)
from services.situation_service import get_current_situation
from ui.components import (
    ai_assistance_area,
    app_footer,
    app_header,
    assistance_view,
    home_view,
    render_live_assistance,
    sensor_panel,
)
from ui.tts import (
    cancel_active_speech,
    queue_ai_response_speech,
    render_pending_ai_speech,
)


BASE_DIR = Path(__file__).parent


def get_parking_guidance(
    sensor_snapshot: Mapping[str, object],
    objective_condition: Mapping[str, object],
    *,
    language: str,
) -> str:
    """Indirection keeps the app request boundary easy to test."""
    return llm_service.get_parking_guidance(
        sensor_snapshot,
        objective_condition,
        language=language,
    )


def load_css(path: Path) -> None:
    st.html(f"<style>{path.read_text(encoding='utf-8')}</style>")


def initialize_state() -> None:
    defaults = {
        "view": "home",
        "ai_result": None,
        "ai_sensor_snapshot": None,
        "ai_objective_condition": None,
        "ai_request_in_progress": False,
        "last_ai_request_time": None,
        "assistance_paused": False,
        "tts_enabled": True,
        "ai_response_id": 0,
        "ai_spoken_response_id": None,
        "ai_pending_speech": None,
        "tts_cancel_requested": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def request_ai_suggestion(
    sensor_snapshot: Mapping[str, object],
    objective_condition: Mapping[str, object],
    language: str = DEFAULT_LANGUAGE,
) -> str:
    """Request guidance from the supplied snapshot, never by polling Firebase."""
    return get_parking_guidance(
        sensor_snapshot,
        objective_condition,
        language=language,
    )


def generate_automatic_assistance(
    sensor_snapshot: Mapping[str, object],
    objective_condition: Mapping[str, object],
) -> None:
    """Store one AI result and associate it with the exact sensor snapshot used."""
    if st.session_state.ai_request_in_progress:
        return

    st.session_state.ai_request_in_progress = True
    st.session_state.last_ai_request_time = time()
    language = DEFAULT_LANGUAGE

    try:
        suggestion = request_ai_suggestion(sensor_snapshot, objective_condition, language)
    except Exception:
        suggestion = get_ui_text(language, "ai_request_failed")
    finally:
        st.session_state.ai_request_in_progress = False

    st.session_state.ai_sensor_snapshot = dict(sensor_snapshot)
    st.session_state.ai_objective_condition = dict(objective_condition)
    st.session_state.ai_result = {"suggestion": suggestion}
    st.session_state.ai_response_id += 1
    queue_ai_response_speech(
        st.session_state.ai_response_id,
        suggestion,
        language,
        enabled=bool(st.session_state.tts_enabled),
    )


def main() -> None:
    st.set_page_config(
        page_title="ParkAssist LLM",
        page_icon="P",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    load_css(BASE_DIR / "assets" / "styles.css")
    initialize_state()

    if st.session_state.tts_cancel_requested:
        cancel_active_speech()
        st.session_state.tts_cancel_requested = False

    sensor_column, content_column = st.columns([0.28, 1], gap="small")
    with sensor_column:
        sensor_panel_placeholder = st.empty()

    with content_column:
        app_header(show_navigation=st.session_state.view == "assistance")
        if st.session_state.view == "home":
            home_view()
            current_situation_placeholder = None
            ai_assistance_placeholder = None
            visualization_placeholder = None
        else:
            # Old sessions may still contain the removed language view.
            if st.session_state.view == "language":
                st.session_state.view = "assistance"

            (
                current_situation_placeholder,
                ai_assistance_placeholder,
                visualization_placeholder,
            ) = assistance_view()

    @st.fragment(run_every="2s")
    def refresh_live_sensor_section() -> None:
        sensor_data = firebase_service.get_parking_data()
        with sensor_panel_placeholder.container():
            sensor_panel(sensor_data)

        if st.session_state.view != "assistance":
            return

        situation = get_current_situation(sensor_data, DEFAULT_LANGUAGE)
        render_live_assistance(
            sensor_data,
            situation,
            current_situation_placeholder,
            visualization_placeholder,
        )

        sensor_snapshot = sensor_snapshot_from_situation(situation)
        objective_condition = objective_condition_from_situation(situation)
        if (
            not st.session_state.assistance_paused
            and not st.session_state.ai_request_in_progress
            and should_generate_assistance(
                sensor_snapshot,
                objective_condition,
                st.session_state.ai_sensor_snapshot,
                st.session_state.ai_objective_condition,
                st.session_state.last_ai_request_time,
                time(),
            )
        ):
            generate_automatic_assistance(sensor_snapshot, objective_condition)

        with ai_assistance_placeholder.container():
            ai_assistance_area()
        render_pending_ai_speech()

    refresh_live_sensor_section()
    app_footer()


if __name__ == "__main__":
    main()
