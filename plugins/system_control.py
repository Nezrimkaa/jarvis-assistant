"""System Control Plugin — volume, media, power, windows."""
import re
from typing import Optional

from .base import BasePlugin, PluginResult


class SystemControlPlugin(BasePlugin):
    """Управление системой: громкость, медиа, питание, окна."""
    
    name = "system_control"
    description = "Громкость, медиа, выключение, перезагрузка, окна"
    version = "1.0.0"
    priority = 50
    
    triggers = [
        (r"громче|увеличь громкость|погромче", "volume_up"),
        (r"тише|уменьши громкость|потише", "volume_down"),
        (r"выключи звук|mute|без звука|тишина", "mute"),
        (r"play|пауза|стоп|воспроизведение", "media_play"),
        (r"следующий трек|следующая|вперед", "media_next"),
        (r"предыдущий трек|предыдущая|назад", "media_prev"),
        (r"выключи компьютер сейчас|выключи пк сейчас|выключи немедленно", "shutdown_now"),
        (r"выключи компьютер|выключи пк|shutdown", "shutdown"),
        (r"перезагрузи компьютер сейчас|перезагрузи пк сейчас", "restart_now"),
        (r"перезагрузи компьютер|перезагрузи пк|restart|ребут", "restart"),
        (r"отмени выключение|отмени перезагрузку", "cancel_shutdown"),
        (r"спящий режим|засыпай|sleep|спи", "sleep"),
        (r"гибернация|режим гибернации|hibernate", "hibernate"),
        (r"заблокируй пк|заблокируй компьютер|lock|блокировка", "lock"),
        (r"выйди из системы|выход|logout", "logout"),
        (r"сверни все окна|свернуть все|минимизировать", "minimize_all"),
        (r"покажи рабочий стол|рабочий стол|desktop", "show_desktop"),
    ]
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        lowered = text.lower()
        commands = self._get_commands()
        
        if not commands:
            return PluginResult(success=False, response="Системное управление недоступно")
        
        # Volume
        if any(k in lowered for k in ("громче", "увеличь громкость", "погромче")):
            return PluginResult(success=True, response=commands.volume_up())
        elif any(k in lowered for k in ("тише", "уменьши громкость", "потише")):
            return PluginResult(success=True, response=commands.volume_down())
        elif any(k in lowered for k in ("выключи звук", "mute", "без звука", "тишина")):
            return PluginResult(success=True, response=commands.mute())
        
        # Media
        elif any(k in lowered for k in ("play", "пауза", "стоп", "воспроизведение")):
            return PluginResult(success=True, response=commands.media_play_pause())
        elif any(k in lowered for k in ("следующий трек", "следующая", "вперед")):
            return PluginResult(success=True, response=commands.media_next())
        elif any(k in lowered for k in ("предыдущий трек", "предыдущая", "назад")):
            return PluginResult(success=True, response=commands.media_prev())
        
        # Power
        elif any(k in lowered for k in ("выключи компьютер сейчас", "выключи пк сейчас", "выключи немедленно")):
            return PluginResult(success=True, response=commands.shutdown_now())
        elif any(k in lowered for k in ("выключи компьютер", "выключи пк", "shutdown")):
            return PluginResult(success=True, response=commands.shutdown())
        elif any(k in lowered for k in ("перезагрузи компьютер сейчас", "перезагрузи пк сейчас")):
            return PluginResult(success=True, response=commands.restart_now())
        elif any(k in lowered for k in ("перезагрузи компьютер", "перезагрузи пк", "restart", "ребут")):
            return PluginResult(success=True, response=commands.restart())
        elif any(k in lowered for k in ("отмени выключение", "отмени перезагрузку")):
            return PluginResult(success=True, response=commands.cancel_shutdown())
        elif any(k in lowered for k in ("спящий режим", "засыпай", "sleep", "спи")):
            return PluginResult(success=True, response=commands.sleep())
        elif any(k in lowered for k in ("гибернация", "режим гибернации", "hibernate")):
            return PluginResult(success=True, response=commands.hibernate())
        elif any(k in lowered for k in ("заблокируй пк", "заблокируй компьютер", "lock", "блокировка")):
            return PluginResult(success=True, response=commands.lock())
        elif any(k in lowered for k in ("выйди из системы", "выход", "logout")):
            return PluginResult(success=True, response=commands.logout())
        
        # Windows
        elif any(k in lowered for k in ("сверни все окна", "свернуть все", "минимизировать")):
            return PluginResult(success=True, response=commands.minimize_all_windows())
        elif any(k in lowered for k in ("покажи рабочий стол", "рабочий стол", "desktop")):
            return PluginResult(success=True, response=commands.show_desktop())
        
        return PluginResult(success=False)
    
    def get_help(self) -> str:
        return ("Система: 'громче', 'тише', 'выключи звук', 'пауза', "
                "'выключи компьютер', 'перезагрузи', 'спящий режим', 'сверни окна'")
