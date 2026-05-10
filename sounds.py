"""Звуки J.A.R.V.I.S. — воспроизведение MP3 приветствия."""
import os
import threading
import sys
import time

def _get_sound_path(filename: str) -> str:
    """Получить путь к звуковому файлу."""
    if getattr(sys, 'frozen', False):
        # PyInstaller --onefile extracts to temp dir (sys._MEIPASS)
        # Fallback to exe dir if _MEIPASS is not available
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

def play_startup_music():
    """Воспроизвести MP3 приветствие при запуске."""
    def _play():
        sound_file = _get_sound_path("startup_sound.mp3")
        print(f"[Sound] Looking for: {sound_file}")
        print(f"[Sound] Exists: {os.path.exists(sound_file)}")
        
        if not os.path.exists(sound_file):
            print("[Sound] startup_sound.mp3 не найден")
            return
        
        try:
            import pygame
            print("[Sound] pygame imported")
            pygame.mixer.init()
            print("[Sound] pygame mixer init OK")
            pygame.mixer.music.load(sound_file)
            print("[Sound] pygame music load OK")
            pygame.mixer.music.play()
            print("[Sound] pygame music playing")
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.quit()
            print("[Sound] pygame playback finished")
            return
        except ImportError:
            print("[Sound] pygame not installed")
        except Exception as e:
            print(f"[Sound] Pygame error: {e}")
        
        try:
            from playsound import playsound as ps
            ps(sound_file)
            print("[Sound] playsound playback finished")
            return
        except Exception as e:
            print(f"[Sound] Playsound error: {e}")
    
    thread = threading.Thread(target=_play, daemon=True)
    thread.start()

def play_wake_sound():
    """Звук активации."""
    def _play():
        try:
            import winsound
            winsound.Beep(1800, 100)
        except:
            pass
    
    thread = threading.Thread(target=_play, daemon=True)
    thread.start()

def play_error_sound():
    """Звук ошибки."""
    def _play():
        try:
            import winsound
            winsound.Beep(400, 300)
        except:
            pass
    
    thread = threading.Thread(target=_play, daemon=True)
    thread.start()

def play_success_sound():
    """Звук успеха."""
    def _play():
        try:
            import winsound
            winsound.Beep(2000, 150)
        except:
            pass
    
    thread = threading.Thread(target=_play, daemon=True)
    thread.start()
