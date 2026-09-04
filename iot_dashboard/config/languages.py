from types import MappingProxyType
from typing import Mapping


DEFAULT_LANGUAGE = "English"

SUPPORTED_LANGUAGES = ("English", "Japanese", "Tiếng Việt")

LANGUAGE_CONFIG = MappingProxyType(
    {
        "English": {
            "ui": {
                "current_situation": "Current Situation",
                "vehicle_angle": "Vehicle Angle",
                "ai_suggestion": "AI Suggestion",
                "get_assistance": "Get Assistance",
                "generate_new": "Generate New",
                "change_language": "Change Language",
                "home": "Home",
                "voice_on": "Voice On",
                "voice_off": "Voice Off",
                "choose_language": "Choose your language",
            },
            "sensor_status": {
                "safe": "Safe",
                "warning": "Warning",
                "critical": "Critical",
                "unknown": "Unavailable",
            },
            "directions": {
                "left": "left",
                "center": "center",
                "right": "right",
            },
            "situation_templates": {
                "critical": "Critical obstacle proximity detected on the {direction} side at {distance} cm.",
                "warning": "Warning obstacle proximity detected on the {direction} side at {distance} cm.",
                "safe": "All available obstacle-distance readings are safe. The nearest reading is on the {direction} side at {distance} cm.",
                "unavailable": "Sensor readings are temporarily unavailable.",
            },
            "angle_templates": {
                "straight": "The vehicle is roughly parallel to the surface behind it (~0°).",
                "tilted_right": "Tilted about {angle}° — the rear-right side is closer to the obstacle.",
                "tilted_left": "Tilted about {angle}° — the rear-left side is closer to the obstacle.",
                "unavailable": "Vehicle angle cannot be determined right now.",
            },
            "llm_instruction": (
                "Provide an extremely short, natural driving instruction in English."
            ),
        },
        "Japanese": {
            "ui": {
                "current_situation": "現在の状況",
                "vehicle_angle": "車両の角度",
                "ai_suggestion": "AI提案",
                "get_assistance": "支援を開始",
                "generate_new": "新しく生成",
                "change_language": "言語を変更",
                "home": "ホーム",
                "voice_on": "音声オン",
                "voice_off": "音声オフ",
                "choose_language": "言語を選択してください",
            },
            "sensor_status": {
                "safe": "安全",
                "warning": "注意",
                "critical": "危険",
                "unknown": "利用不可",
            },
            "directions": {
                "left": "左",
                "center": "中央",
                "right": "右",
            },
            "situation_templates": {
                "critical": "{direction}側で{distance}cm先に危険な近接障害物を検知しました。",
                "warning": "{direction}側で{distance}cm先に注意が必要な近接障害物を検知しました。",
                "safe": "利用可能な障害物距離の測定値はすべて安全です。最も近い測定値は{direction}側の{distance}cmです。",
                "unavailable": "センサーの読み取り値を一時的に取得できません。",
            },
            "angle_templates": {
                "straight": "背後の障害物とほぼ平行です(約0°)。",
                "tilted_right": "約{angle}°傾いています(右後方が障害物に近い)。",
                "tilted_left": "約{angle}°傾いています(左後方が障害物に近い)。",
                "unavailable": "現在、車両の角度を計算できません。",
            },
            "llm_instruction": (
                "Provide an extremely short, natural driving instruction in Japanese."
            ),
        },
        "Tiếng Việt": {
            "ui": {
                "current_situation": "Tình huống hiện tại",
                "vehicle_angle": "Góc nghiêng xe",
                "ai_suggestion": "Gợi ý AI",
                "get_assistance": "Nhận hỗ trợ",
                "generate_new": "Tạo mới",
                "change_language": "Đổi ngôn ngữ",
                "home": "Trang chủ",
                "voice_on": "Bật giọng nói",
                "voice_off": "Tắt giọng nói",
                "choose_language": "Chọn ngôn ngữ",
            },
            "sensor_status": {
                "safe": "An toàn",
                "warning": "Cảnh báo",
                "critical": "Nguy hiểm",
                "unknown": "Không khả dụng",
            },
            "directions": {
                "left": "trái",
                "center": "giữa",
                "right": "phải",
            },
            "situation_templates": {
                "critical": "Phát hiện chướng ngại vật ở mức nguy hiểm bên {direction}, cách {distance} cm.",
                "warning": "Phát hiện chướng ngại vật ở mức cảnh báo bên {direction}, cách {distance} cm.",
                "safe": "Các khoảng cách chướng ngại vật hiện có đều an toàn. Giá trị gần nhất là {distance} cm ở bên {direction}.",
                "unavailable": "Tạm thời không có dữ liệu cảm biến.",
            },
            "angle_templates": {
                "straight": "Xe gần như song song với chướng ngại vật phía sau (~0°).",
                "tilted_right": "Lệch khoảng {angle}° — phía sau bên phải xe gần chướng ngại vật hơn.",
                "tilted_left": "Lệch khoảng {angle}° — phía sau bên trái xe gần chướng ngại vật hơn.",
                "unavailable": "Hiện chưa thể xác định góc nghiêng của xe.",
            },
            "llm_instruction": (
                "Provide an extremely short, natural driving instruction in Vietnamese."
            ),
        },
    }
)


