"""System Info Plugin — time, date, system info."""
import re
from datetime import datetime
from typing import Optional

from .base import BasePlugin, PluginResult


class SystemInfoPlugin(BasePlugin):
    """Время, дата и системная информация."""
    
    name = "system_info"
    description = "Время, дата, информация о системе"
    version = "1.0.0"
    priority = 20
    
    triggers = [
        (r"сколько время|который час|время|час", "time"),
        (r"какое сегодня число|дата|число|какой день", "date"),
        (r"процессор|оперативка|память|диск|система|производительность", "system"),
    ]
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        lowered = text.lower()
        
        if any(k in lowered for k in ("время", "час")):
            return self.get_time(text, match)
        elif any(k in lowered for k in ("дата", "число", "день")):
            return self.get_date(text, match)
        elif any(k in lowered for k in ("процессор", "оперативка", "память", "диск", "система", "производительность")):
            return self.get_system(text, match)
        
        return PluginResult(success=False)
    
    def get_time(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        now = datetime.now()
        response = f"Текущее время: {now.strftime('%H:%M:%S')}"
        return PluginResult(success=True, response=response)
    
    def get_date(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        now = datetime.now()
        response = f"Сегодня {now.strftime('%d.%m.%Y')}, {now.strftime('%A')}"
        return PluginResult(success=True, response=response)
    
    def get_system(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        commands = self._get_commands()
        if commands:
            response = commands.get_system_info()
        else:
            response = "Информация о системе недоступна"
        return PluginResult(success=True, response=response)
    
    def get_help(self) -> str:
        return "Время: 'сколько время', 'дата', 'системная информация'"
