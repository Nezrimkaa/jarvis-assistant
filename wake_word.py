"""Wake-word детектор J.A.R.V.I.S. — постоянное прослушивание."""
import re
import threading
import time
from typing import Callable, Optional

from voice import Voice


class WakeWordListener:
    """Постоянно слушает микрофон и активируется по слову 'Джарвис'."""

    # Различные варианты произношения
    WAKE_PATTERNS = [
        re.compile(r"джарвис", re.IGNORECASE),
        re.compile(r"jarvis", re.IGNORECASE),
        re.compile(r"джарв", re.IGNORECASE),
        re.compile(r"джарвиз", re.IGNORECASE),
        re.compile(r"джервис", re.IGNORECASE),
        re.compile(r"жарвис", re.IGNORECASE),
    ]

    def __init__(self, on_wake: Callable, voice: Voice):
        self.on_wake = on_wake
        self.voice = voice
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.cooldown_until = 0.0
        self.listen_count = 0
        self.error_count = 0
        self.debug = True

    def start(self):
        """Запустить фоновое прослушивание."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[WakeWord] ========================================")
        print("[WakeWord] Фоновое прослушивание ЗАПУЩЕНО")
        print("[WakeWord] Скажите 'Джарвис' для активации")
        print("[WakeWord] Работает даже в трее!")
        print("[WakeWord] ========================================")

    def stop(self):
        """Остановить прослушивание."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=3)
        print("[WakeWord] Остановлено.")

    def _loop(self):
        """Главный цикл прослушивания."""
        time.sleep(2)
        
        print("[WakeWord] Микрофон активен. Слушаю...")
        
        while self.running:
            time.sleep(0.3)

            if time.time() < self.cooldown_until:
                continue

            self.listen_count += 1
            
            if self.debug and self.listen_count % 20 == 0:
                print(f"[WakeWord] Цикл #{self.listen_count}, жду команду...")
            
            try:
                # Слушаем 4 секунды для лучшего распознавания
                text = self.voice.listen(duration=4)
                
                if text is not None:
                    self.error_count = 0
                    if self.debug:
                        print(f"[WakeWord] Распознано: '{text}'")
                
            except Exception as e:
                self.error_count += 1
                if self.error_count % 5 == 0:
                    print(f"[WakeWord] Ошибка записи ({self.error_count} подряд): {e}")
                time.sleep(1)
                continue

            if not text:
                continue

            if self._is_wake_word(text):
                print(f"[WakeWord] >>> АКТИВАЦИЯ! Распознано: '{text}' <<<")
                self.error_count = 0
                self.cooldown_until = time.time() + 5.0
                try:
                    self.on_wake()
                except Exception as e:
                    print(f"[WakeWord] Ошибка обработчика: {e}")

    def _is_wake_word(self, text: str) -> bool:
        """Проверить, содержит ли текст wake-word."""
        for pattern in self.WAKE_PATTERNS:
            if pattern.search(text):
                return True
        return False
