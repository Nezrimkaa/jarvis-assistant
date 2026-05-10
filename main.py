"""J.A.R.V.I.S. — Персональный ИИ-ассистент для ПК.

Точка входа. Запуск:
    python main.py
"""
import re
import subprocess
import time
import threading
from typing import Optional

import requests

from config import Config
from brain import Brain
from voice import Voice
from commands import SystemCommands
from gui import JarvisGUI
from wake_word import WakeWordListener
from tray import TrayIcon
from autostart import enable_startup, disable_startup, is_startup_enabled
from sounds import play_startup_music, play_wake_sound, play_success_sound, play_error_sound
from settings import SettingsWindow
from coding import CodingAssistant
from coding_enhanced import EnhancedCodingAssistant
from plugins import PluginRegistry


import os
import glob

def find_ollama_exe():
    """Найти путь к ollama.exe автоматически."""
    # Возможные пути установки Ollama
    possible_paths = [
        r"C:\Users\Илья\AppData\Local\Programs\Ollama\ollama.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Ollama\ollama.exe"),
        r"C:\Program Files\Ollama\ollama.exe",
        r"C:\Program Files (x86)\Ollama\ollama.exe",
        r"C:\Ollama\ollama.exe",
    ]
    
    # Проверяем стандартные пути
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Ищем в Program Files
    for base in [r"C:\Program Files", r"C:\Program Files (x86)"]:
        if os.path.exists(base):
            for root, dirs, files in os.walk(base):
                if "ollama.exe" in files:
                    return os.path.join(root, "ollama.exe")
    
    # Ищем через glob в AppData
    appdata_paths = glob.glob(os.path.expanduser(r"~\AppData\*\Programs\Ollama\ollama.exe"))
    if appdata_paths:
        return appdata_paths[0]
    
    return None


