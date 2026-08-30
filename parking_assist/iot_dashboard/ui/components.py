from html import escape
from textwrap import dedent
from typing import Mapping

import streamlit as st

from config.languages import DEFAULT_LANGUAGE, get_sensor_status_label, get_ui_text
from services.situation_service import format_distance, get_sensor_status


STATUS_STYLES = {
    "safe": {
        "label": "SAFE",
        "color": "#146c2e",
    },
    "warning": {
        "label": "WARNING",
        "color": "#8d5200",
    },
    "critical": {
        "label": "CRITICAL",
        "color": "#ba1a1a",
    },
    "unknown": {
        "label": "UNAVAILABLE",
        "color": "#687575",
    },
}


def _html(markup: str) -> str:
    return dedent(markup).strip()


def render_html(markup: str) -> None:
    st.html(_html(markup))


def _format_distance(distance: object) -> str:
    return format_distance(distance if isinstance(distance, (int, float)) else None)


def sensor_card(name: str, distance: object) -> str:
    status = get_sensor_status(distance)
    status_style = STATUS_STYLES[status]
    label = escape(name.upper())
    value = _format_distance(distance)
    status_label = get_sensor_status_label(DEFAULT_LANGUAGE, status).upper()

    return _html(
        f"""
        <article class="sensor-card sensor-card--{status}" style="--status-color: {status_style['color']};" aria-label="{label} sensor distance">
            <div class="sensor-card__label">{label}</div>
            <div class="sensor-card__value">{value}</div>
            <div class="sensor-card__unit">CM</div>
            <div class="sensor-card__status">
                <span class="status-dot" aria-hidden="true"></span>
                <span>{status_label}</span>
            </div>
        </article>
        """
    )


def navigation_panel() -> str:
    return _html(
        """
        <nav class="sensor-nav" aria-label="Sensor views">
            <div class="sensor-nav__item sensor-nav__item--active">
                <span class="sensor-nav__glyph sensor-nav__glyph--dashboard" aria-hidden="true"></span>
                <span>Sensor Dashboard</span>
            </div>
            <div class="sensor-nav__item">
                <span class="sensor-nav__glyph sensor-nav__glyph--logs" aria-hidden="true"></span>
                <span>Sensor Logs</span>
            </div>
        </nav>
        """
    )


def sensor_panel(sensor_data: Mapping[str, object] | None) -> None:
    readings = sensor_data if isinstance(sensor_data, Mapping) else {}
    cards = "\n".join(
        sensor_card(label, readings.get(key))
        for key, label in (
            ("left", "Left"),
            ("center", "Center"),
            ("right", "Right"),
        )
    )

    render_html(
        f"""
        <aside class="sensor-panel" aria-label="Real-time telemetry">
            <div>
                <div class="sensor-panel__title">Sensor Data</div>
                <div class="sensor-panel__subtitle">REAL-TIME TELEMETRY</div>
                <div class="sensor-panel__cards">
                    {cards}
                </div>
            </div>
            {navigation_panel()}
        </aside>
        """
    )


def app_header(show_navigation: bool = False) -> None:
    with st.container(key="app_header_layout"):
        title_column, navigation_column = st.columns([1, 0.16], gap="small")
        with title_column:
            render_html(
                """
                <header class="app-header">
                    <h1>ParkAssist LLM</h1>
                </header>
                """
            )
        with navigation_column:
            if show_navigation and st.button(
                get_ui_text(DEFAULT_LANGUAGE, "home"),
                key="assistance_home",
                width="stretch",
            ):
                st.session_state.view = "home"
                st.rerun()


def _technical_icon() -> str:
    return _html(
        """
        <div class="technical-icon" role="img" aria-label="Telemetry processor">
            <span class="technical-icon__body">
                <i></i><i></i><i></i>
            </span>
        </div>
        """
    )


def home_view() -> None:
    render_html(
        f"""
        <section class="home-intro" aria-labelledby="home-title">
            {_technical_icon()}
            <h2 id="home-title">ParkAssist LLM</h2>
            <p>
                Intelligent parking guidance initialized. Awaiting user command to
                process telemetry.
            </p>
        </section>
        """
    )

    with st.container(key="home_action"):
        _, action_column, _ = st.columns([1, 0.55, 1], gap="small")
        with action_column:
            if st.button(
                "Get Parking Assistance",
                type="primary",
                key="get_parking_assistance",
                width="stretch",
            ):
                st.session_state.view = "assistance"
                st.session_state.ai_result = None
                st.session_state.ai_sensor_snapshot = None
                st.session_state.ai_objective_condition = None
                st.session_state.last_ai_request_time = None
                st.session_state.ai_pending_speech = None
                st.rerun()

    render_html(
        """
        <div class="monitor-status">
            <span class="monitor-status__dot" aria-hidden="true"></span>
            <span>Real-time sensor monitoring active</span>
        </div>
        """
    )


def select_language(language: str) -> None:
    st.session_state.language = language
    st.session_state.view = "assistance"
    st.rerun()


def language_selection_view() -> None:
    render_html(
        """
        <section class="language-selection" aria-labelledby="language-title">
            <h2>ParkAssist LLM</h2>
            <h3 id="language-title">Choose your language</h3>
        </section>
        """
    )

    with st.container(key="language_selection", gap="small"):
        for language in ("English", "Japanese", "Tiếng Việt"):
            if st.button(
                language,
                key=f"language_{language}",
                width="stretch",
            ):
                select_language(language)


