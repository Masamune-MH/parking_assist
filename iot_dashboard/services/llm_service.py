import os
import streamlit as st
import requests

from services.situation_service import (
    GUIDANCE_CONTINUE_STRAIGHT,
    GUIDANCE_CORRECTION_MANEUVER,
    GUIDANCE_STEER_LEFT,
    GUIDANCE_STEER_RIGHT,
    GUIDANCE_STOP,
    decide_guidance_category,
)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "google/gemini-3.6-flash"

# Fallback text used when there's no API key and as a safety net if the LLM
# call fails outright. The LLM's job is only to phrase these more naturally.
CATEGORY_DEFAULT_RESPONSES = {
    GUIDANCE_STOP: {
        "English": "Stop now, you're very close to an obstacle.",
        "Japanese": "今すぐ停止してください。障害物にとても近づいています。",
        "Tiếng Việt": "Dừng lại ngay, bạn đang rất gần chướng ngại vật.",
    },
    GUIDANCE_CORRECTION_MANEUVER: {
        "English": "Stop, pull forward a little, straighten the wheel, and reverse again.",
        "Japanese": "一度停止して少し前に進み、ハンドルを戻してからもう一度バックしてください。",
        "Tiếng Việt": "Dừng lại, tiến lên một chút, đánh thẳng vô-lăng rồi lùi lại.",
    },
    GUIDANCE_STEER_LEFT: {
        "English": "Steer slightly left while reversing.",
        "Japanese": "ハンドルを少し左に切りながら下がってください。",
        "Tiếng Việt": "Đánh nhẹ vô-lăng sang trái trong khi lùi.",
    },
    GUIDANCE_STEER_RIGHT: {
        "English": "Steer slightly right while reversing.",
        "Japanese": "ハンドルを少し右に切りながら下がってください。",
        "Tiếng Việt": "Đánh nhẹ vô-lăng sang phải trong khi lùi.",
    },
    GUIDANCE_CONTINUE_STRAIGHT: {
        "English": "Looking good, continue reversing slowly and steadily.",
        "Japanese": "良い状態です。そのままゆっくり下がってください。",
        "Tiếng Việt": "Ổn rồi, tiếp tục lùi chậm và đều.",
    },
}

CATEGORY_DESCRIPTIONS = {
    GUIDANCE_STOP: "the obstacle is critically close; tell the driver to stop immediately",
    GUIDANCE_CORRECTION_MANEUVER: (
        "the vehicle is too angled for steering alone to fix in the space left; tell the "
        "driver to stop, pull forward a little, straighten the wheel, and reverse again"
    ),
    GUIDANCE_STEER_LEFT: "tell the driver to steer slightly left while reversing",
    GUIDANCE_STEER_RIGHT: "tell the driver to steer slightly right while reversing",
    GUIDANCE_CONTINUE_STRAIGHT: (
        "the vehicle is essentially straight with no urgent issue; tell the driver to "
        "continue reversing steadily (do not invent a steering correction)"
    ),
}


@st.cache_resource
def get_openrouter_api_key() -> str | None:
    """Lấy API key OpenRouter từ Streamlit secrets hoặc biến môi trường."""
    api_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    return api_key or None


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


def get_parking_guidance(
    left: float,
    center: float,
    right: float,
    language: str = "Tiếng Việt",
    angle_deg: float | None = None,
) -> str:
    """
    Decide *what* the driver needs to hear deterministically (see
    situation_service.decide_guidance_category), then ask the LLM only to
    phrase that decision as one natural, spoken sentence — the LLM does not
    re-derive the decision itself, so its output stays predictable even
    though the wording varies.
    """
    category = decide_guidance_category(left, center, right, angle_deg)
    default_text = CATEGORY_DEFAULT_RESPONSES[category].get(
        language, CATEGORY_DEFAULT_RESPONSES[category]["English"]
    )

    api_key = get_openrouter_api_key()
    if not api_key:
        return default_text

    prompt = f"""
    You are a friendly in-car parking assistant speaking naturally to the driver,
    like a helpful human co-pilot — not a robot reading out rules.

    The instruction to give has already been decided: {CATEGORY_DESCRIPTIONS[category]}.

    Task: phrase that exact instruction as ONE short, natural spoken sentence in
    {language}. Vary the wording naturally each time rather than sounding robotic.
    Do NOT mention specific distances, degrees, or which side (left/right) triggered
    this — just give the plain instruction itself, nothing else.
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "ParkAssist LLM",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        reply = _extract_openrouter_text(data)
        return reply.strip() or default_text
    except Exception:
        return default_text