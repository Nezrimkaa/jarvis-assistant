"""Network Plugin — internet, IP, ping, clipboard."""
import re
import pyperclip
from typing import Optional

from .base import BasePlugin, PluginResult


class NetworkPlugin(BasePlugin):
    """Сеть: интернет, IP, ping, буфер обмена."""
    
    name = "network"
    description = "Проверка интернета, IP, ping, буфер обмена"
    version = "1.0.0"
    priority = 140
    
    triggers = [
        (r"интернет|скорость интернета|ping", "internet"),
        (r"мой ip|ip адрес|какой у меня ip", "ip"),
        (r"очисти буфер|очистить буфер обмена", "clear_clipboard"),
    ]
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        lowered = text.lower()
        commands = self._get_commands()
        
        if any(k in lowered for k in ("интернет", "скорость интернета", "ping")):
            if commands:
                return PluginResult(success=True, response=commands.run_command("ping google.com -n 4"))
            else:
                import subprocess
                try:
                    result = subprocess.run("ping google.com -n 4", shell=True, capture_output=True, text=True)
                    return PluginResult(success=True, response=result.stdout or "Ping выполнен")
                except Exception as e:
                    return PluginResult(success=False, response=f"Ошибка ping: {e}")
        
        elif any(k in lowered for k in ("мой ip", "ip адрес", "какой у меня ip")):
            if commands:
                return PluginResult(success=True, response=commands.run_command("ipconfig"))
            else:
                import subprocess
                try:
                    result = subprocess.run("ipconfig", shell=True, capture_output=True, text=True)
                    return PluginResult(success=True, response=result.stdout or "IP информация получена")
                except Exception as e:
                    return PluginResult(success=False, response=f"Ошибка: {e}")
        
        elif any(k in lowered for k in ("очисти буфер", "очистить буфер обмена")):
            try:
                pyperclip.copy("")
                return PluginResult(success=True, response="Буфер обмена очищен")
            except Exception as e:
                return PluginResult(success=False, response=f"Ошибка: {e}")
        
        return PluginResult(success=False)
    
    def get_help(self) -> str:
        return "Сеть: 'интернет', 'мой IP', 'очисти буфер'"
