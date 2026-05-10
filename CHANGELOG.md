# Changelog — J.A.R.V.I.S. Assistant

## [Unreleased] — Major AI Upgrade

### Added
- **OpenRouter Integration** — доступ к облачным моделям (Llama 3.1 405B, DeepSeek Chat, Gemini Flash)
- **Local AI Models (Disk E)** — DeepSeek V3 (48GB), Qwen 2.5 72B (43GB), Llama 3.3 70B (40GB)
- **CHANGELOG.md** — система отслеживания изменений
- **Model Selector in Settings** — выбор между локальными и облачными моделями
- **Test AI Button** — проверка доступности всех провайдеров
- **Animated Avatar** — пульсирующая иконка J.A.R.V.I.S. в GUI
- **Copy-Paste Support** — Ctrl+C/Ctrl+V в чате и поле ввода
- **Mouse Wheel Scrolling** — прокрутка чата колесиком мыши
- **File Creation** — плагин coding теперь реально создает файлы на диске

### Changed
- **Brain System Prompt** — улучшен для развернутых ответов и работы с кодом
- **max_tokens** — увеличен с 256 до 1024 (ответы не обрезаются)
- **Hybrid Router** — приоритет OpenRouter > HF > Ollama для сложных задач
- **Coding Plugin** — создание файлов работает без зависимости от AI
- **GUI** — правый клик по сообщениям для копирования текста

### Removed
- **qwen2.5:0.5b** — удалена как бесполезная модель
- **_is_valid_response** — убран ложный fallback ломавший ответы

## [1.0.0] — Initial Release

### Features
- Voice recognition and synthesis
- Plugin architecture (18 plugins)
- Ollama integration (local AI)
- Hugging Face integration (cloud AI)
- System tray icon
- Settings GUI
- Telegram bot support
- GitHub integration
- Memory system (SQLite + vector)
- Coding assistant

