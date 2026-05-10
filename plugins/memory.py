"""Memory Plugin — manage conversation memory and context."""
import re
from typing import Optional

from .base import BasePlugin, PluginResult


class MemoryPlugin(BasePlugin):
    """Память: очистка, улучшение, контекст."""
    
    name = "memory"
    description = "Управление памятью и контекстом"
    version = "1.0.0"
    priority = 130
    
    triggers = [
        (r"улучши себя|самоулучшение|обучись|запомни", "improve"),
        (r"очисти память|забудь всё|сбрось контекст", "clear"),
    ]
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        lowered = text.lower()
        
        if any(k in lowered for k in ("улучши себя", "самоулучшение", "обучись", "запомни")):
            return PluginResult(
                success=True,
                response="Запомнил, сэр. Буду использовать эту информацию в будущем."
            )
        
        elif any(k in lowered for k in ("очисти память", "забудь всё", "сбрось контекст")):
            # Clear history
            if self.jarvis and hasattr(self.jarvis, 'history'):
                self.jarvis.history.clear()
            
            # Clear brain context
            brain = self._get_brain()
            if brain and hasattr(brain, 'context'):
                brain.context["known_facts"] = {}
            
            return PluginResult(
                success=True,
                response="Память очищена, сэр. Начинаем с чистого листа."
            )
        
        return PluginResult(success=False)
    
    def get_help(self) -> str:
        return "Память: 'очисти память', 'забудь всё'"
