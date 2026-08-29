import unittest
from unittest.mock import Mock, patch

from services.firebase_service import get_parking_data


class FirebaseServiceTests(unittest.TestCase):
    @patch("services.firebase_service.requests.get")
    @patch("services.firebase_service.firebase_login", return_value="test-token")
    def test_preserves_available_readings_when_one_field_is_missing(
        self,
        _firebase_login: Mock,
        get_request: Mock,
    ) -> None:
        response = Mock()
        response.json.return_value = {"Left": 12, "Center": None, "Right": 45}
        get_request.return_value = response

        self.assertEqual(
            get_parking_data(),
            {"left": 12, "center": None, "right": 45},
        )

    @patch("services.firebase_service.firebase_login", side_effect=RuntimeError)
    def test_returns_unavailable_readings_when_a_poll_fails(
        self,
        _firebase_login: Mock,
    ) -> None:
        self.assertEqual(
            get_parking_data(),
            {"left": None, "center": None, "right": None},
        )


if __name__ == "__main__":
    unittest.main()
