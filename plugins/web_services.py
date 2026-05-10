"""Web Services Plugin — weather, news, maps, translator."""
import re
from typing import Optional

from .base import BasePlugin, PluginResult


class WebServicesPlugin(BasePlugin):
    """Веб-сервисы: погода, новости, карты, переводчик."""
    
    name = "web_services"
    description = "Погода, новости, карты, переводчик"
    version = "1.0.0"
    priority = 80
    
    triggers = [
        (r"погода(?:\s+в\s+(.+))?", "weather"),
        (r"новости|покажи новости", "news"),
        (r"карты|открой карты|покажи на карте(?:\s+(.+))?", "maps"),
        (r"переведи(?:\s+(.+))?|переводчик|перевод", "translate"),
    ]
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        lowered = text.lower()
        commands = self._get_commands()
        
        if not commands:
            return PluginResult(success=False, response="Веб-сервисы недоступны")
        
        # Weather
        if "погода" in lowered:
            city = None
            if match and match.lastindex and match.lastindex >= 1:
                city = match.group(1)
            elif "погода в" in lowered:
                parts = lowered.split("погода в")
                if len(parts) > 1:
                    city = parts[1].strip()
            return PluginResult(success=True, response=commands.get_weather(city))
        
        # News
        elif any(k in lowered for k in ("новости", "покажи новости")):
            return PluginResult(success=True, response=commands.get_news())
        
        # Maps
        elif any(k in lowered for k in ("карты", "открой карты", "покажи на карте")):
            location = None
            if match and match.lastindex and match.lastindex >= 1:
                location = match.group(1)
            elif "на карте" in lowered:
                parts = lowered.split("на карте")
                if len(parts) > 1:
                    location = parts[1].strip()
            return PluginResult(success=True, response=commands.open_maps(location))
        
        # Translate
        elif any(k in lowered for k in ("переведи", "переводчик", "перевод")):
            text_to_translate = None
            if match and match.lastindex and match.lastindex >= 1:
                text_to_translate = match.group(1)
            elif "переведи" in lowered:
                parts = lowered.split("переведи")
                if len(parts) > 1:
                    text_to_translate = parts[1].strip()
            return PluginResult(success=True, response=commands.translate(text_to_translate))
        
        return PluginResult(success=False)
    
    def get_help(self) -> str:
        return "Веб: 'погода', 'новости', 'карты [место]', 'переведи [текст]'"
