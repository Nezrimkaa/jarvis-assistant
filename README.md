# J.A.R.V.I.S. — Персональный ИИ-ассистент

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)](https://microsoft.com/windows)

**J.A.R.V.I.S.** — умный русскоязычный голосовой ассистент для Windows, вдохновлённый Железным Человеком.

![J.A.R.V.I.S. GUI](assets/screenshot.png)

## Возможности

### Голосовое управление
- Распознавание речи (русский язык)
- Синтез речи (голос J.A.R.V.I.S.)
- Активация по ключевому слову "Джарвис"

### Искусственный интеллект
- **Локальные модели** (Ollama):
  - Qwen 2.5 72B — лучший русский язык
  - Llama 3.1 8B — быстрый fallback
- **Облачные модели** (OpenRouter):
  - Llama 3.1 405B — бесплатно, 405B параметров
  - Gemini 2.0 Flash — бесплатно, быстрая
  - DeepSeek Chat — бесплатно, для кода
  - Claude 3.5 Sonnet — платная, лучшая для кодинга

### Плагины
- Управление системой (громкость, яркость, скриншоты)
- Запуск приложений
- Поиск в интернете
- Работа с файлами и кодом
- GitHub интеграция
- Управление музыкой (Spotify)
- И многое другое

### Интерфейс
- Стиль Железного Человека (J.A.R.V.I.S. UI)
- Анимированный аватар
- Chat-style интерфейс с пузырями сообщений
- Поддержка copy-paste
- Системный трей

## Установка

### 1. Скачайте
```bash
git clone https://github.com/Nezrimkaa/jarvis-assistant.git
cd jarvis-assistant
```

### 2. Установите зависимости
```bash
pip install -r requirements.txt
```

### 3. Установите Ollama
Скачайте с [ollama.com](https://ollama.com) и установите модели:
```bash
ollama pull qwen2.5:72b
ollama pull llama3.1:8b
```

### 4. Настройте окружение
Создайте `.env` файл (или используйте настройки в GUI):
```env
BOT_NAME=Джарвис
AI_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:72b
OPENROUTER_API_KEY=your_key_here  # Опционально
```

### 5. Запустите
```bash
python main.py
```

## Использование

### Голосовые команды
- "Джарвис, привет" — приветствие
- "Джарвис, открой браузер" — запуск приложений
- "Джарвис, найди ..." — поиск в интернете
- "Джарвис, создай файл ..." — создание файлов

### Текстовые команды
- Нажмите Enter или кнопку отправки
- Поддерживается copy-paste (Ctrl+C/Ctrl+V)
- Прокрутка колесиком мыши

### Настройки
Нажмите ⚙ в правом верхнем углу для:
- Выбора AI провайдера (Ollama/OpenRouter)
- Выбора модели
- Настройки голоса
- Включения/отключения функций

## Требования

- Windows 10/11
- Python 3.11+
- 8GB RAM (минимум)
- 16GB RAM (рекомендуется)
- 64GB RAM (для локальных моделей 72B+)
- Микрофон (для голосового ввода)

## Архитектура

```
jarvis-assistant/
├── main.py              # Точка входа
├── config.py            # Конфигурация
├── brain/               # ИИ мозг
│   ├── __init__.py      # Brain (чат, провайдеры)
│   ├── hybrid.py        # Router (Ollama/HF/OpenRouter)
│   └── tool_manager.py  # Function calling
├── plugins/             # Плагины (18 штук)
│   ├── coding.py        # Работа с кодом
│   ├── search.py        # Поиск
│   └── ...
├── gui.py               # Интерфейс (tkinter)
├── voice.py             # Голос (STT/TTS)
├── memory/              # Память (SQLite + vector)
└── .env                 # Настройки
```

## Лицензия

MIT License — см. [LICENSE](LICENSE)

## Автор

**Nezrimkaa** — [GitHub](https://github.com/Nezrimkaa)

---

*"Jarvis, sometimes you gotta run before you can walk."* — Tony Stark
