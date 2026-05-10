"""Greeting Plugin — handles hellos and goodbyes."""
import re
from typing import Optional

from .base import BasePlugin, PluginResult


class GreetingPlugin(BasePlugin):
    """Приветствия и прощания."""
    
    name = "greeting"
    description = "Приветствия, прощания и базовые реплики"
    version = "1.0.0"
    priority = 10
    
    triggers = [
        (r"\bпривет\b|\bздравствуй\b|\bдобрый день\b|\bдоброе утро\b|\bдобрый вечер\b|\bхай\b|\bздарова\b|\bздрасьте\b", "greet"),
        (r"\bпока\b|\bдо свидания\b|\bвыход\b|\bзавершить\b|\bспокойной ночи\b|\bбай\b|\bдо встречи\b|\bпрощай\b", "farewell"),
        (r"\bспасибо\b|\bблагодарю\b|\bспс\b|\bthx\b|\bблагодарен\b|\bспасибочки\b", "thanks"),
    ]
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        """Route to specific handler based on match."""
        lowered = text.lower()
        
        if any(k in lowered for k in ("привет", "здравствуй", "добрый день", "доброе утро", "добрый вечер", "хай", "здарова", "здрасьте")):
            return self.greet(text, match)
        elif any(k in lowered for k in ("до свидания", "выход", "завершить", "спокойной ночи", "бай", "до встречи", "прощай")) or lowered.strip() == "пока":
            return self.farewell(text, match)
        elif any(k in lowered for k in ("спасибо", "благодарю", "спс", "thx", "благодарен", "спасибочки")):
            return self.thanks(text, match)
        
        return PluginResult(success=False)
    
    def greet(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        """Приветствие."""
        brain = self._get_brain()
        if brain:
            response = brain._smart_fallback(text, "greeting")
        else:
            response = "Приветствую, сэр. J.A.R.V.I.S. к вашим услугам."
        return PluginResult(success=True, response=response)
    
    def farewell(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        """Прощание."""
        brain = self._get_brain()
        if brain:
            response = brain._smart_fallback(text, "farewell")
        else:
            response = "До свидания, сэр. Всегда к вашим услугам."
        return PluginResult(success=True, response=response)
    
    def thanks(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        """Ответ на благодарность."""
        brain = self._get_brain()
        if brain:
            response = brain._smart_fallback(text, "thanks")
        else:
            response = "Всегда пожалуйста, сэр! Рад быть полезным."
        return PluginResult(success=True, response=response)
    
    def get_help(self) -> str:
        return "Приветствия: 'привет', 'пока', 'спасибо'"
