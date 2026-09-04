from html import escape
from textwrap import dedent
from typing import Mapping

import streamlit as st

from config.languages import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    get_sensor_status_label,
    get_ui_text,
    normalize_language,
)
from services.situation_service import format_distance, get_sensor_status


STATUS_STYLES = {
    "safe": {
        "color": "#146c2e",
    },
    "warning": {
        "color": "#8d5200",
    },
    "critical": {
        "color": "#ba1a1a",
    },
    "unknown": {
        "color": "#66706f",
    },
}


def _html(markup: str) -> str:
    return dedent(markup).strip()


def render_html(markup: str) -> None:
    st.html(_html(markup))


def selected_language() -> str:
    return normalize_language(st.session_state.get("language", DEFAULT_LANGUAGE))


def text(key: str) -> str:
    return get_ui_text(selected_language(), key)


def sensor_card(name: str, distance: object, language: str | None = None) -> str:
    status = get_sensor_status(distance)
    status_style = STATUS_STYLES[status]
    label = escape(name.upper())
    value = format_distance(distance)
    status_label = escape(get_sensor_status_label(language, status))

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


def sensor_panel(sensor_data: Mapping[str, object]) -> None:
    language = selected_language()
    cards = "\n".join(
        sensor_card(label, sensor_data.get(key), language=language)
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


def go_home() -> None:
    st.session_state.view = "home"
    st.rerun()


def change_language() -> None:
    st.session_state.ai_result = None
    st.session_state.view = "language"
    st.rerun()


def assistance_header() -> None:
    with st.container(key="assistance_header"):
        title_column, home_column, language_column = st.columns(
            [1, 0.18, 0.3],
            gap="small",
        )

        with title_column:
            render_html('<div class="app-header__title">ParkAssist LLM</div>')
        with home_column:
            if st.button(
                text("home"),
                key="assistance_home",
                width="stretch",
            ):
                go_home()
        with language_column:
            if st.button(
                text("change_language"),
                key="assistance_change_language",
                width="stretch",
            ):
                change_language()


def app_header(show_navigation: bool = False) -> None:
    if show_navigation:
        assistance_header()
        return

    render_html(
        """
        <header class="app-header">
            <h1>ParkAssist LLM</h1>
            <div class="app-header__controls" aria-label="Account and help controls">
                <span class="header-icon header-icon--account" aria-label="Account"></span>
                <span class="header-icon header-icon--help" aria-label="Help"></span>
            </div>
        </header>
        """
    )


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

    if st.button(
        text("get_assistance"),
        type="primary",
        key="get_parking_assistance",
    ):
        st.session_state.view = "language"
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
    st.session_state.language = normalize_language(language)
    st.session_state.ai_result = None
    st.session_state.view = "assistance"
    st.rerun()


def language_selection_view() -> None:
    render_html(
        f"""
        <section class="language-selection" aria-labelledby="language-title">
            <h2>ParkAssist LLM</h2>
            <h3 id="language-title">{escape(text("choose_language"))}</h3>
        </section>
        """
    )

    with st.container(key="language_selection", gap="small"):
        for language in SUPPORTED_LANGUAGES:
            if st.button(
                language,
                key=f"language_{language}",
                width="stretch",
            ):
                select_language(language)


def _sensor_reading_markup(
    label: str,
    distance: object,
    language: str | None = None,
) -> str:
    status = get_sensor_status(distance)
    status_style = STATUS_STYLES[status]
    status_label = escape(get_sensor_status_label(language, status))

    return _html(
        f"""
        <div class="sensor-reading sensor-reading--{label.lower()}" style="--sensor-color: {status_style['color']};">
            <span class="sensor-reading__label">{escape(label)}</span>
            <strong class="sensor-reading__value">{format_distance(distance)} cm</strong>
            <span class="sensor-reading__status">
                <i aria-hidden="true"></i>{status_label}
            </span>
        </div>
        """
    )


def vehicle_sensor_visualization(sensor_data: Mapping[str, object]) -> None:
    language = selected_language()
    readings = {
        key: _sensor_reading_markup(label, sensor_data.get(key), language=language)
        for key, label in (
            ("left", "LEFT"),
            ("center", "CENTER"),
            ("right", "RIGHT"),
        )
    }
    rays = {
        key: STATUS_STYLES[get_sensor_status(sensor_data.get(key))]["color"]
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


def current_situation_card(content: str) -> None:
    render_html(
        f"""
        <article class="assistance-card current-situation" aria-labelledby="current-situation-title">
            <div class="assistance-card__heading">
                <span class="information-icon" aria-hidden="true">i</span>
                <h2 id="current-situation-title">{escape(text("current_situation"))}</h2>
            </div>
            <p>{escape(content)}</p>
        </article>
        """
    )


def vehicle_angle_card(content: str) -> None:
    render_html(
        f"""
        <article class="assistance-card vehicle-angle" aria-labelledby="vehicle-angle-title">
            <div class="assistance-card__heading">
                <span class="information-icon" aria-hidden="true">∠</span>
                <h2 id="vehicle-angle-title">{escape(text("vehicle_angle"))}</h2>
            </div>
            <p>{escape(content)}</p>
        </article>
        """
    )


def ai_suggestion_card(content: str) -> None:
    render_html(
        f"""
        <article class="assistance-card ai-suggestion" aria-labelledby="ai-suggestion-title">
            <div class="assistance-card__heading">
                <span class="suggestion-icon" aria-hidden="true"></span>
                <h2 id="ai-suggestion-title">{escape(text("ai_suggestion"))}</h2>
            </div>
            <p>{escape(content)}</p>
        </article>
        """
    )


def audio_controls() -> None:
    with st.container(key="audio_controls"):
        play_column, pause_column, end_column, spacer_column, audio_column = st.columns(
            [1, 1, 1, 0.2, 1],
            gap="small",
        )

        with play_column:
            st.button(
                "Play",
                icon=":material/play_arrow:",
                key="audio_play",
                width="stretch",
            )
        with pause_column:
            st.button(
                "Pause",
                icon=":material/pause:",
                key="audio_pause",
                width="stretch",
            )
        with end_column:
            st.button(
                "End",
                icon=":material/stop:",
                key="audio_end",
                width="stretch",
            )
        with spacer_column:
            st.empty()
        with audio_column:
            audio_enabled = st.session_state.audio_enabled
            if st.button(
                text("voice_off") if audio_enabled else text("voice_on"),
                icon=":material/volume_up:" if audio_enabled else ":material/volume_off:",
                key="audio_toggle",
                width="stretch",
            ):
                st.session_state.audio_enabled = not audio_enabled
                st.rerun()


def _current_situation_content(situation: Mapping[str, object] | None) -> str:
    if isinstance(situation, Mapping):
        return str(
            situation.get("current_situation")
            or "Sensor readings are temporarily unavailable."
        )

    return "Sensor readings are temporarily unavailable."


def _vehicle_angle_content(angle_info: Mapping[str, object] | None) -> str:
    if isinstance(angle_info, Mapping):
        return str(
            angle_info.get("text")
            or "Vehicle angle cannot be determined right now."
        )

    return "Vehicle angle cannot be determined right now."


def _ai_suggestion_content() -> str:
    default_suggestion = (
        "Reverse slowly while steering slightly toward the left. Continue "
        "monitoring the right-side clearance while moving."
    )
    ai_result = st.session_state.ai_result
    suggestion = (
        str(ai_result.get("suggestion") or default_suggestion)
        if isinstance(ai_result, Mapping)
        else default_suggestion
    )

    return suggestion


def render_live_assistance(
    sensor_data: Mapping[str, object],
    situation: Mapping[str, object] | None,
    current_situation_container: object,
    visualization_container: object,
    angle_info: Mapping[str, object] | None = None,
    vehicle_angle_container: object = None,
) -> None:
    with current_situation_container:
        current_situation_card(_current_situation_content(situation))

    if vehicle_angle_container is not None:
        with vehicle_angle_container:
            vehicle_angle_card(_vehicle_angle_content(angle_info))

    with visualization_container:
        vehicle_sensor_visualization(sensor_data)


def render_live_ai_suggestion(
    ai_suggestion_container: object,
    suggestion: str,
) -> None:
    with ai_suggestion_container:
        ai_suggestion_card(suggestion)


def assistance_view() -> tuple[object, object, object, object]:
    current_situation_container = st.empty()
    vehicle_angle_container = st.empty()
    ai_suggestion_container = st.empty()
    with ai_suggestion_container:
        ai_suggestion_card(_ai_suggestion_content())
    visualization_container = st.empty()
    audio_controls()

    return (
        current_situation_container,
        vehicle_angle_container,
        ai_suggestion_container,
        visualization_container,
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
            <span>Powered by OpenRouter</span>
        </div>
        """
    )
