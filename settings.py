"""Окно настроек J.A.R.V.I.S. — расширенная версия."""
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Callable

from config import Config


class SettingsWindow:
    """Расширенное окно настроек J.A.R.V.I.S."""

    BG = "#0a0e14"
    BG_SECONDARY = "#111820"
    ACCENT = "#00d4ff"
    ACCENT_HOVER = "#00a8cc"
    TEXT_PRIMARY = "#e0f7ff"
    TEXT_SECONDARY = "#6b8fa3"
    INPUT_BG = "#1a2332"
    BORDER = "#00d4ff"
    BORDER_DIM = "#1a3a4a"

    def __init__(self, voice, on_save: Callable = None):
        self.voice = voice
        self.on_save = on_save
        self.window = None

    def show(self):
        """Показать окно настроек."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel()
        self.window.title(f"{Config.BOT_NAME} — Настройки")
        self.window.geometry("500x700")
        self.window.configure(bg=self.BG)
        self.window.resizable(True, True)
        self.window.transient()
        self.window.grab_set()

        # Основной контейнер
        main = tk.Frame(self.window, bg=self.BG, highlightbackground=self.BORDER, highlightthickness=2)
        main.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Заголовок
        header = tk.Frame(main, bg=self.BG_SECONDARY, height=50)
        header.pack(fill=tk.X, padx=4, pady=(4, 0))
        header.pack_propagate(False)

        tk.Label(
            header,
            text="⚙ Настройки J.A.R.V.I.S.",
            font=("Segoe UI", 14, "bold"),
            fg=self.TEXT_PRIMARY,
            bg=self.BG_SECONDARY,
        ).pack(side=tk.LEFT, padx=15, pady=10)

        # Canvas с прокруткой
        canvas = tk.Canvas(main, bg=self.BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(main, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=460)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 4))

        # === Раздел: AI Провайдер ===
        self._add_section(scrollable_frame, "🧠 Искусственный интеллект")

        tk.Label(
            scrollable_frame,
            text="Провайдер ИИ:",
            font=("Segoe UI", 10),
            fg=self.TEXT_SECONDARY,
            bg=self.BG,
        ).pack(anchor="w", padx=15, pady=(5, 0))

        self.ai_provider = tk.StringVar(value=Config.AI_PROVIDER)
        provider_combo = ttk.Combobox(
            scrollable_frame,
            textvariable=self.ai_provider,
            values=["ollama", "hf", "openrouter"],
            state="readonly",
            width=20,
        )
        provider_combo.pack(anchor="w", padx=15, pady=5)

        # Qwen/Ollama настройки
        self._add_checkbox(scrollable_frame, "Использовать локальную модель (Ollama/Qwen)", 
                          tk.BooleanVar(value=(Config.AI_PROVIDER == "ollama")))

        tk.Label(
            scrollable_frame,
            text="Модель Ollama:",
            font=("Segoe UI", 10),
            fg=self.TEXT_SECONDARY,
            bg=self.BG,
        ).pack(anchor="w", padx=15, pady=(10, 0))

        self.ollama_model = tk.StringVar(value=Config.OLLAMA_MODEL)
        ollama_entry = tk.Entry(
            scrollable_frame,
            textvariable=self.ollama_model,
            font=("Segoe UI", 10),
            bg=self.INPUT_BG,
            fg=self.TEXT_PRIMARY,
            insertbackground=self.ACCENT,
            width=30,
        )
        ollama_entry.pack(anchor="w", padx=15, pady=5)

        # API Keys (бесплатные)
        self._add_section(scrollable_frame, "🔑 API Ключи (бесплатные)")

        tk.Label(
            scrollable_frame,
            text="Hugging Face API Key (бесплатно):",
            font=("Segoe UI", 10),
            fg=self.TEXT_SECONDARY,
            bg=self.BG,
        ).pack(anchor="w", padx=15, pady=(5, 0))

        self.hf_key = tk.StringVar(value=Config.HF_API_KEY)
        hf_entry = tk.Entry(
            scrollable_frame,
            textvariable=self.hf_key,
            font=("Segoe UI", 10),
            bg=self.INPUT_BG,
            fg=self.TEXT_PRIMARY,
            insertbackground=self.ACCENT,
            width=40,
        )
        hf_entry.pack(anchor="w", padx=15, pady=5)
        
        # Context menu for paste
        def show_context_menu(event):
            menu = tk.Menu(hf_entry, tearoff=0)
            menu.add_command(label="Paste", command=lambda: paste_from_clipboard())
            menu.post(event.x_root, event.y_root)
        
        def paste_from_clipboard():
            try:
                text = hf_entry.clipboard_get()
                current = self.hf_key.get()
                hf_entry.insert(tk.INSERT, text)
            except tk.TclError:
                pass
        
        hf_entry.bind("<Button-3>", show_context_menu)  # Right-click
        
        # Also try Shift+Insert (standard paste on Windows)
        def shift_insert(event):
            try:
                text = hf_entry.clipboard_get()
                hf_entry.insert(tk.INSERT, text)
                return "break"
            except tk.TclError:
                pass
        hf_entry.bind("<Shift-Insert>", shift_insert)
        
        # And Ctrl+V with focus check
        def ctrl_v(event):
            if hf_entry.focus_get() == hf_entry:
                try:
                    text = hf_entry.clipboard_get()
                    hf_entry.insert(tk.INSERT, text)
                    return "break"
                except tk.TclError:
                    pass
        hf_entry.bind("<Control-v>", ctrl_v)
        hf_entry.bind("<Control-V>", ctrl_v)
        
        # OpenRouter API Key
        tk.Label(
            scrollable_frame,
            text="OpenRouter API Key (бесплатно — Llama 3.1 70B!):",
            font=("Segoe UI", 10),
            fg=self.TEXT_SECONDARY,
            bg=self.BG,
        ).pack(anchor="w", padx=15, pady=(15, 0))
        
        self.openrouter_key = tk.StringVar(value=getattr(Config, 'OPENROUTER_API_KEY', ''))
        or_entry = tk.Entry(
            scrollable_frame,
            textvariable=self.openrouter_key,
            font=("Segoe UI", 10),
            bg=self.INPUT_BG,
            fg=self.TEXT_PRIMARY,
            insertbackground=self.ACCENT,
            width=40,
        )
        or_entry.pack(anchor="w", padx=15, pady=5)
        
        # OpenRouter model selector
        tk.Label(
            scrollable_frame,
            text="OpenRouter Модель:",
            font=("Segoe UI", 10),
            fg=self.TEXT_SECONDARY,
            bg=self.BG,
        ).pack(anchor="w", padx=15, pady=(10, 0))
        
        self.openrouter_model = tk.StringVar(value=getattr(Config, 'OPENROUTER_MODEL', 'meta-llama/llama-3.1-405b-instruct:free'))
        or_model_combo = ttk.Combobox(
            scrollable_frame,
            textvariable=self.openrouter_model,
            values=[
                "meta-llama/llama-3.1-405b-instruct:free",
                "google/gemini-2.0-flash-exp:free",
                "deepseek/deepseek-chat:free",
                "anthropic/claude-3.5-sonnet (платная)",
                "anthropic/claude-3-opus (платная)",
                "openai/gpt-4o (платная)",
            ],
            state="readonly",
            width=45,
        )
        or_model_combo.pack(anchor="w", padx=15, pady=5)
        
        # Test AI Button
        test_btn = tk.Button(
            scrollable_frame,
            text="🧪 Тест AI",
            command=self._test_ai,
            font=("Segoe UI", 10, "bold"),
            bg=self.ACCENT,
            fg="black",
            activebackground=self.ACCENT_HOVER,
            activeforeground="black",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=5,
        )
        test_btn.pack(anchor="w", padx=15, pady=(10, 5))

        # === Раздел: Голос ===
        self._add_section(scrollable_frame, "🔊 Голос")

        self.voice_enabled = tk.BooleanVar(value=Config.VOICE_ENABLED)
        self._add_checkbox(scrollable_frame, "Включить голосовой вывод", self.voice_enabled)

        self.voice_responses_enabled = tk.BooleanVar(value=Config.VOICE_RESPONSES_ENABLED)
        self._add_checkbox(scrollable_frame, "Озвучивать ответы голосом", self.voice_responses_enabled)

        tk.Label(
            scrollable_frame,
            text="Голос:",
            font=("Segoe UI", 10),
            fg=self.TEXT_SECONDARY,
            bg=self.BG,
        ).pack(anchor="w", padx=15, pady=(10, 0))

        self.voice_gender = tk.StringVar(value=Config.VOICE_GENDER)
        voice_combo = ttk.Combobox(
            scrollable_frame,
            textvariable=self.voice_gender,
            values=["male", "female", "jarvis"],
            state="readonly",
            width=20,
        )
        voice_combo.pack(anchor="w", padx=15, pady=5)

        # === Раздел: Микрофон ===
        self._add_section(scrollable_frame, "🎤 Микрофон")

        tk.Label(
            scrollable_frame,
            text="Устройство записи:",
            font=("Segoe UI", 10),
            fg=self.TEXT_SECONDARY,
            bg=self.BG,
        ).pack(anchor="w", padx=15, pady=(5, 0))

        self.mic_var = tk.StringVar()
        mics = self.voice.get_microphones()
        mic_names = [f"{m['index']}: {m['name']}" for m in mics] if mics else ["Микрофоны не найдены"]
        
        self.mic_combo = ttk.Combobox(
            scrollable_frame,
            textvariable=self.mic_var,
            values=mic_names,
            state="readonly",
            width=40,
        )
        self.mic_combo.pack(anchor="w", padx=15, pady=5)
        if mic_names:
            self.mic_combo.current(0)

        # Кнопка теста
        test_btn = tk.Label(
            scrollable_frame,
            text="▶ Тестировать микрофон",
            font=("Segoe UI", 10),
            fg=self.ACCENT,
            bg=self.BG,
            cursor="hand2",
        )
        test_btn.pack(anchor="w", padx=15, pady=5)
        test_btn.bind("<Button-1>", lambda e: self._test_microphone())
        test_btn.bind("<Enter>", lambda e: test_btn.config(fg=self.ACCENT_HOVER))
        test_btn.bind("<Leave>", lambda e: test_btn.config(fg=self.ACCENT))

        self.mic_status = tk.Label(
            scrollable_frame,
            text="",
            font=("Segoe UI", 9),
            fg=self.TEXT_SECONDARY,
            bg=self.BG,
        )
        self.mic_status.pack(anchor="w", padx=15, pady=(0, 10))

        # === Раздел: Wake Word ===
        self._add_section(scrollable_frame, "👂 Голосовая активация")

        self.wake_enabled = tk.BooleanVar(value=Config.WAKE_WORD_ENABLED)
        self._add_checkbox(scrollable_frame, "Включить активацию 'Джарвис'", self.wake_enabled)

        tk.Label(
            scrollable_frame,
            text="Чувствительность (сек):",
            font=("Segoe UI", 10),
            fg=self.TEXT_SECONDARY,
            bg=self.BG,
        ).pack(anchor="w", padx=15, pady=(5, 0))

        self.wake_cooldown = tk.DoubleVar(value=Config.WAKE_WORD_COOLDOWN)
        cooldown_scale = tk.Scale(
            scrollable_frame,
            from_=2.0,
            to=10.0,
            resolution=0.5,
            orient=tk.HORIZONTAL,
            variable=self.wake_cooldown,
            bg=self.BG,
            fg=self.TEXT_PRIMARY,
            highlightthickness=0,
            troughcolor=self.INPUT_BG,
            activebackground=self.ACCENT,
            length=200,
        )
        cooldown_scale.pack(anchor="w", padx=15, pady=5)

        # === Раздел: Настроение ===
        self._add_section(scrollable_frame, "😊 Настроение")

        tk.Label(
            scrollable_frame,
            text="Стиль общения:",
            font=("Segoe UI", 10),
            fg=self.TEXT_SECONDARY,
            bg=self.BG,
        ).pack(anchor="w", padx=15, pady=(5, 0))

        self.mood = tk.StringVar(value="neutral")
        mood_combo = ttk.Combobox(
            scrollable_frame,
            textvariable=self.mood,
            values=["neutral", "friendly", "strict", "humorous", "formal"],
            state="readonly",
            width=20,
        )
        mood_combo.pack(anchor="w", padx=15, pady=5)

        # === Раздел: Автозапуск ===
        self._add_section(scrollable_frame, "🚀 Автозапуск")

        self.autostart_enabled = tk.BooleanVar(value=Config.AUTOSTART_ENABLED)
        self._add_checkbox(scrollable_frame, "Запускать с Windows", self.autostart_enabled)

        # === Раздел: Разработка ===
        self._add_section(scrollable_frame, "💻 Разработка")

        self.dev_mode = tk.BooleanVar(value=False)
        self._add_checkbox(scrollable_frame, "Режим разработчика (доступ к коду)", self.dev_mode)

        # === Раздел: Самоулучшение ===
        self._add_section(scrollable_frame, "🔄 Самоулучшение")

        self.self_improve = tk.BooleanVar(value=False)
        self._add_checkbox(scrollable_frame, "Автоматически улучшать ответы", self.self_improve)

        tk.Label(
            scrollable_frame,
            text="История обучения:",
            font=("Segoe UI", 10),
            fg=self.TEXT_SECONDARY,
            bg=self.BG,
        ).pack(anchor="w", padx=15, pady=(5, 0))

        self.learning_text = scrolledtext.ScrolledText(
            scrollable_frame,
            wrap=tk.WORD,
            width=50,
            height=4,
            font=("Consolas", 9),
            bg=self.INPUT_BG,
            fg=self.TEXT_PRIMARY,
            insertbackground=self.ACCENT,
        )
        self.learning_text.pack(anchor="w", padx=15, pady=5)
        self.learning_text.insert(tk.END, "// Здесь можно добавить свои шаблоны ответов\n")
        self.learning_text.config(state=tk.DISABLED)

        # === Кнопки ===
        buttons_frame = tk.Frame(main, bg=self.BG, pady=15)
        buttons_frame.pack(fill=tk.X, padx=4, pady=(0, 4))

        save_btn = tk.Label(
            buttons_frame,
            text="💾 Сохранить",
            font=("Segoe UI", 11, "bold"),
            fg=self.BG,
            bg=self.ACCENT,
            cursor="hand2",
            padx=20,
            pady=8,
        )
        save_btn.pack(side=tk.LEFT, padx=(15, 10))
        save_btn.bind("<Button-1>", lambda e: self._save_settings())
        save_btn.bind("<Enter>", lambda e: save_btn.config(bg=self.ACCENT_HOVER))
        save_btn.bind("<Leave>", lambda e: save_btn.config(bg=self.ACCENT))

        cancel_btn = tk.Label(
            buttons_frame,
            text="❌ Отмена",
            font=("Segoe UI", 11),
            fg=self.TEXT_SECONDARY,
            bg=self.BG_SECONDARY,
            cursor="hand2",
            padx=20,
            pady=8,
        )
        cancel_btn.pack(side=tk.LEFT)
        cancel_btn.bind("<Button-1>", lambda e: self.window.destroy())
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(fg=self.TEXT_PRIMARY))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(fg=self.TEXT_SECONDARY))

    def _add_section(self, parent, title: str):
        """Добавить заголовок раздела."""
        frame = tk.Frame(parent, bg=self.BG, pady=10)
        frame.pack(fill=tk.X, padx=10)

        tk.Label(
            frame,
            text=title,
            font=("Segoe UI", 12, "bold"),
            fg=self.ACCENT,
            bg=self.BG,
        ).pack(anchor="w")

        line = tk.Frame(parent, bg=self.BORDER_DIM, height=1)
        line.pack(fill=tk.X, padx=15, pady=(0, 5))

    def _add_checkbox(self, parent, text: str, var):
        """Добавить чекбокс."""
        cb = tk.Checkbutton(
            parent,
            text=text,
            variable=var,
            font=("Segoe UI", 10),
            fg=self.TEXT_PRIMARY,
            bg=self.BG,
            selectcolor=self.INPUT_BG,
            activebackground=self.BG,
            activeforeground=self.TEXT_PRIMARY,
        )
        cb.pack(anchor="w", padx=15, pady=5)

    def _test_microphone(self):
        """Тестировать микрофон."""
        self.mic_status.config(text="Тестирование...", fg=self.ACCENT)
        self.window.update()
        
        success, message = self.voice.test_microphone()
        
        if success:
            self.mic_status.config(text=f"✓ {message}", fg="#34C759")
        else:
            self.mic_status.config(text=f"✗ {message}", fg="#ff4444")

    def _test_ai(self):
        """Тестировать AI подключение."""
        import requests
        import threading
        
        def test():
            results = []
            
            # Test Ollama
            try:
                resp = requests.get(f"{Config.OLLAMA_URL}/api/tags", timeout=3)
                if resp.status_code == 200:
                    models = [m['name'] for m in resp.json().get('models', [])]
                    results.append(f"✓ Ollama: Работает\n   Модели: {', '.join(models[:3])}")
                else:
                    results.append(f"✗ Ollama: Ошибка {resp.status_code}")
            except Exception as e:
                results.append(f"✗ Ollama: {str(e)[:50]}")
            
            # Test Hugging Face
            if Config.HF_API_KEY:
                try:
                    import openai
                    client = openai.OpenAI(
                        api_key=Config.HF_API_KEY,
                        base_url=Config.HF_BASE_URL,
                    )
                    # Just test the connection with a simple request
                    resp = requests.get(f"{Config.HF_BASE_URL}/models", 
                                       headers={"Authorization": f"Bearer {Config.HF_API_KEY}"},
                                       timeout=5)
                    if resp.status_code == 200:
                        results.append(f"✓ Hugging Face: API Key работает")
                    else:
                        results.append(f"✗ Hugging Face: Ошибка {resp.status_code}")
                except Exception as e:
                    results.append(f"✗ Hugging Face: {str(e)[:50]}")
            else:
                results.append("○ Hugging Face: API Key не указан")
            
            # Test OpenRouter
            if Config.OPENROUTER_API_KEY:
                try:
                    resp = requests.get("https://openrouter.ai/api/v1/auth/key",
                                       headers={"Authorization": f"Bearer {Config.OPENROUTER_API_KEY}"},
                                       timeout=5)
                    if resp.status_code == 200:
                        data = resp.json()
                        results.append(f"✓ OpenRouter: Работает\n   Модель: {Config.OPENROUTER_MODEL}")
                    else:
                        results.append(f"✗ OpenRouter: Ошибка {resp.status_code}")
                except Exception as e:
                    results.append(f"✗ OpenRouter: {str(e)[:50]}")
            else:
                results.append("○ OpenRouter: API Key не указан (рекомендуется!)")
            
            # Show results
            result_text = "\n\n".join(results)
            self.window.after(0, lambda: messagebox.showinfo("Тест AI", result_text))
        
        # Run test in background
        thread = threading.Thread(target=test)
        thread.daemon = True
        thread.start()

    def _save_settings(self):
        """Сохранить настройки."""
        # Микрофон
        mic_selection = self.mic_var.get()
        if mic_selection and ":" in mic_selection:
            try:
                device_index = int(mic_selection.split(":")[0])
                self.voice.set_microphone(device_index)
            except:
                pass

        # AI Provider
        Config.AI_PROVIDER = self.ai_provider.get()
        Config.OLLAMA_MODEL = self.ollama_model.get()
        Config.HF_API_KEY = self.hf_key.get()
        Config.OPENROUTER_API_KEY = self.openrouter_key.get()
        Config.OPENROUTER_MODEL = self.openrouter_model.get()
        
        # Голос
        Config.VOICE_ENABLED = self.voice_enabled.get()
        Config.VOICE_RESPONSES_ENABLED = self.voice_responses_enabled.get()
        Config.VOICE_GENDER = self.voice_gender.get()
        
        # Wake word
        Config.WAKE_WORD_ENABLED = self.wake_enabled.get()
        Config.WAKE_WORD_COOLDOWN = self.wake_cooldown.get()
        
        # Автозапуск
        Config.AUTOSTART_ENABLED = self.autostart_enabled.get()

        # Сохраняем в .env
        self._save_to_env()

        messagebox.showinfo("Настройки", "Настройки сохранены!")
        
        if self.on_save:
            self.on_save()
        
        self.window.destroy()

    def _save_to_env(self):
        """Сохранить настройки в .env файл."""
        try:
            env_path = ".env"
            lines = []
            
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            
            settings = {
                "VOICE_ENABLED": str(Config.VOICE_ENABLED).lower(),
                "VOICE_RESPONSES_ENABLED": str(Config.VOICE_RESPONSES_ENABLED).lower(),
                "VOICE_GENDER": Config.VOICE_GENDER,
                "WAKE_WORD_ENABLED": str(Config.WAKE_WORD_ENABLED).lower(),
                "WAKE_WORD_COOLDOWN": str(Config.WAKE_WORD_COOLDOWN),
                "AI_PROVIDER": Config.AI_PROVIDER,
                "OLLAMA_MODEL": Config.OLLAMA_MODEL,
                "HF_API_KEY": Config.HF_API_KEY,
                "OPENROUTER_API_KEY": getattr(Config, 'OPENROUTER_API_KEY', ''),
                "OPENROUTER_MODEL": getattr(Config, 'OPENROUTER_MODEL', 'meta-llama/llama-3.1-70b-instruct:free'),
                "AUTOSTART_ENABLED": str(Config.AUTOSTART_ENABLED).lower(),
            }
            
            new_lines = []
            updated = set()
            
            for line in lines:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key = line.split("=")[0]
                    if key in settings:
                        new_lines.append(f"{key}={settings[key]}\n")
                        updated.add(key)
                    else:
                        new_lines.append(line + "\n")
                else:
                    new_lines.append(line + "\n")
            
            for key, value in settings.items():
                if key not in updated:
                    new_lines.append(f"{key}={value}\n")
            
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
                
        except Exception as e:
            print(f"[Settings] Ошибка сохранения: {e}")
