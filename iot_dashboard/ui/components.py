from html import escape
from textwrap import dedent
from typing import Mapping

import streamlit as st


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
}


def _html(markup: str) -> str:
    return dedent(markup).strip()


def render_html(markup: str) -> None:
    st.html(_html(markup))


def get_sensor_status(distance: float) -> str:
    if distance <= 10:
        return "critical"

    if distance <= 20:
        return "warning"

    return "safe"


def _format_distance(distance: float) -> str:
    numeric_distance = float(distance)

    if numeric_distance.is_integer():
        return str(int(numeric_distance))

    return f"{numeric_distance:.1f}"


def sensor_card(name: str, distance: float) -> str:
    status = get_sensor_status(distance)
    status_style = STATUS_STYLES[status]
    label = escape(name.upper())
    value = _format_distance(distance)

    return _html(
        f"""
        <article class="sensor-card sensor-card--{status}" style="--status-color: {status_style['color']};" aria-label="{label} sensor distance">
            <div class="sensor-card__label">{label}</div>
            <div class="sensor-card__value">{value}</div>
            <div class="sensor-card__unit">CM</div>
            <div class="sensor-card__status">
                <span class="status-dot" aria-hidden="true"></span>
                <span>{status_style['label']}</span>
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


def sensor_panel(sensor_data: Mapping[str, float]) -> None:
    cards = "\n".join(
        sensor_card(label, sensor_data[key])
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


def app_header() -> None:
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
        "Get Parking Assistance",
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


def _sensor_reading_markup(label: str, distance: float) -> str:
    status = get_sensor_status(distance)
    status_style = STATUS_STYLES[status]

    return _html(
        f"""
        <div class="sensor-reading sensor-reading--{label.lower()}" style="--sensor-color: {status_style['color']};">
            <span class="sensor-reading__label">{escape(label)}</span>
            <strong class="sensor-reading__value">{_format_distance(distance)} cm</strong>
            <span class="sensor-reading__status">
                <i aria-hidden="true"></i>{status_style['label']}
            </span>
        </div>
        """
    )


def vehicle_sensor_visualization(sensor_data: Mapping[str, float]) -> None:
    readings = {
        key: _sensor_reading_markup(label, sensor_data[key])
        for key, label in (
            ("left", "LEFT"),
            ("center", "CENTER"),
            ("right", "RIGHT"),
        )
    }
    rays = {
        key: STATUS_STYLES[get_sensor_status(sensor_data[key])]["color"]
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
                <h2 id="current-situation-title">Current Situation</h2>
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
                <h2 id="ai-suggestion-title">AI Suggestion</h2>
            </div>
            <p>{escape(text)}</p>
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
                "Mute" if audio_enabled else "Speaker",
                icon=":material/volume_up:" if audio_enabled else ":material/volume_off:",
                key="audio_toggle",
                width="stretch",
            ):
                st.session_state.audio_enabled = not audio_enabled
                st.rerun()


def assistance_view(sensor_data: Mapping[str, float]) -> None:
    default_result = {
        "current_situation": (
            "An obstacle is very close to the right-front side of the monitored "
            "area. The right sensor currently measures approximately 8 cm of "
            "clearance, while significantly more clearance is available through "
            "the center and left sensing directions."
        ),
        "suggestion": (
            "Reverse slowly while steering slightly toward the left. Continue "
            "monitoring the right-side clearance while moving."
        ),
    }
    ai_result = st.session_state.ai_result
    result = ai_result if isinstance(ai_result, Mapping) else default_result

    current_situation_card(
        str(result.get("current_situation") or default_result["current_situation"])
    )
    ai_suggestion_card(str(result.get("suggestion") or default_result["suggestion"]))
    vehicle_sensor_visualization(sensor_data)
    audio_controls()


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
