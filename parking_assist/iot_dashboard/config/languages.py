from types import MappingProxyType
from typing import Mapping


DEFAULT_LANGUAGE = "English"

SUPPORTED_LANGUAGES = ("English",)

LANGUAGE_CONFIG = MappingProxyType(
    {
        "English": {
            "ui": {
                "current_situation": "Current Situation",
                "ai_suggestion": "AI Suggestion",
                "get_assistance": "Get Assistance",
                "generate_new": "Generate New",
                "change_language": "Change Language",
                "home": "Home",
                "voice_on": "Voice On",
                "voice_off": "Voice Off",
                "mute": "Mute",
                "unmute": "Unmute",
                "pause_assistance": "Pause Assistance",
                "resume_assistance": "Resume Assistance",
                "generating_assistance": "Generating assistance",
                "ai_request_failed": "Unable to generate parking assistance right now. Please try again.",
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
            "llm_instruction": (
                "Provide an extremely short, natural driving instruction in English."
            ),
            "speech_locale": "en-US",
        },
        "Japanese": {
            "ui": {
                "current_situation": "現在の状況",
                "ai_suggestion": "AI提案",
                "get_assistance": "支援を開始",
                "generate_new": "新しく生成",
                "change_language": "言語を変更",
                "home": "ホーム",
                "voice_on": "音声オン",
                "voice_off": "音声オフ",
                "mute": "ミュート",
                "unmute": "ミュート解除",
                "pause_assistance": "支援を一時停止",
                "resume_assistance": "支援を再開",
                "generating_assistance": "駐車支援を生成しています...",
                "ai_request_failed": "現在、駐車支援を生成できません。もう一度お試しください。",
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
            "llm_instruction": (
                "Provide an extremely short, natural driving instruction in Japanese."
            ),
            "speech_locale": "ja-JP",
        },
        "Tiếng Việt": {
            "ui": {
                "current_situation": "Tình huống hiện tại",
                "ai_suggestion": "Gợi ý AI",
                "get_assistance": "Nhận hỗ trợ",
                "generate_new": "Tạo mới",
                "change_language": "Đổi ngôn ngữ",
                "home": "Trang chủ",
                "voice_on": "Bật giọng nói",
                "voice_off": "Tắt giọng nói",
                "mute": "Tắt tiếng",
                "unmute": "Bật tiếng",
                "pause_assistance": "Tạm dừng hỗ trợ",
                "resume_assistance": "Tiếp tục hỗ trợ",
                "generating_assistance": "Đang tạo hỗ trợ đỗ xe...",
                "ai_request_failed": "Hiện không thể tạo hỗ trợ đỗ xe. Vui lòng thử lại.",
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
            "llm_instruction": (
                "Provide an extremely short, natural driving instruction in Vietnamese."
            ),
            "speech_locale": "vi-VN",
        },
    }
)


def normalize_language(language: str | None) -> str:
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


def get_llm_instruction(language: str | None) -> str:
    config = get_language_config(language)
    return str(config["llm_instruction"])


def get_speech_locale(language: str | None) -> str:
    config = get_language_config(language)
    locale = config.get("speech_locale")
    if isinstance(locale, str) and locale:
        return locale

    return str(LANGUAGE_CONFIG[DEFAULT_LANGUAGE]["speech_locale"])
