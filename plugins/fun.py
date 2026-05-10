"""Fun Plugin — jokes, facts, motivation, compliments."""
import re
from typing import Optional

from .base import BasePlugin, PluginResult


class FunPlugin(BasePlugin):
    """Развлечения: шутки, факты, мотивация, комплименты."""
    
    name = "fun"
    description = "Шутки, факты, мотивация, комплименты"
    version = "1.0.0"
    priority = 100
    
    triggers = [
        (r"шутка|пошути|анекдот|рассмеши|юмор", "joke"),
        (r"интересный факт|факт|расскажи факт", "fact"),
        (r"мотивация|мотивируй|вдохнови|не могу|устал", "motivation"),
        (r"совет|посоветуй|что делать|как быть", "advice"),
        (r"комплимент|похвали|скажи что-то приятное", "compliment"),
    ]
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        lowered = text.lower()
        brain = self._get_brain()
        history = self._get_history()
        
        if brain is None:
            return PluginResult(success=False, response="AI мозг недоступен")
        
        if any(k in lowered for k in ("шутка", "пошути", "анекдот", "рассмеши", "юмор")):
            response = brain.chat("расскажи шутку", history)
        elif any(k in lowered for k in ("интересный факт", "факт", "расскажи факт")):
            response = brain.chat("расскажи интересный факт", history)
        elif any(k in lowered for k in ("мотивация", "мотивируй", "вдохнови", "не могу", "устал")):
            response = brain.chat("помотивируй меня", history)
        elif any(k in lowered for k in ("совет", "посоветуй", "что делать", "как быть")):
            response = brain.chat("дай совет", history)
        elif any(k in lowered for k in ("комплимент", "похвали", "скажи что-то приятное")):
            response = brain.chat("скажи комплимент", history)
        else:
            return PluginResult(success=False)
        
        return PluginResult(success=True, response=response)
    
    def get_help(self) -> str:
        return "Развлечения: 'шутка', 'факт', 'мотивация', 'совет', 'комплимент'"
