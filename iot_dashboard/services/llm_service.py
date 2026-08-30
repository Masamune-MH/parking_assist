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


def get_parking_guidance(left: float, center: float, right: float, language: str = "Tiếng Việt") -> str:
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

    prompt = f"""
    You are a professional in-car parking and driving assistant sitting in the passenger seat.
    Real-time rear sensor distance data:
    - Left: {left} cm
    - Center: {center} cm
    - Right: {right} cm

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