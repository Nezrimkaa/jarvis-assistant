"""Автозапуск J.A.R.V.I.S. с Windows — управление ключом реестра."""
import os
import sys

import winreg


def get_exe_path() -> str:
    """Получить путь к текущему EXE или Python-скрипту."""
    if getattr(sys, "frozen", False):
        # Запущены как EXE (PyInstaller)
        return sys.executable
    
    # Ищем EXE рядом с main.py или в dist/
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    possible_exes = [
        os.path.join(script_dir, "dist", "Jarvis.exe"),
        os.path.join(script_dir, "Jarvis.exe"),
        os.path.join(os.path.dirname(script_dir), "dist", "Jarvis.exe"),
        r"E:\jarvis-assistant\dist\Jarvis.exe",
    ]
    
    for exe_path in possible_exes:
        if os.path.exists(exe_path):
            return exe_path
    
    # Fallback: запущены как python main.py
    return os.path.abspath(sys.argv[0])


def is_startup_enabled() -> bool:
    """Проверить, есть ли J.A.R.V.I.S в автозагрузке."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
            winreg.QueryValueEx(key, "Jarvis")
            return True
    except FileNotFoundError:
        return False
    except OSError:
        return False


def enable_startup() -> bool:
    """Добавить J.A.R.V.I.S в автозагрузку Windows."""
    try:
        exe_path = get_exe_path()
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "Jarvis", 0, winreg.REG_SZ, exe_path)
        return True
    except Exception as e:
        print(f"[Autostart] Ошибка добавления: {e}")
        return False


def disable_startup() -> bool:
    """Удалить J.A.R.V.I.S из автозагрузки Windows."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, "Jarvis")
        return True
    except FileNotFoundError:
        return True  # уже удалено
    except Exception as e:
        print(f"[Autostart] Ошибка удаления: {e}")
        return False
