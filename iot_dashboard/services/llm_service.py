import os
import streamlit as st
import requests

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "google/gemini-3.6-flash"


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
    Xử lý dữ liệu cảm biến và tạo câu lệnh chỉ dẫn bằng AI theo ngôn ngữ được chọn.
    Dùng OpenRouter API thay vì Google Gemini SDK để tương thích với key OpenRouter.
    """
    default_responses = {
        "English": "Reverse slowly while monitoring the distance.",
        "Japanese": "ゆっくり後退してください。",
        "Tiếng Việt": "Lùi xe chậm và theo dõi khoảng cách."
    }

    api_key = get_openrouter_api_key()
    if not api_key:
        return default_responses.get(language, "Unable to process at this time.")

    if angle_deg is None:
        angle_context = "Estimated vehicle tilt: unknown."
    elif abs(angle_deg) < 3:
        angle_context = "Estimated vehicle tilt: roughly parallel to the obstacle behind it."
    else:
        tilt_side = "right" if angle_deg > 0 else "left"
        angle_context = (
            f"Estimated vehicle tilt: about {abs(angle_deg):.1f} degrees, "
            f"with the rear-{tilt_side} side closer to the obstacle behind it."
        )

    prompt = f"""
    You are a professional in-car parking and driving assistant sitting in the passenger seat.
    Real-time rear sensor distance data:
    - Left: {left} cm
    - Center: {center} cm
    - Right: {right} cm
    - {angle_context}

    Decide the single most useful instruction to say right now:
    - If the tilt is small (under ~10 degrees) and there is enough clearance on all sides, give a short steering correction (e.g. steer slightly left/right while reversing).
    - If the tilt is large (roughly 15 degrees or more) and the near side is getting close (under ~15 cm), steering alone will not straighten the car out in the remaining space. In that case, tell the driver to stop, pull forward a little, straighten the wheel, and reverse again to correct the angle (a correction maneuver / 切り返し), instead of just telling them to keep steering.
    - If any side is critically close (under ~10 cm) regardless of angle, prioritize telling the driver to stop immediately.

    Requirement: Provide an extremely short, natural driving instruction sentence spoken directly to the driver in this exact language: {language}.
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
        return reply.strip() or default_responses.get(language, "Unable to process at this time.")
    except Exception:
        return default_responses.get(language, "Unable to process at this time.")