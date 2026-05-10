"""Сборка J.A.R.V.I.S. в EXE и установка ярлыков."""
import os
import sys
import subprocess
import shutil
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Установи Pillow: pip install pillow")
    sys.exit(1)


def create_icon():
    """Создать иконку J.A.R.V.I.S."""
    icon_path = Path("icon.ico")
    # Удаляем старую иконку чтобы создать новую
    if icon_path.exists():
        icon_path.unlink()
        print("[*] Удалена старая иконка")

    print("[*] Создание новой золотой иконки J.A.R.V.I.S....")
    
    # Создаем большое изображение для хорошего качества
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Золотой круг (цвет Железного Человека)
    circle_color = (255, 215, 0, 255)  # Яркое золото #FFD700
    draw.ellipse([10, 10, size-10, size-10], fill=circle_color)
    
    # Белая буква J
    try:
        font = ImageFont.truetype("segoeui.ttf", 140)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", 140)
        except:
            font = ImageFont.load_default()
    
    # Центрируем текст
    bbox = draw.textbbox((0, 0), "J", font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 10
    
    draw.text((x, y), "J", font=font, fill=(255, 255, 255, 255))
    
    # Сохраняем как ICO
    img.save(str(icon_path), format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"[+] Иконка создана: {icon_path}")
    return str(icon_path)


def build_exe():
    """Собрать EXE через PyInstaller."""
    print("[*] Сборка EXE через PyInstaller...")
    print("[*] Это может занять 2-3 минуты...")
    
    # Очищаем старые сборки
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Команда для сборки
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--onefile",
        "--name", "Jarvis",
        "--icon", "icon.ico",
        "--add-data", ".env;.",
        "--hidden-import", "config",
        "--hidden-import", "brain",
        "--hidden-import", "voice",
        "--hidden-import", "commands",
        "--hidden-import", "gui",
        "--hidden-import", "wake_word",
        "--hidden-import", "tray",
        "--hidden-import", "autostart",
        "--hidden-import", "edge_tts",
        "--hidden-import", "speech_recognition",
        "--hidden-import", "pystray",
        "--hidden-import", "PIL",
        "--hidden-import", "playsound",
        "--hidden-import", "sounddevice",
        "--hidden-import", "numpy",
        "--hidden-import", "psutil",
        "--hidden-import", "requests",
        "--hidden-import", "openai",
        "--hidden-import", "pyautogui",
        "--hidden-import", "pyperclip",
        "--hidden-import", "dotenv",
        "--hidden-import", "settings",
        "--hidden-import", "sounds",
        "--hidden-import", "winsound",
        "--hidden-import", "google.generativeai",
        "--hidden-import", "pygame",
        "--hidden-import", "pygame.mixer",
        "main.py"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[+] EXE успешно собран!")
        exe_path = os.path.abspath("dist/Jarvis.exe")
        print(f"[+] Путь: {exe_path}")
        
        # Копируем звуковой файл если есть
        if os.path.exists("startup_sound.mp3"):
            shutil.copy("startup_sound.mp3", "dist/startup_sound.mp3")
            print("[+] Звуковой файл скопирован")
        
        return exe_path
    else:
        print("[-] Ошибка сборки:")
        print(result.stderr)
        return None


def create_shortcut(exe_path, shortcut_name, shortcut_path):
    """Создать ярлык Windows."""
    try:
        import winshell
        from win32com.client import Dispatch
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.IconLocation = os.path.join(os.path.dirname(exe_path), "icon.ico")
        shortcut.Description = "J.A.R.V.I.S. — Персональный ИИ-ассистент"
        shortcut.save()
        print(f"[+] Ярлык создан: {shortcut_path}")
        return True
    except ImportError:
        # Fallback: создаем через PowerShell
        return create_shortcut_powershell(exe_path, shortcut_name, shortcut_path)


def create_shortcut_powershell(exe_path, shortcut_name, shortcut_path):
    """Создать ярлык через PowerShell."""
    ps_script = f"""
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{exe_path}"
$Shortcut.WorkingDirectory = "{os.path.dirname(exe_path)}"
$Shortcut.IconLocation = "{os.path.join(os.path.dirname(exe_path), 'icon.ico')}"
$Shortcut.Description = "J.A.R.V.I.S. — Персональный ИИ-ассистент"
$Shortcut.Save()
"""
    
    result = subprocess.run(
        ["powershell", "-Command", ps_script],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"[+] Ярлык создан: {shortcut_path}")
        return True
    else:
        print(f"[-] Ошибка создания ярлыка: {result.stderr}")
        return False


def install():
    """Установка J.A.R.V.I.S."""
    print("=" * 60)
    print("  J.A.R.V.I.S. — Установка")
    print("=" * 60)
    print()
    
    # 1. Создаем иконку
    create_icon()
    
    # 2. Собираем EXE
    exe_path = build_exe()
    if not exe_path:
        print("[-] Сборка прервана.")
        return
    
    # 3. Копируем иконку в dist
    shutil.copy("icon.ico", "dist/icon.ico")
    
    # 4. Создаем ярлык на рабочем столе
    desktop = Path.home() / "Desktop"
    desktop_shortcut = desktop / "J.A.R.V.I.S..lnk"
    
    print("[*] Создание ярлыка на рабочем столе...")
    create_shortcut(exe_path, "J.A.R.V.I.S.", str(desktop_shortcut))
    
    # 5. Создаем ярлык в меню Пуск
    start_menu = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs"
    start_shortcut = start_menu / "J.A.R.V.I.S..lnk"
    
    print("[*] Создание ярлыка в меню Пуск...")
    create_shortcut(exe_path, "J.A.R.V.I.S.", str(start_shortcut))
    
    print()
    print("=" * 60)
    print("  Установка завершена!")
    print("=" * 60)
    print()
    print(f"  EXE: {exe_path}")
    print(f"  Ярлык на рабочем столе: {desktop_shortcut}")
    print(f"  Ярлык в меню Пуск: {start_shortcut}")
    print()
    print("  Для запуска:")
    print("  - Двойной клик по ярлыку на рабочем столе")
    print("  - Или через меню Пуск")
    print()


if __name__ == "__main__":
    try:
        install()
    except Exception as e:
        print(f"[-] Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nНажми Enter для выхода...")
