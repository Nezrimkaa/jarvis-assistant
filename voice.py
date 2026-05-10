"""Голосовой модуль J.A.R.V.I.S. — естественный русский голос."""
import asyncio
import os
import tempfile
import time
from typing import Optional, List, Dict

import edge_tts
import numpy as np
import sounddevice as sd
from playsound import playsound

from config import Config


class Voice:
    """Текст-в-речь (Edge-TTS) с естественным русским голосом."""

    # Доступные голоса (более естественные)
    VOICES = {
        "male": "ru-RU-DmitryNeural",
        "female": "ru-RU-SvetlanaNeural",  # Более естественный женский
        "jarvis": "ru-RU-DmitryNeural",
    }

    # Фразы Джарвиса
    JARVIS_PHRASES = {
        "wake": ["Да, сэр?", "Слушаю вас, сэр.", "Ваши указания?", "К вашим услугам."],
        "greeting": ["Добро пожаловать домой, сэр.", 
                     "Приветствую. Система готова к работе.",
                     "J.A.R.V.I.S. онлайн. Чем могу помочь, сэр?"],
        "error": ["Прошу прощения, сэр. Не могу выполнить запрос.", 
                  "Ошибка в системе. Повторите команду, пожалуйста."],
        "processing": ["Обрабатываю запрос...", "Работаю над этим, сэр...", "Один момент..."],
        "goodbye": ["До свидания, сэр. J.A.R.V.I.S. переходит в режим ожидания.",
                    "Всегда к вашим услугам. До встречи.",
                    "Система переходит в спящий режим. До скорого, сэр."],
        "not_heard": ["Прошу прощения, сэр. Не расслышал.",
                      "Не уловил команду. Повторите, пожалуйста."],
    }

    def __init__(self):
        self.enabled = Config.VOICE_ENABLED
        # Используем более естественный голос
        self.voice = "ru-RU-DmitryNeural"
        self.sample_rate = 16000
        self.channels = 1
        self._speaking = False
        self._mic_device = None
        self._initialized = False
        
        self._init_microphone()
        
        print(f"[Voice] Выбран голос: {self.voice}")

    def _init_microphone(self):
        """Инициализировать микрофон."""
        try:
            devices = self.get_microphones()
            if devices:
                self._mic_device = devices[0]["index"]
                print(f"[Voice] Микрофон: {devices[0]['name']} (device {self._mic_device})")
                self._initialized = True
            else:
                print("[Voice] ВНИМАНИЕ: Микрофоны не найдены!")
        except Exception as e:
            print(f"[Voice] Ошибка инициализации микрофона: {e}")

    def get_microphones(self) -> List[Dict]:
        """Получить список микрофонов."""
        try:
            devices = []
            for i, device in enumerate(sd.query_devices()):
                if device['max_input_channels'] > 0:
                    devices.append({
                        "index": i,
                        "name": device['name'],
                        "channels": device['max_input_channels'],
                        "sample_rate": device['default_samplerate']
                    })
            return devices
        except Exception as e:
            print(f"[Voice] Ошибка получения списка микрофонов: {e}")
            return []

    def set_microphone(self, device_index: int):
        """Установить микрофон."""
        self._mic_device = device_index
        try:
            device_info = sd.query_devices(device_index)
            print(f"[Voice] Выбран микрофон: {device_info['name']}")
        except:
            print(f"[Voice] Выбран микрофон #{device_index}")

    # ------------------------------------------------------------------
    # TTS — текст в речь (с естественностью)
    # ------------------------------------------------------------------
    def speak(self, text: str):
        """Озвучить текст естественным голосом."""
        if not self.enabled or not text or not Config.VOICE_RESPONSES_ENABLED:
            return

        import threading
        threading.Thread(target=self._speak_sync, args=(text,), daemon=True).start()

    def _speak_sync(self, text: str):
        """Синхронная озвучка с SSML для естественности."""
        self._speaking = True
        print(f"[{Config.BOT_NAME}] {text}")

        try:
            asyncio.run(self._speak_async(text))
        except Exception as e:
            print(f"[Voice ERROR] TTS: {e}")
        finally:
            self._speaking = False

    async def _speak_async(self, text: str):
        """Асинхронная генерация речи."""
        # ЧИСТЫЙ ТЕКСТ без SSML! (SSML вызывает "меньше чем больше чем")
        communicate = edge_tts.Communicate(text, voice=self.voice)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp_path = tmp.name

        try:
            await communicate.save(tmp_path)
            playsound(tmp_path)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def speak_jarvis_phrase(self, phrase_type: str = "wake") -> str:
        """Озвучить фразу Джарвиса."""
        import random
        phrases = self.JARVIS_PHRASES.get(phrase_type, ["Да, сэр?"])
        text = random.choice(phrases)
        self.speak(text)
        return text

    def is_speaking(self) -> bool:
        """Проверить, говорит ли сейчас Джарвис."""
        return self._speaking

    # ------------------------------------------------------------------
    # STT — речь в текст
    # ------------------------------------------------------------------
    def listen(self, duration: int = 5) -> Optional[str]:
        """Слушать микрофон."""
        if not self.enabled:
            return None

        try:
            import speech_recognition as sr
        except ImportError:
            print("[Voice] Установите SpeechRecognition: pip install SpeechRecognition")
            return None

        try:
            kwargs = {
                "samplerate": self.sample_rate,
                "channels": self.channels,
                "dtype": "int16",
                "blocksize": 2048,
            }
            
            if self._mic_device is not None:
                kwargs["device"] = self._mic_device
            
            recording = sd.rec(int(duration * self.sample_rate), **kwargs)
            sd.wait()

            # Нормализация
            recording = self._normalize_audio(recording)
            volume = np.abs(recording).mean()
            
            if volume < 15:
                return None

            audio_bytes = recording.tobytes()
            audio_data = sr.AudioData(audio_bytes, self.sample_rate, 2)

            recognizer = sr.Recognizer()
            
            try:
                text = recognizer.recognize_google(audio_data, language="ru-RU", show_all=False)
                if text and len(text.strip()) > 0:
                    print(f"[Вы] {text}")
                    return text
            except sr.UnknownValueError:
                pass
            
            try:
                text = recognizer.recognize_google(audio_data, language="en-US", show_all=False)
                if text and len(text.strip()) > 0:
                    print(f"[Вы] {text}")
                    return text
            except sr.UnknownValueError:
                return None

        except sr.RequestError as e:
            print(f"[Voice] Ошибка сети: {e}")
            return None
        except Exception as e:
            print(f"[Voice] Ошибка: {e}")
            return None

    def _normalize_audio(self, recording: np.ndarray) -> np.ndarray:
        """Нормализовать аудио."""
        max_val = np.max(np.abs(recording))
        if max_val > 0:
            target_max = 32767 * 0.7
            gain = target_max / max_val
            recording = recording * gain
            recording = np.clip(recording, -32767, 32767)
        return recording.astype("int16")

    def listen_wake(self) -> Optional[str]:
        """Запись для wake-word."""
        return self.listen(duration=4)

    def listen_command(self) -> Optional[str]:
        """Запись команды."""
        return self.listen(duration=8)

    def test_microphone(self, duration: int = 3):
        """Тест микрофона."""
        try:
            kwargs = {
                "samplerate": self.sample_rate,
                "channels": self.channels,
                "dtype": "int16",
            }
            
            if self._mic_device is not None:
                kwargs["device"] = self._mic_device
            
            print("[Voice] Запись тестового сигнала...")
            recording = sd.rec(int(duration * self.sample_rate), **kwargs)
            sd.wait()
            
            recording = self._normalize_audio(recording)
            volume = np.abs(recording).mean()
            max_volume = np.abs(recording).max()
            
            print(f"[Voice] Средний уровень: {volume:.0f}")
            print(f"[Voice] Максимальный уровень: {max_volume:.0f}")
            
            if volume < 30:
                return False, f"Слишком тихо ({volume:.0f}). Проверьте микрофон."
            elif volume > 10000:
                return False, f"Слишком громко ({volume:.0f})."
            else:
                return True, f"Микрофон работает (уровень: {volume:.0f})"
                
        except Exception as e:
            return False, f"Ошибка тестирования: {e}"
