import requests
import streamlit as st


# ========================================
# Firebase configuration
# ========================================

FIREBASE_API_KEY = "AIzaSyBD-PwsaacQq6Ea5F3iZ_Jayie1KOHcFuQ"
FIREBASE_DATABASE_URL = "https://parkassistllm-default-rtdb.asia-southeast1.firebasedatabase.app"

FIREBASE_USER_EMAIL = "gpbl2026group4@parkassistllm.local"
FIREBASE_USER_PASSWORD = "RfQ7W4SmLVLhVpJhEAz3"

FIREBASE_PATH = "Parking/Current"


# ========================================
# Firebase login
# ========================================

@st.cache_resource
def firebase_login():
    """Authenticate with Firebase and return ID token"""
    url = (
        "https://identitytoolkit.googleapis.com/"
        "v1/accounts:signInWithPassword"
        f"?key={FIREBASE_API_KEY}"
    )

    payload = {
        "email": FIREBASE_USER_EMAIL,
        "password": FIREBASE_USER_PASSWORD,
        "returnSecureToken": True
    }

    response = requests.post(
        url,
        json=payload,
        timeout=10
    )

    response.raise_for_status()
    data = response.json()

    return data["idToken"]


# ========================================
# Read parking sensor data
# ========================================

def get_parking_data():
    """Get real-time sensor data from Firebase"""
    try:
        id_token = firebase_login()

        url = (
            f"{FIREBASE_DATABASE_URL}/"
            f"{FIREBASE_PATH}.json"
            f"?auth={id_token}"
        )

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        if data is None:
            raise ValueError("No parking sensor data found.")

        left = data.get("Left")
        center = data.get("Center")
        right = data.get("Right")

        if (
            left is None
            or center is None
            or right is None
        ):
            raise ValueError("Sensor data is missing.")

        return {
            "left": left,
            "center": center,
            "right": right
        }

    except Exception as e:
        st.error(f"Firebase Error: {str(e)}")
        # Return default data if Firebase fails
        return {
            "left": 30,
            "center": 30,
            "right": 30
        }