def ensure_ollama_running():
    """Проверить, запущена ли Ollama, и запустить если нет."""
    # Сначала проверяем, отвечает ли уже сервер
    try:
        resp = requests.get("http://localhost:11434", timeout=2)
        if resp.status_code == 200:
            print("[Ollama] Уже запущена.")
            return True
    except Exception:
        pass

    # Ищем ollama.exe
    ollama_exe = find_ollama_exe()
    
    if not ollama_exe:
        print("[Ollama] Не найден ollama.exe. Убедитесь, что Ollama установлена.")
        print("[Ollama] Скачайте с: https://ollama.com")
        return False
    
    print(f"[Ollama] Найдена: {ollama_exe}")
    print("[Ollama] Запускаю сервер...")
    
    try:
        subprocess.Popen(
            [ollama_exe, "serve"],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        # Ждём, пока сервер поднимется (макс 30 сек)
        print("[Ollama] Ожидание запуска сервера...")
        for i in range(30):
            time.sleep(1)
            try:
                resp = requests.get("http://localhost:11434", timeout=2)
                if resp.status_code == 200:
                    print("[Ollama] Сервер запущен и готов!")
                    return True
            except Exception:
                pass
            if i % 5 == 0:
                print(f"[Ollama] Ожидание... ({i} сек)")
        
        print("[Ollama] Не удалось дождаться запуска. Запустите вручную: ollama serve")
        return False
    except Exception as e:
        print(f"[Ollama] Ошибка запуска: {e}")
        return False


class Jarvis:
    """Главный класс ассистента."""

    def __init__(self):
        self.voice = Voice()
        self.commands = SystemCommands()
        self.coding = EnhancedCodingAssistant()
        self.history: list = []
        self.gui: Optional[JarvisGUI] = None
        self.tray: Optional[TrayIcon] = None
        self.wake_listener: Optional[WakeWordListener] = None
        self._running = True
        self._lock = threading.Lock()
        self._init_complete = False
        self.plugin_registry = PluginRegistry(jarvis_instance=self)
        # Brain initialized after registry so it can use tools
        self.brain = Brain(plugin_registry=self.plugin_registry)
        # Connect brain to coding assistant
        self.coding.brain = self.brain

    # ------------------------------------------------------------------
    # Голосовой вывод с проверкой настроек
    # ------------------------------------------------------------------
    def speak(self, text: str):
        """Озвучить текст, если включены голосовые ответы."""
        if Config.VOICE_RESPONSES_ENABLED and Config.VOICE_ENABLED:
            self.voice.speak(text)

    # ------------------------------------------------------------------
    # Запуск
    # ------------------------------------------------------------------
    def run(self):
        # Настройка автозапуска
        if Config.AUTOSTART_ENABLED and not is_startup_enabled():
            if enable_startup():
                print("[Autostart] Автозапуск включен.")
        elif not Config.AUTOSTART_ENABLED and is_startup_enabled():
            disable_startup()
            print("[Autostart] Автозапуск отключен.")

        # Создаем GUI (это быстро, не блокирует)
        self.gui = JarvisGUI(
            on_text_message=self.handle_text,
            on_voice_button=self.handle_voice,
            on_settings_button=self.show_settings,
            on_minimize_to_tray=self.minimize_to_tray,
        )

        # Запускаем инициализацию в фоне
        init_thread = threading.Thread(target=self._init_background, daemon=True)
        init_thread.start()

        # Создаем иконку в трее
        if Config.TRAY_ENABLED:
            self.tray = TrayIcon(
                on_show=self.show_window,
                on_exit=self.exit_app,
                tooltip=f"{Config.BOT_NAME} — Онлайн",
            )
            self.tray.start()
            print("[Tray] Иконка в трее запущена.")

        # Запускаем GUI
        self.gui.run()

        # Очистка при закрытии
        self._cleanup()

    def _init_background(self):
        """Фоновая инициализация (Ollama, wake-word, приветствие)."""
        # Проверяем/запускаем Ollama
        if Config.AI_PROVIDER == "ollama":
            ensure_ollama_running()

        # Запускаем wake-word listener
        if Config.WAKE_WORD_ENABLED:
            self.wake_listener = WakeWordListener(
                on_wake=self.on_wake_word,
                voice=self.voice,
            )
            self.wake_listener.start()
            print("[WakeWord] Голосовая активация запущена.")

        # Инициализируем плагины
        self.plugin_registry.discover()
        
        # Приветствие как в Железном Человеке
        time.sleep(0.5)
        self._play_welcome_sequence()

        self._init_complete = True

    def _play_welcome_sequence(self):
        """Приветствие как в Железном Человеке: звук + фраза."""
        # Воспроизводим музыку при включении
        play_startup_music()
        
        # Небольшая задержка для синхронизации
        time.sleep(0.3)
        
        # Говорим приветствие
        greeting = "Добро пожаловать домой, сэр."
        self.speak(greeting)
        self.gui.add_system_message(f"🎵 {greeting}")
        
        # Добавляем информацию о статусе
        self.gui.add_system_message("Система активна. Скажите 'Джарвис' для голосовой активации.")

    def _cleanup(self):
        """Очистка ресурсов при закрытии."""
        self._running = False
        if self.wake_listener:
            self.wake_listener.stop()
        if self.tray:
            self.tray.stop()
        print("[Jarvis] Завершение работы.")

    # ------------------------------------------------------------------
    # Tray & Window management
    # ------------------------------------------------------------------
    def minimize_to_tray(self):
        """Свернуть в трей."""
        if self.gui:
            self.gui.hide()
        if self.tray:
            self.tray.notify("J.A.R.V.I.S.", "Работаю в фоновом режиме. Скажите 'Джарвис' для активации.")
        print("[GUI] Свернуто в трей.")

    def show_window(self):
        """Показать окно."""
        if self.gui:
            self.gui.show()
            print("[GUI] Окно показано.")

    def exit_app(self):
        """Полностью закрыть приложение."""
        self._running = False
        if self.wake_listener:
            self.wake_listener.stop()
        if self.tray:
            self.tray.stop()
        if self.gui:
            self.gui.destroy()
        print("[Jarvis] Выход.")

    def show_settings(self):
        """Показать окно настроек."""
        settings = SettingsWindow(
            voice=self.voice,
            on_save=self._on_settings_saved
        )
        settings.show()

    def _on_settings_saved(self):
        """Обработчик сохранения настроек."""
        # Перезапускаем wake-word если изменились настройки
        if self.wake_listener:
            was_running = self.wake_listener.running
            self.wake_listener.stop()
            if Config.WAKE_WORD_ENABLED and was_running:
                time.sleep(0.5)
                self.wake_listener = WakeWordListener(
                    on_wake=self.on_wake_word,
                    voice=self.voice,
                )
                self.wake_listener.start()
        
        self.gui.add_system_message("Настройки сохранены.")
        self.speak("Настройки применены, сэр.")

    # ------------------------------------------------------------------
    # Wake Word
    # ------------------------------------------------------------------
    def on_wake_word(self):
        """Обработка активации по wake-word."""
        if not self._running:
            return

        # Показываем окно если скрыто
        if self.gui and not self.gui.is_visible():
            self.show_window()

        # Озвучиваем активацию
        phrase = self.voice.speak_jarvis_phrase("wake")
        self.gui.add_system_message(f"🎤 {phrase}")
        self.gui.set_listening_status(True)

        # Слушаем команду
        text = self.voice.listen_command()
        self.gui.set_listening_status(False)

        if text:
            self.gui.add_user_message(text)
            response = self.process(text)
            self.gui.add_bot_message(response)
            self.speak(response)
        else:
            self.gui.add_system_message("Не расслышал команду, сэр.")
            self.speak("Прошу прощения, сэр. Не расслышал.")

    # ------------------------------------------------------------------
    # Обработчики GUI
    # ------------------------------------------------------------------
    def handle_text(self, text: str):
        """Обработать текстовое сообщение от пользователя."""
        response = self.process(text)
        self.gui.add_bot_message(response)
        self.speak(response)

    def handle_voice(self):
        """Обработать голосовой ввод из GUI."""
        self.gui.set_listening_status(True)
        text = self.voice.listen(duration=7)
        self.gui.set_listening_status(False)
        
        if text:
            self.gui.add_user_message(text)
            self.handle_text(text)
        else:
            self.gui.add_system_message("Не расслышал, повторите.")
            self.speak("Прошу прощения, сэр. Не расслышал.")

    # ------------------------------------------------------------------
    # Логика обработки команд
    # ------------------------------------------------------------------
    def process(self, text: str) -> str:
        """Определить, что хочет пользователь, и выполнить.
        
        Использует PluginRegistry для поиска подходящего плагина.
        Если ни один плагин не обработал — отправляет в LLM.
        """
        lowered = text.lower().strip()
        
        # Пробуем найти плагин через registry
        plugin, match = self.plugin_registry.process(text)
        
        if plugin is not None:
            try:
                result = plugin.execute(text, match)
                if result.success or result.response:
                    # Update history for plugins that don't speak
                    if result.add_to_history:
                        self.history.append({"role": "user", "content": text})
                        self.history.append({"role": "assistant", "content": result.response})
                        if len(self.history) > 20:
                            self.history = self.history[-20:]
                    return result.response
            except Exception as e:
                print(f"[Process] Plugin {plugin.name} error: {e}")
        
        # Fallback: отправляем в LLM
        response = self.brain.chat(text, self.history)
        self.history.append({"role": "user", "content": text})
        self.history.append({"role": "assistant", "content": response})

        # Ограничиваем историю последними 20 сообщениями
        if len(self.history) > 20:
            self.history = self.history[-20:]

        return response


if __name__ == "__main__":
    print("=" * 50)
    print(f"  {Config.BOT_NAME} — Персональный ИИ-ассистент")
    print("=" * 50)
    print(f"  AI Provider: {Config.AI_PROVIDER}")
    print(f"  Voice:       {'ON' if Config.VOICE_ENABLED else 'OFF'}")
    print(f"  Wake Word:   {'ON' if Config.WAKE_WORD_ENABLED else 'OFF'}")
    print(f"  Tray:        {'ON' if Config.TRAY_ENABLED else 'OFF'}")
    print(f"  Autostart:   {'ON' if Config.AUTOSTART_ENABLED else 'OFF'}")
    print("=" * 50)
    print()

    jarvis = Jarvis()
    try:
        jarvis.run()
    except KeyboardInterrupt:
        print("\n[Jarvis] Прерывание пользователем.")
        jarvis._cleanup()
