import requests


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

def firebase_login():

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

def get_parking_data(id_token):

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

        raise ValueError(
            "No parking sensor data found."
        )


    left = data.get("Left")
    center = data.get("Center")
    right = data.get("Right")


    if (
        left is None
        or center is None
        or right is None
    ):

        raise ValueError(
            "Sensor data is missing."
        )


    return {
        "left": left,
        "center": center,
        "right": right
    }


# ========================================
# Test
# ========================================

if __name__ == "__main__":

    try:

        token = firebase_login()

        sensor_data = get_parking_data(
            token
        )


        print(
            "Parking sensor data:"
        )

        print(sensor_data)


        print(
            f"Left: {sensor_data['left']} cm | "
            f"Center: {sensor_data['center']} cm | "
            f"Right: {sensor_data['right']} cm"
        )


        # Show sensor errors clearly
        if sensor_data["left"] == -1:
            print(
                "Warning: Left sensor did not receive an echo."
            )

        if sensor_data["center"] == -1:
            print(
                "Warning: Center sensor did not receive an echo."
            )

        if sensor_data["right"] == -1:
            print(
                "Warning: Right sensor did not receive an echo."
            )


    except Exception as e:

        print(
            "Error:",
            e
        )