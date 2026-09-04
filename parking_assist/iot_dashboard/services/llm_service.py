import os
from textwrap import dedent
from typing import Mapping

import streamlit as st
import requests

from config.languages import (
    DEFAULT_LANGUAGE,
    get_guidance_template,
    get_llm_instruction,
    normalize_language,
)
from services.situation_service import decide_guidance_category

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_OPENROUTER_MODEL = "nvidia/nemotron-3.5-lightning:free"

CATEGORY_DESCRIPTIONS = {
    "stop": "the obstacle is critically close; tell the driver to stop immediately",
    "correction_maneuver": (
        "the vehicle is too angled for steering alone to fix in the space left; tell the "
        "driver to stop, pull forward a little, straighten the wheel, and reverse again"
    ),
    "steer_left": "tell the driver to steer slightly left while reversing",
    "steer_right": "tell the driver to steer slightly right while reversing",
    "continue_straight": (
        "the vehicle is essentially straight with no urgent issue; tell the driver to "
        "continue reversing steadily (do not invent a steering correction)"
    ),
}


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


def build_parking_guidance_prompt(category: str, language: str | None) -> str:
    """Phrase a category that Python has already decided — never re-derive it here."""
    selected_language = normalize_language(language)

    return dedent(
        f"""
        You are an in-car parking guidance assistant, speaking naturally to the driver
        like a helpful human co-pilot — not a robot reading out rules.

        Language instruction: {get_llm_instruction(selected_language)}

        The instruction to give has already been decided by the sensor-analysis system
        (this is authoritative — do not re-derive, second-guess, or contradict it):
        {CATEGORY_DESCRIPTIONS[category]}.

        Safety constraints:
        - Phrase that exact instruction as ONE short, natural spoken sentence. Vary the
          wording naturally each time rather than sounding robotic.
        - Do not mention specific distances, degrees, or which side (left/right) triggered this.
        - Do not invent obstacle types (car, wall, person, etc.) — ultrasonic sensors only
          provide distance and direction context.
        - Respond only in the selected language.
        - Avoid unnecessary explanation. Do not include analysis, reasoning, or numbered steps.
        - Provide a short safe driving tip at the end of your response. No need to begin with "Safe Driving Tips", just tell it directly.
        """
    ).strip()


def get_parking_guidance(
    sensor_snapshot: Mapping[str, object],
    objective_condition: Mapping[str, object],
    language: str | None = DEFAULT_LANGUAGE,
) -> str:
    """Request concise guidance without performing sensor analysis in the LLM layer."""
    selected_language = normalize_language(language)
    category = decide_guidance_category(
        sensor_snapshot.get("left"),
        sensor_snapshot.get("center"),
        sensor_snapshot.get("right"),
        objective_condition.get("angle_deg"),
    )
    failure_message = get_guidance_template(selected_language, category)

    try:
        api_key = get_openrouter_api_key()
        if not api_key:
            return failure_message

        prompt = build_parking_guidance_prompt(category, selected_language)
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
