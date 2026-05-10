"""Autostart Plugin — manage Windows autostart."""
import re
from typing import Optional

from .base import BasePlugin, PluginResult


class AutostartPlugin(BasePlugin):
    """Автозапуск: включение и выключение."""
    
    name = "autostart"
    description = "Управление автозапуском с Windows"
    version = "1.0.0"
    priority = 160
    
    triggers = [
        (r"включи автозапуск|автозапуск включи", "enable"),
        (r"выключи автозапуск|автозапуск выключи", "disable"),
    ]
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        lowered = text.lower()
        
        # We need to import autostart functions directly
        try:
            from autostart import enable_startup, disable_startup
        except ImportError:
            return PluginResult(success=False, response="Модуль автозапуска недоступен")
        
        if any(k in lowered for k in ("включи автозапуск", "автозапуск включи")):
            if enable_startup():
                return PluginResult(
                    success=True,
                    response="Автозапуск включен. J.A.R.V.I.S. будет запускаться с Windows."
                )
            return PluginResult(success=False, response="Не удалось включить автозапуск.")
        
        elif any(k in lowered for k in ("выключи автозапуск", "автозапуск выключи")):
            if disable_startup():
                return PluginResult(success=True, response="Автозапуск отключен.")
            return PluginResult(success=False, response="Не удалось отключить автозапуск.")
        
        return PluginResult(success=False)
    
    def get_help(self) -> str:
        return "Автозапуск: 'включи автозапуск', 'выключи автозапуск'"
