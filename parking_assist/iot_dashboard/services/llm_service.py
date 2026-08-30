import os
from textwrap import dedent
from typing import Mapping

import streamlit as st
import requests

from config.languages import (
    DEFAULT_LANGUAGE,
    get_llm_instruction,
    get_ui_text,
    normalize_language,
)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_OPENROUTER_MODEL = "nvidia/nemotron-3.5-lightning:free"


@st.cache_resource
def get_openrouter_api_key() -> str | None:
    """Lấy API key OpenRouter từ Streamlit secrets hoặc biến môi trường."""
    api_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    return api_key or None


def get_openrouter_model() -> str:
    """Allow deployments with credit to select a different OpenRouter model."""
    configured_model = (
        st.secrets.get("OPENROUTER_MODEL")
        or os.getenv("OPENROUTER_MODEL")
        or DEFAULT_OPENROUTER_MODEL
    )
    return str(configured_model)


def _extract_openrouter_text(response_data: dict) -> str:
    """Trích nội dung trả về từ OpenRouter response."""
    try:
        choices = response_data["choices"]
        if not choices:
            raise ValueError("No choices returned from OpenRouter")

        message = choices[0].get("message", {})
        content = message.get("content")

        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict):
                    text_parts.append(item.get("text", ""))
            return "".join(text_parts).strip()

        if isinstance(content, str):
            return content.strip()

        raise ValueError("Unexpected OpenRouter content format")
    except Exception:
        raise ValueError("Failed to parse OpenRouter response")


def _format_distance(value: object) -> str:
    if value is None:
        return "unavailable"

    try:
        distance = float(value)
    except (TypeError, ValueError):
        return "unavailable"

    if distance.is_integer():
        return f"{int(distance)} cm"

    return f"{distance:.1f} cm"


def _objective_value(objective_condition: Mapping[str, object], key: str) -> str:
    value = objective_condition.get(key)
    return "unavailable" if value is None else str(value)


def build_parking_guidance_prompt(
    sensor_snapshot: Mapping[str, object],
    objective_condition: Mapping[str, object],
    language: str | None,
) -> str:
    """Build guidance instructions from facts already determined by Python."""
    selected_language = normalize_language(language)

    return dedent(
        f"""
        You are an in-car parking guidance assistant.

        Language instruction: {get_llm_instruction(selected_language)}

        Sensor snapshot captured when the driver requested assistance:
        - Left distance: {_format_distance(sensor_snapshot.get('left'))}
        - Center distance: {_format_distance(sensor_snapshot.get('center'))}
        - Right distance: {_format_distance(sensor_snapshot.get('right'))}

        Deterministic objective condition from Python. This is authoritative:
        - Nearest direction: {_objective_value(objective_condition, 'nearest_direction')}
        - Nearest distance: {_format_distance(objective_condition.get('nearest_distance'))}
        - Overall risk level: {_objective_value(objective_condition, 'overall_status')}

        Safety constraints:
        - Give concise, practical parking guidance only.
        - Do not invent obstacle types.
        - Ultrasonic sensors provide only distance and direction context.
        - Do not claim an obstacle is a car, wall, person, vehicle, or any other type.
        - Do not override, reinterpret, or contradict the objective condition supplied by Python.
        - Respond only in the selected language.
        - Avoid unnecessary explanation.
        - Do not include analysis, reasoning, or numbered steps.
        - Provide a short safe driving tips at the end of your response. No need to begin with "Safe Driving Tips", just tell it directly.
        """
    ).strip()


def get_parking_guidance(
    sensor_snapshot: Mapping[str, object],
    objective_condition: Mapping[str, object],
    language: str | None = DEFAULT_LANGUAGE,
) -> str:
    """Request concise guidance without performing sensor analysis in the LLM layer."""
    selected_language = normalize_language(language)
    failure_message = get_ui_text(selected_language, "ai_request_failed")

    try:
        api_key = get_openrouter_api_key()
        if not api_key:
            return failure_message

        prompt = build_parking_guidance_prompt(
            sensor_snapshot,
            objective_condition,
            selected_language,
        )
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "ParkAssist LLM",
        }
        payload = {
            "model": get_openrouter_model(),
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 120,
            "reasoning": {
                "effort": "none",
                "exclude": True,
            },
        }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        reply = _extract_openrouter_text(data)
        return reply.strip() or failure_message
    except Exception:
        return failure_message
