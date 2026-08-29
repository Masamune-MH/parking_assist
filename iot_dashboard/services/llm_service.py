import os
import streamlit as st
import google.generativeai as genai

@st.cache_resource
def get_gemini_client():
    """Khởi tạo client Gemini một lần duy nhất bằng API key từ st.secrets hoặc environment variables"""
    api_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        # Return None instead of raising error
        return None
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.5-flash')
    except:
        return None

def get_parking_guidance(left: float, center: float, right: float, language: str = "Tiếng Việt") -> str:
    """
    Xử lý dữ liệu cảm biến và tạo câu lệnh chỉ dẫn bằng AI theo ngôn ngữ được chọn.
    """
    # Default responses by language
    default_responses = {
        "English": "Reverse slowly while monitoring the distance.",
        "Japanese": "ゆっくり後退してください。",
        "Tiếng Việt": "Lùi xe chậm và theo dõi khoảng cách."
    }
    
    try:
        client = get_gemini_client()
        
        prompt = f"""
        You are a professional in-car parking and driving assistant sitting in the passenger seat.
        Real-time rear sensor distance data:
        - Left: {left} cm
        - Center: {center} cm
        - Right: {right} cm
        
        Requirement: Provide an extremely short, natural driving instruction sentence spoken directly to the driver in this exact language: {language}.
        """
        
        response = client.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # Return default response instead of error
        return default_responses.get(language, "Unable to process at this time.")