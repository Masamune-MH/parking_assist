import time
from pathlib import Path
from config.languages import DEFAULT_LANGUAGE, normalize_language
from services.llm_service import get_parking_guidance
from services.firebase_service import get_parking_data
from services.situation_service import get_current_situation, get_vehicle_angle
import streamlit as st

from ui.components import (
    app_footer,
    app_header,
    assistance_view,
    home_view,
    language_selection_view,
    render_live_ai_suggestion,
    render_live_assistance,
    sensor_panel,
)


BASE_DIR = Path(__file__).parent

AI_REFRESH_THRESHOLD_CM = 5
AI_REFRESH_MIN_INTERVAL_SECONDS = 8.0


def _distances_changed_significantly(
    previous: tuple[float, float, float] | None,
    current: tuple[float, float, float],
) -> bool:
    if previous is None:
        return True

    return any(
        abs(current[i] - previous[i]) >= AI_REFRESH_THRESHOLD_CM
        for i in range(3)
    )


def _resolve_distances(situation: dict) -> tuple[float, float, float]:
    readings = situation["sensor_readings"]
    left = readings["left"]["distance"]
    center = readings["center"]["distance"]
    right = readings["right"]["distance"]
    return (
        left if left is not None else 30,
        center if center is not None else 30,
        right if right is not None else 30,
    )


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

    if "ai_sensor_snapshot" not in st.session_state:
        st.session_state.ai_sensor_snapshot = None

    if "ai_last_update_time" not in st.session_state:
        st.session_state.ai_last_update_time = 0.0

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
    vehicle_angle_container = None
    ai_suggestion_container = None
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
                distances = _resolve_distances(initial_situation)
                initial_angle = get_vehicle_angle(initial_sensor_data, current_lang)
                advice = get_parking_guidance(
                    *distances,
                    language=current_lang,
                    angle_deg=initial_angle["angle"],
                )
                st.session_state.ai_result = {
                    "suggestion": advice
                }
                st.session_state.ai_sensor_snapshot = distances
                st.session_state.ai_last_update_time = time.monotonic()

            (
                current_situation_container,
                vehicle_angle_container,
                ai_suggestion_container,
                visualization_container,
            ) = assistance_view()
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
            and vehicle_angle_container is not None
            and ai_suggestion_container is not None
            and visualization_container is not None
        ):
            live_language = normalize_language(st.session_state.get("language"))
            live_situation = get_current_situation(live_sensor_data, live_language)
            live_angle = get_vehicle_angle(live_sensor_data, live_language)
            render_live_assistance(
                live_sensor_data,
                live_situation,
                current_situation_container,
                visualization_container,
                angle_info=live_angle,
                vehicle_angle_container=vehicle_angle_container,
            )

            live_distances = _resolve_distances(live_situation)
            time_since_last_update = time.monotonic() - st.session_state.ai_last_update_time
            if (
                _distances_changed_significantly(
                    st.session_state.ai_sensor_snapshot,
                    live_distances,
                )
                and time_since_last_update >= AI_REFRESH_MIN_INTERVAL_SECONDS
            ):
                st.session_state.ai_result = {
                    "suggestion": get_parking_guidance(
                        *live_distances,
                        language=live_language,
                        angle_deg=live_angle["angle"],
                    )
                }
                st.session_state.ai_sensor_snapshot = live_distances
                st.session_state.ai_last_update_time = time.monotonic()

            render_live_ai_suggestion(
                ai_suggestion_container,
                st.session_state.ai_result["suggestion"],
            )

    refresh_live_sensor_section()

    app_footer()


if __name__ == "__main__":
    main()