def _sensor_reading_markup(label: str, distance: object) -> str:
    status = get_sensor_status(distance)
    status_style = STATUS_STYLES[status]

    return _html(
        f"""
        <div class="sensor-reading sensor-reading--{label.lower()}" style="--sensor-color: {status_style['color']};">
            <span class="sensor-reading__label">{escape(label)}</span>
            <strong class="sensor-reading__value">{_format_distance(distance)} cm</strong>
            <span class="sensor-reading__status">
                <i aria-hidden="true"></i>{get_sensor_status_label(DEFAULT_LANGUAGE, status).upper()}
            </span>
        </div>
        """
    )


def vehicle_sensor_visualization(sensor_data: Mapping[str, object] | None) -> None:
    readings_source = sensor_data if isinstance(sensor_data, Mapping) else {}
    readings = {
        key: _sensor_reading_markup(label, readings_source.get(key))
        for key, label in (
            ("left", "LEFT"),
            ("center", "CENTER"),
            ("right", "RIGHT"),
        )
    }
    rays = {
        key: STATUS_STYLES[get_sensor_status(readings_source.get(key))]["color"]
        for key in ("left", "center", "right")
    }

    render_html(
        f"""
        <section class="assistance-card sensor-visualization" aria-labelledby="sensor-view-title">
            <h2 id="sensor-view-title">TOP-DOWN SENSOR VIEW</h2>
            <div class="sensor-visualization__canvas">
                {readings['left']}
                {readings['center']}
                {readings['right']}

                <span class="sensor-ray sensor-ray--left" style="--sensor-color: {rays['left']};" aria-hidden="true"></span>
                <span class="sensor-ray sensor-ray--center" style="--sensor-color: {rays['center']};" aria-hidden="true"></span>
                <span class="sensor-ray sensor-ray--right" style="--sensor-color: {rays['right']};" aria-hidden="true"></span>

                <div class="vehicle-outline" role="img" aria-label="Top-down vehicle outline">
                    <span class="vehicle-outline__windshield" aria-hidden="true"></span>
                    <span class="vehicle-outline__centerline" aria-hidden="true"></span>
                    <span class="vehicle-outline__label">VEHICLE</span>
                </div>
            </div>
        </section>
        """
    )


def current_situation_card(text: str) -> None:
    render_html(
        f"""
        <article class="assistance-card current-situation" aria-labelledby="current-situation-title">
            <div class="assistance-card__heading">
                <span class="information-icon" aria-hidden="true">i</span>
                <h2 id="current-situation-title">{escape(get_ui_text(DEFAULT_LANGUAGE, 'current_situation'))}</h2>
            </div>
            <p>{escape(text)}</p>
        </article>
        """
    )


def ai_suggestion_card(text: str) -> None:
    render_html(
        f"""
        <article class="assistance-card ai-suggestion" aria-labelledby="ai-suggestion-title">
            <div class="assistance-card__heading">
                <span class="suggestion-icon" aria-hidden="true"></span>
                <h2 id="ai-suggestion-title">{escape(get_ui_text(DEFAULT_LANGUAGE, 'ai_suggestion'))}</h2>
            </div>
            <p>{escape(text)}</p>
        </article>
        """
    )


def audio_controls() -> None:
    with st.container(key="audio_controls"):
        mute_column, pause_column = st.columns(2, gap="small")
        with mute_column:
            enabled = bool(st.session_state.get("tts_enabled", True))
            if st.button(
                get_ui_text(DEFAULT_LANGUAGE, "mute" if enabled else "unmute"),
                icon=":material/volume_up:" if enabled else ":material/volume_off:",
                key="assistance_mute_toggle",
                width="stretch",
            ):
                st.session_state.tts_enabled = not enabled
                if enabled:
                    st.session_state.ai_pending_speech = None
                    st.session_state.tts_cancel_requested = True
                st.rerun()
        with pause_column:
            paused = bool(st.session_state.get("assistance_paused", False))
            if st.button(
                get_ui_text(
                    DEFAULT_LANGUAGE,
                    "resume_assistance" if paused else "pause_assistance",
                ),
                icon=":material/play_arrow:" if paused else ":material/pause:",
                key="assistance_pause_toggle",
                width="stretch",
            ):
                st.session_state.assistance_paused = not paused
                st.rerun()


def ai_assistance_area() -> None:
    ai_result = st.session_state.get("ai_result")
    if not isinstance(ai_result, Mapping):
        return

    suggestion = ai_result.get("suggestion")
    if isinstance(suggestion, str) and suggestion:
        ai_suggestion_card(suggestion)


def render_live_assistance(
    sensor_data: Mapping[str, object] | None,
    situation: Mapping[str, object],
    current_situation_placeholder: object,
    visualization_placeholder: object,
) -> None:
    current_situation = situation.get("current_situation")
    with current_situation_placeholder.container():
        current_situation_card(str(current_situation or "Sensor readings are temporarily unavailable."))
    with visualization_placeholder.container():
        vehicle_sensor_visualization(sensor_data)


def assistance_view() -> tuple[object, object, object]:
    current_situation_placeholder = st.empty()
    ai_assistance_placeholder = st.empty()
    visualization_placeholder = st.empty()
    audio_controls()
    return (
        current_situation_placeholder,
        ai_assistance_placeholder,
        visualization_placeholder,
    )


def assistance_placeholder_view() -> None:
    render_html(
        """
        <section class="assistance-placeholder" aria-labelledby="assistance-title">
            <h2 id="assistance-title">Assistance screen will be implemented next.</h2>
        </section>
        """
    )


def app_footer() -> None:
    render_html(
        """
        <div class="app-footer" role="contentinfo">
            <span>&copy; 2026 ParkAssist</span>
            <span>Powered by Google Gemini</span>
        </div>
        """
    )
