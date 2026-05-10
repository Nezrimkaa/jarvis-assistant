"""Mood Plugin — change AI personality/mood."""
import re
from typing import Optional

from .base import BasePlugin, PluginResult


class MoodPlugin(BasePlugin):
    """Настроение: изменение стиля общения AI."""
    
    name = "mood"
    description = "Изменение настроения и стиля общения"
    version = "1.0.0"
    priority = 120
    
    triggers = [
        (r"настроение\s+(.+)", "set_mood"),
        (r"будь дружелюбным|будь добрым", "friendly"),
        (r"будь серь[её]зным|будь строгим", "strict"),
        (r"пошути|будь вес[её]лым", "humorous"),
        (r"будь официальным|будь формальным", "formal"),
    ]
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        lowered = text.lower()
        brain = self._get_brain()
        
        if brain is None:
            return PluginResult(success=False, response="AI мозг недоступен")
        
        mood = None
        response = ""
        
        if match and "настроение" in lowered:
            mood = match.group(1).strip()
            response = f"Настроение изменено на: {mood}. Буду общаться соответственно, сэр."
        elif any(k in lowered for k in ("дружелюбн", "добрым")):
            mood = "friendly"
            response = "Конечно, сэр! Буду более дружелюбным и тёплым."
        elif any(k in lowered for k in ("серьёзн", "серьезн", "строгим")):
            mood = "strict"
            response = "Понял, сэр. Перехожу в строгий режим. Только по делу."
        elif any(k in lowered for k in ("пошути", "весёлым", "веселым")):
            mood = "humorous"
            response = "С удовольствием, сэр! Готов шутить и подшучивать."
        elif any(k in lowered for k in ("официальн", "формальн")):
            mood = "formal"
            response = "Как скажете, сэр. Буду общаться на 'Вы' и официально."
        else:
            return PluginResult(success=False)
        
        brain.update_context("mood", mood)
        return PluginResult(success=True, response=response)
    
    def get_help(self) -> str:
        return "Настроение: 'будь дружелюбным', 'будь серьёзным', 'будь весёлым'"
