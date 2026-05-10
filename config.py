"""Конфигурация J.A.R.V.I.S. — загрузка из .env файла."""
import os

from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()


class Config:
    """Конфигурация приложения."""

    # === Общие настройки ===
    BOT_NAME: str = os.getenv("BOT_NAME", "Джарвис")
    VOICE_ENABLED: bool = os.getenv("VOICE_ENABLED", "true").lower() == "true"
    VOICE_RESPONSES_ENABLED: bool = os.getenv("VOICE_RESPONSES_ENABLED", "true").lower() == "true"
    VOICE_GENDER: str = os.getenv("VOICE_GENDER", "male")

    # === AI Провайдер ===
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "ollama")

    # Ollama (локальная, бесплатная)
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:4b")

    # Hugging Face Inference API (бесплатный tier, глобально доступен)
    HF_API_KEY: str = os.getenv("HF_API_KEY", "")
    HF_MODEL: str = os.getenv("HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")
    HF_BASE_URL: str = os.getenv("HF_BASE_URL", "https://router.huggingface.co/v1")

    # OpenRouter (бесплатный tier с Llama 3.1 70B, Mistral и др.)
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-70b-instruct:free")

    # === Telegram ===
    TELEGRAM_ENABLED: bool = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")

    # === Прокси ===
    PROXY_URL: str = os.getenv("PROXY_URL", "")

    # === Wake Word ===
    WAKE_WORD_ENABLED: bool = os.getenv("WAKE_WORD_ENABLED", "true").lower() == "true"
    WAKE_WORD_COOLDOWN: float = float(os.getenv("WAKE_WORD_COOLDOWN", "4.0"))

    # === Tray ===
    TRAY_ENABLED: bool = os.getenv("TRAY_ENABLED", "true").lower() == "true"

    # === Autostart ===
    AUTOSTART_ENABLED: bool = os.getenv("AUTOSTART_ENABLED", "false").lower() == "true"

    # === GUI ===
    WINDOW_WIDTH: int = int(os.getenv("WINDOW_WIDTH", "500"))
    WINDOW_HEIGHT: int = int(os.getenv("WINDOW_HEIGHT", "750"))
    WINDOW_MIN_WIDTH: int = int(os.getenv("WINDOW_MIN_WIDTH", "400"))
    WINDOW_MIN_HEIGHT: int = int(os.getenv("WINDOW_MIN_HEIGHT", "500"))

    @classmethod
    def reload(cls):
        """Перезагрузить конфигурацию из .env."""
        load_dotenv(override=True)
        for key in dir(cls):
            if key.startswith("_"):
                continue
            value = os.getenv(key)
            if value is not None:
                current = getattr(cls, key)
                if isinstance(current, bool):
                    setattr(cls, key, value.lower() == "true")
                elif isinstance(current, int):
                    setattr(cls, key, int(value))
                elif isinstance(current, float):
                    setattr(cls, key, float(value))
                else:
                    setattr(cls, key, value)
