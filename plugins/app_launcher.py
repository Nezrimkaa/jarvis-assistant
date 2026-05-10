"""App Launcher Plugin — open apps, websites, folders."""
import re
import webbrowser
from typing import Optional

from .base import BasePlugin, PluginResult


class AppLauncherPlugin(BasePlugin):
    """Открытие приложений, сайтов и папок."""
    
    name = "app_launcher"
    description = "Открытие программ, сайтов и папок"
    version = "1.0.0"
    priority = 30
    
    triggers = [
        (r"открой\s+(.+)", "open"),
        (r"запусти\s+(.+)", "open"),
        (r"открой сайт\s+(.+)", "website"),
        (r"перейди на\s+(.+)", "website"),
        (r"открой вкладку\s+(.+)", "new_tab"),
        (r"новая вкладка\s+(.+)", "new_tab"),
        (r"открой папку\s+(.+)", "folder"),
    ]
    
    # Popular websites shortcuts
    POPULAR_SITES = {
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
        "инстаграм": "https://www.instagram.com",
        "instagram": "https://www.instagram.com",
        "github": "https://github.com",
        "гитхаб": "https://github.com",
        "twitch": "https://www.twitch.tv",
        "твич": "https://www.twitch.tv",
    }
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        lowered = text.lower().strip()
        commands = self._get_commands()
        
        # Check for popular sites shortcuts first
        for keyword, url in self.POPULAR_SITES.items():
            if keyword in lowered:
                webbrowser.open(url)
                return PluginResult(success=True, response=f"Открываю {keyword}")
        
        # Regex matches
        if match:
            groups = match.groups()
            if groups:
                target = groups[0].strip()
                
                if "сайт" in lowered or "перейди" in lowered:
                    return self._open_website(target, commands)
                elif "вкладк" in lowered or "вкладку" in lowered:
                    return self._open_website(target, commands)
                elif "папк" in lowered:
                    return self._open_folder(target, commands)
                else:
                    return self._open_app(target, commands)
        
        return PluginResult(success=False)
    
    def _open_app(self, name: str, commands) -> PluginResult:
        if commands:
            response = commands.open_app(name)
        else:
            import os
            import subprocess
            try:
                subprocess.Popen(name, shell=True)
                response = f"Открываю {name}"
            except Exception as e:
                response = f"Не удалось открыть {name}: {e}"
        return PluginResult(success=True, response=response)
    
    def _open_website(self, url: str, commands) -> PluginResult:
        if commands:
            response = commands.open_website(url)
        else:
            if not url.startswith(("http://", "https://")):
                url = f"https://{url}"
            webbrowser.open(url)
            response = f"Открываю {url}"
        return PluginResult(success=True, response=response)
    
    def _open_folder(self, path: str, commands) -> PluginResult:
        if commands:
            response = commands.open_folder(path)
        else:
            import os
            if os.path.exists(path):
                os.startfile(path)
                response = f"Открываю {path}"
            else:
                response = f"Папка не найдена: {path}"
        return PluginResult(success=True, response=response)
    
    def get_help(self) -> str:
        return "Приложения: 'открой [приложение]', 'открой сайт [url]', 'открой папку [путь]'"
