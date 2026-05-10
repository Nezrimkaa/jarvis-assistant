"""Keyboard Plugin — type text and press keys."""
import re
from typing import Optional

from .base import BasePlugin, PluginResult


class KeyboardPlugin(BasePlugin):
    """Клавиатура: набор текста и нажатие клавиш."""
    
    name = "keyboard"
    description = "Набор текста и нажатие клавиш"
    version = "1.0.0"
    priority = 150
    
    triggers = [
        (r"напечатай\s+(.+)", "type"),
        (r"напиши\s+(.+)", "type"),
        (r"нажми\s+(.+)", "press"),
    ]
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        lowered = text.lower()
        commands = self._get_commands()
        
        if not commands:
            return PluginResult(success=False, response="Управление клавиатурой недоступно")
        
        if match:
            content = match.group(1).strip()
            
            if any(k in lowered for k in ("напечатай", "напиши")):
                return PluginResult(success=True, response=commands.type_text(content))
            elif "нажми" in lowered:
                return PluginResult(success=True, response=commands.press_key(content))
        
        return PluginResult(success=False)
    
    def get_help(self) -> str:
        return "Клавиатура: 'напечатай [текст]', 'нажми [клавиша]'"
