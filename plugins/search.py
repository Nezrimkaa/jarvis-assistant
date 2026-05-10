"""Search Plugin — Google, YouTube, Yandex, Wikipedia search."""
import re
from typing import Optional

from .base import BasePlugin, PluginResult


class SearchPlugin(BasePlugin):
    """Поиск в интернете."""
    
    name = "search"
    description = "Поиск в Google, YouTube, Yandex, Википедии"
    version = "1.0.0"
    priority = 40
    
    triggers = [
        (r"поищи\s+(.+)", "search"),
        (r"найди в гугл\s+(.+)", "google"),
        (r"найди на ютуб\s+(.+)", "youtube"),
        (r"youtube\s+(.+)", "youtube"),
        (r"найди в яндексе\s+(.+)", "yandex"),
        (r"поищи в яндексе\s+(.+)", "yandex"),
        (r"википедия\s+(.+)", "wikipedia"),
        (r"что такое\s+(.+)", "wikipedia"),
    ]
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        if not match:
            return PluginResult(success=False)
        
        query = match.group(1).strip()
        lowered = text.lower()
        commands = self._get_commands()
        
        if not commands:
            return PluginResult(success=False, response="Поиск временно недоступен")
        
        if "ютуб" in lowered or "youtube" in lowered:
            response = commands.search_youtube(query)
        elif "яндекс" in lowered:
            response = commands.search_yandex(query)
        elif "википеди" in lowered or "что такое" in lowered:
            response = commands.search_wikipedia(query)
        else:
            response = commands.search_google(query)
        
        return PluginResult(success=True, response=response)
    
    def get_help(self) -> str:
        return "Поиск: 'поищи [запрос]', 'найди в яндексе [запрос]', 'википедия [статья]'"