def normalize_language(language: str | None) -> str:
    if language in SUPPORTED_LANGUAGES:
        return str(language)

    return DEFAULT_LANGUAGE


def get_language_config(language: str | None) -> Mapping[str, object]:
    return LANGUAGE_CONFIG[normalize_language(language)]


def get_ui_text(language: str | None, key: str) -> str:
    config = get_language_config(language)
    ui_text = config["ui"]

    if isinstance(ui_text, Mapping) and key in ui_text:
        return str(ui_text[key])

    default_ui_text = LANGUAGE_CONFIG[DEFAULT_LANGUAGE]["ui"]
    if isinstance(default_ui_text, Mapping) and key in default_ui_text:
        return str(default_ui_text[key])

    return key


def get_sensor_status_label(language: str | None, status: str) -> str:
    config = get_language_config(language)
    status_labels = config["sensor_status"]

    if isinstance(status_labels, Mapping) and status in status_labels:
        return str(status_labels[status])

    default_status_labels = LANGUAGE_CONFIG[DEFAULT_LANGUAGE]["sensor_status"]
    if isinstance(default_status_labels, Mapping) and status in default_status_labels:
        return str(default_status_labels[status])

    return status


def get_direction_label(language: str | None, direction: str) -> str:
    config = get_language_config(language)
    direction_labels = config["directions"]

    if isinstance(direction_labels, Mapping) and direction in direction_labels:
        return str(direction_labels[direction])

    default_direction_labels = LANGUAGE_CONFIG[DEFAULT_LANGUAGE]["directions"]
    if isinstance(default_direction_labels, Mapping) and direction in default_direction_labels:
        return str(default_direction_labels[direction])

    return direction


def get_situation_template(language: str | None, status: str) -> str:
    config = get_language_config(language)
    templates = config["situation_templates"]

    if isinstance(templates, Mapping) and status in templates:
        return str(templates[status])

    default_templates = LANGUAGE_CONFIG[DEFAULT_LANGUAGE]["situation_templates"]
    if isinstance(default_templates, Mapping) and status in default_templates:
        return str(default_templates[status])

    return str(default_templates["unavailable"])


def get_angle_template(language: str | None, key: str) -> str:
    config = get_language_config(language)
    templates = config["angle_templates"]

    if isinstance(templates, Mapping) and key in templates:
        return str(templates[key])

    default_templates = LANGUAGE_CONFIG[DEFAULT_LANGUAGE]["angle_templates"]
    if isinstance(default_templates, Mapping) and key in default_templates:
        return str(default_templates[key])

    return str(default_templates["unavailable"])


def get_llm_instruction(language: str | None) -> str:
    config = get_language_config(language)
    return str(config["llm_instruction"])
