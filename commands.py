"""Системные команды J.A.R.V.I.S. — расширенный набор."""
import os
import subprocess
import webbrowser
from datetime import datetime
from typing import Dict, Optional, List

import pyautogui


class SystemCommands:
    """Набор системных команд для управления ПК."""

    # --- Список известных приложений ---
    APPS: Dict[str, str] = {
        # Браузеры
        "браузер": "chrome",
        "хром": "chrome",
        "google chrome": "chrome",
        "firefox": "firefox",
        "opera": "opera",
        "edge": "msedge",
        
        # Офис
        "блокнот": "notepad",
        "калькулятор": "calc",
        "ворд": "winword",
        "word": "winword",
        "эксель": "excel",
        "excel": "excel",
        "пауэрпоинт": "powerpnt",
        "powerpoint": "powerpnt",
        
        # Системные
        "проводник": "explorer",
        "терминал": "cmd",
        "командная строка": "cmd",
        "cmd": "cmd",
        "powershell": "powershell",
        "диспетчер задач": "taskmgr",
        "панель управления": "control",
        "настройки": "ms-settings:",
        "редактор реестра": "regedit",
        
        # Разработка
        "пайчарм": "pycharm",
        "pycharm": "pycharm",
        "вс код": "code",
        "vscode": "code",
        "code": "code",
        "блокнот++": "notepad++",
        "notepad++": "notepad++",
        "git bash": "git-bash",
        
        # Медиа
        "паинт": "mspaint",
        "paint": "mspaint",
        "фотошоп": "photoshop",
        "photoshop": "photoshop",
        
        # Социальные сети и мессенджеры
        "дискорд": "discord",
        "discord": "discord",
        "телеграм": "telegram",
        "telegram": "telegram",
        "whatsapp": "whatsapp",
        "вконтакте": "vk",
        "vk": "vk",
        
        # Игры
        "стим": "steam",
        "steam": "steam",
        "epic games": "epicgameslauncher",
        
        # Другое
        "spotify": "spotify",
        "календарь": "outlookcal:",
        "почта": "outlookmail:",
    }

    # --- Известные сайты ---
    WEBSITES: Dict[str, str] = {
        "гугл": "https://www.google.com",
        "google": "https://www.google.com",
        "яндекс": "https://www.yandex.ru",
        "yandex": "https://www.yandex.ru",
        "ютуб": "https://www.youtube.com",
        "youtube": "https://www.youtube.com",
        "вконтакте": "https://vk.com",
        "vk": "https://vk.com",
        "телеграм": "https://web.telegram.org",
        "telegram": "https://web.telegram.org",
        "whatsapp": "https://web.whatsapp.com",
        "инстаграм": "https://www.instagram.com",
        "instagram": "https://www.instagram.com",
        "фейсбук": "https://www.facebook.com",
        "facebook": "https://www.facebook.com",
        "твиттер": "https://twitter.com",
        "twitter": "https://twitter.com",
        "дисcord": "https://discord.com",
        "discord": "https://discord.com",
        "github": "https://github.com",
        "гитхаб": "https://github.com",
        "stackoverflow": "https://stackoverflow.com",
        "стаковерфлоу": "https://stackoverflow.com",
        " reddit": "https://www.reddit.com",
        "новости": "https://news.google.com",
        "погода": "https://yandex.ru/pogoda",
        "переводчик": "https://translate.google.com",
        "карты": "https://maps.google.com",
        "яндекс карты": "https://yandex.ru/maps",
        "netflix": "https://www.netflix.com",
        "кинопоиск": "https://www.kinopoisk.ru",
        "spotify": "https://open.spotify.com",
        "twitch": "https://www.twitch.tv",
        "твич": "https://www.twitch.tv",
    }

    @classmethod
    def open_app(cls, name: str) -> str:
        """Открыть приложение по имени."""
        app = cls.APPS.get(name.lower(), name)
        try:
            subprocess.Popen(app, shell=True)
            return f"Открываю {name}"
        except Exception as e:
            return f"Не удалось открыть {name}: {e}"

    @classmethod
    def search_google(cls, query: str) -> str:
        """Открыть поиск в Google."""
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Ищу в Google: {query}"

    @classmethod
    def search_youtube(cls, query: str) -> str:
        """Открыть поиск на YouTube."""
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Ищу на YouTube: {query}"

    @classmethod
    def search_yandex(cls, query: str) -> str:
        """Открыть поиск в Яндексе."""
        url = f"https://yandex.ru/search/?text={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Ищу в Яндексе: {query}"

    @classmethod
    def open_website(cls, url: str) -> str:
        """Открыть сайт по имени или URL."""
        # Проверяем, есть ли сайт в списке известных
        site_url = cls.WEBSITES.get(url.lower())
        if site_url:
            webbrowser.open(site_url)
            return f"Открываю {url}"
        
        # Иначе открываем как URL
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        webbrowser.open(url)
        return f"Открываю {url}"

    @classmethod
    def open_new_tab(cls, url: str) -> str:
        """Открыть новую вкладку в браузере."""
        return cls.open_website(url)

    @classmethod
    def screenshot(cls, name: Optional[str] = None) -> str:
        """Сделать скриншот экрана."""
        filename = name or f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        pyautogui.screenshot(filename)
        return f"Скриншот сохранён: {os.path.abspath(filename)}"

    @classmethod
    def volume_up(cls, steps: int = 5) -> str:
        """Увеличить громкость."""
        import ctypes
        for _ in range(steps):
            ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)  # VK_VOLUME_UP
            ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)  # KEYUP
        return "Громкость увеличена"

    @classmethod
    def volume_down(cls, steps: int = 5) -> str:
        """Уменьшить громкость."""
        import ctypes
        for _ in range(steps):
            ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)  # VK_VOLUME_DOWN
            ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)  # KEYUP
        return "Громкость уменьшена"

    @classmethod
    def mute(cls) -> str:
        """Включить/выключить звук."""
        import ctypes
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)  # VK_VOLUME_MUTE
        ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)  # KEYUP
        return "Звук переключён"

    @classmethod
    def media_play_pause(cls) -> str:
        """Play/Pause медиа."""
        import ctypes
        ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0)  # VK_MEDIA_PLAY_PAUSE
        ctypes.windll.user32.keybd_event(0xB3, 0, 2, 0)
        return "Медиа: Play/Pause"

    @classmethod
    def media_next(cls) -> str:
        """Следующий трек."""
        import ctypes
        ctypes.windll.user32.keybd_event(0xB0, 0, 0, 0)  # VK_MEDIA_NEXT_TRACK
        ctypes.windll.user32.keybd_event(0xB0, 0, 2, 0)
        return "Следующий трек"

    @classmethod
    def media_prev(cls) -> str:
        """Предыдущий трек."""
        import ctypes
        ctypes.windll.user32.keybd_event(0xB1, 0, 0, 0)  # VK_MEDIA_PREV_TRACK
        ctypes.windll.user32.keybd_event(0xB1, 0, 2, 0)
        return "Предыдущий трек"

    @classmethod
    def shutdown(cls, seconds: int = 60) -> str:
        """Выключить ПК."""
        os.system(f"shutdown /s /t {seconds}")
        return f"Выключение через {seconds} секунд. Скажи 'отмени выключение' для отмены."

    @classmethod
    def shutdown_now(cls) -> str:
        """Выключить ПК немедленно."""
        os.system("shutdown /s /t 0")
        return "Выключение компьютера..."

    @classmethod
    def cancel_shutdown(cls) -> str:
        """Отменить выключение."""
        os.system("shutdown /a")
        return "Выключение отменено"

    @classmethod
    def restart(cls, seconds: int = 60) -> str:
        """Перезагрузить ПК."""
        os.system(f"shutdown /r /t {seconds}")
        return f"Перезагрузка через {seconds} секунд. Скажи 'отмени выключение' для отмены."

    @classmethod
    def restart_now(cls) -> str:
        """Перезагрузить ПК немедленно."""
        os.system("shutdown /r /t 0")
        return "Перезагрузка компьютера..."

    @classmethod
    def sleep(cls) -> str:
        """Перевести ПК в спящий режим."""
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "Перевожу в спящий режим"

    @classmethod
    def hibernate(cls) -> str:
        """Перевести ПК в режим гибернации."""
        os.system("shutdown /h")
        return "Перевожу в режим гибернации"

    @classmethod
    def lock(cls) -> str:
        """Заблокировать ПК."""
        import ctypes
        ctypes.windll.user32.LockWorkStation()
        return "ПК заблокирован"

    @classmethod
    def logout(cls) -> str:
        """Выйти из системы."""
        os.system("shutdown /l")
        return "Выход из системы"

    @classmethod
    def get_system_info(cls) -> str:
        """Получить информацию о системе."""
        import platform
        import psutil

        cpu = platform.processor() or "Unknown"
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        cpu_percent = psutil.cpu_percent(interval=1)

        return (
            f"OS: {platform.system()} {platform.release()}\n"
            f"CPU: {cpu} ({cpu_percent}%)\n"
            f"RAM: {ram.percent}% использовано ({ram.used // 1024 // 1024} MB / {ram.total // 1024 // 1024} MB)\n"
            f"Disk: {disk.percent}% использовано ({disk.used // 1024 // 1024 // 1024} GB / {disk.total // 1024 // 1024 // 1024} GB)"
        )

    @classmethod
    def get_time(cls) -> str:
        """Получить текущее время."""
        now = datetime.now()
        return f"Текущее время: {now.strftime('%H:%M:%S')}"

    @classmethod
    def get_date(cls) -> str:
        """Получить текущую дату."""
        now = datetime.now()
        return f"Сегодня {now.strftime('%d.%m.%Y')}, {now.strftime('%A')}"

    @classmethod
    def create_folder(cls, path: str) -> str:
        """Создать папку."""
        try:
            os.makedirs(path, exist_ok=True)
            return f"Папка создана: {path}"
        except Exception as e:
            return f"Ошибка создания папки: {e}"

    @classmethod
    def open_folder(cls, path: str) -> str:
        """Открыть папку."""
        try:
            if os.path.exists(path):
                os.startfile(path)
                return f"Открываю {path}"
            else:
                # Пробуем как известную папку
                known_folders = {
                    "загрузки": os.path.expanduser("~\\Downloads"),
                    "документы": os.path.expanduser("~\\Documents"),
                    "рабочий стол": os.path.expanduser("~\\Desktop"),
                    "изображения": os.path.expanduser("~\\Pictures"),
                    "видео": os.path.expanduser("~\\Videos"),
                    "музыка": os.path.expanduser("~\\Music"),
                }
                folder = known_folders.get(path.lower())
                if folder and os.path.exists(folder):
                    os.startfile(folder)
                    return f"Открываю {path}"
                return f"Папка не найдена: {path}"
        except Exception as e:
            return f"Ошибка открытия папки: {e}"

    @classmethod
    def empty_recycle_bin(cls) -> str:
        """Очистить корзину."""
        try:
            import ctypes
            from ctypes import wintypes
            
            SHEmptyRecycleBin = ctypes.windll.shell32.SHEmptyRecycleBinW
            SHEmptyRecycleBin(None, None, 0)
            return "Корзина очищена"
        except Exception as e:
            return f"Ошибка очистки корзины: {e}"

    @classmethod
    def restart_explorer(cls) -> str:
        """Перезапустить проводник."""
        try:
            os.system("taskkill /f /im explorer.exe & start explorer.exe")
            return "Проводник перезапущен"
        except Exception as e:
            return f"Ошибка: {e}"

    @classmethod
    def minimize_all_windows(cls) -> str:
        """Свернуть все окна."""
        import ctypes
        ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # LWIN
        ctypes.windll.user32.keybd_event(0x4D, 0, 0, 0)  # M
        ctypes.windll.user32.keybd_event(0x4D, 0, 2, 0)  # KEYUP
        ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)  # KEYUP
        return "Все окна свернуты"

    @classmethod
    def show_desktop(cls) -> str:
        """Показать рабочий стол."""
        import ctypes
        ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # LWIN
        ctypes.windll.user32.keybd_event(0x44, 0, 0, 0)  # D
        ctypes.windll.user32.keybd_event(0x44, 0, 2, 0)  # KEYUP
        ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)  # KEYUP
        return "Рабочий стол"

    @classmethod
    def type_text(cls, text: str) -> str:
        """Напечатать текст."""
        pyautogui.typewrite(text, interval=0.01)
        return f"Напечатал: {text}"

    @classmethod
    def press_key(cls, key: str) -> str:
        """Нажать клавишу."""
        pyautogui.press(key)
        return f"Нажал {key}"

    @classmethod
    def copy_to_clipboard(cls, text: str) -> str:
        """Копировать текст в буфер обмена."""
        import pyperclip
        try:
            pyperclip.copy(text)
            return "Скопировано в буфер обмена"
        except:
            return "Ошибка копирования"

    @classmethod
    def paste_from_clipboard(cls) -> str:
        """Вставить из буфера обмена."""
        pyautogui.hotkey('ctrl', 'v')
        return "Вставлено"

    @classmethod
    def kill_process(cls, process_name: str) -> str:
        """Завершить процесс."""
        try:
            os.system(f"taskkill /f /im {process_name}")
            return f"Процесс {process_name} завершён"
        except Exception as e:
            return f"Ошибка: {e}"

    @classmethod
    def open_control_panel(cls, item: Optional[str] = None) -> str:
        """Открыть панель управления или конкретный пункт."""
        if item:
            os.system(f"control {item}")
            return f"Открываю {item}"
        os.system("control")
        return "Открываю панель управления"

    @classmethod
    def open_task_manager(cls) -> str:
        """Открыть диспетчер задач."""
        os.system("taskmgr")
        return "Открываю диспетчер задач"

    @classmethod
    def open_calculator(cls) -> str:
        """Открыть калькулятор."""
        os.system("calc")
        return "Открываю калькулятор"

    @classmethod
    def open_cmd(cls) -> str:
        """Открыть командную строку."""
        os.system("start cmd")
        return "Открываю командную строку"

    @classmethod
    def open_powershell(cls) -> str:
        """Открыть PowerShell."""
        os.system("start powershell")
        return "Открываю PowerShell"

    @classmethod
    def open_settings(cls) -> str:
        """Открыть настройки Windows."""
        os.system("start ms-settings:")
        return "Открываю настройки"

    @classmethod
    def open_file_explorer(cls, path: Optional[str] = None) -> str:
        """Открыть проводник."""
        if path:
            os.system(f'explorer "{path}"')
            return f"Открываю проводник: {path}"
        os.system("explorer")
        return "Открываю проводник"

    @classmethod
    def open_browser(cls, url: Optional[str] = None) -> str:
        """Открыть браузер."""
        if url:
            webbrowser.open(url)
            return f"Открываю браузер: {url}"
        os.system("start chrome")
        return "Открываю браузер"

    @classmethod
    def get_weather(cls, city: Optional[str] = None) -> str:
        """Открыть погоду."""
        if city:
            url = f"https://yandex.ru/pogoda/{city}"
        else:
            url = "https://yandex.ru/pogoda"
        webbrowser.open(url)
        return "Открываю погоду"

    @classmethod
    def get_news(cls) -> str:
        """Открыть новости."""
        webbrowser.open("https://news.google.com")
        return "Открываю новости"

    @classmethod
    def open_maps(cls, location: Optional[str] = None) -> str:
        """Открыть карты."""
        if location:
            url = f"https://www.google.com/maps/search/{location.replace(' ', '+')}"
        else:
            url = "https://www.google.com/maps"
        webbrowser.open(url)
        return "Открываю карты"

    @classmethod
    def translate(cls, text: Optional[str] = None) -> str:
        """Открыть переводчик."""
        if text:
            url = f"https://translate.google.com/?sl=auto&tl=ru&text={text.replace(' ', '%20')}"
        else:
            url = "https://translate.google.com"
        webbrowser.open(url)
        return "Открываю переводчик"

    @classmethod
    def search_wikipedia(cls, query: str) -> str:
        """Поиск в Википедии."""
        url = f"https://ru.wikipedia.org/wiki/{query.replace(' ', '_')}"
        webbrowser.open(url)
        return f"Ищу в Википедии: {query}"

    @classmethod
    def run_command(cls, command: str) -> str:
        """Выполнить команду в cmd."""
        try:
            subprocess.Popen(command, shell=True)
            return f"Выполняю: {command}"
        except Exception as e:
            return f"Ошибка: {e}"
