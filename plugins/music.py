"""Music Plugin — Spotify, YouTube Music."""
import re
import webbrowser
from typing import Optional

from .base import BasePlugin, PluginResult


class MusicPlugin(BasePlugin):
    """Музыка: Spotify и YouTube Music."""
    
    name = "music"
    description = "Spotify и YouTube Music"
    version = "1.0.0"
    priority = 90
    
    triggers = [
        (r"включи музыку|spotify", "spotify"),
        (r"включи ютуб музыку|youtube music", "youtube_music"),
    ]
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        lowered = text.lower()
        commands = self._get_commands()
        
        if "ютуб музыку" in lowered or "youtube music" in lowered:
            webbrowser.open("https://music.youtube.com")
            return PluginResult(success=True, response="Открываю YouTube Music")
        elif any(k in lowered for k in ("включи музыку", "spotify")):
            if commands:
                return PluginResult(success=True, response=commands.open_app("spotify"))
            else:
                return PluginResult(success=False, response="Spotify недоступен")
        
        return PluginResult(success=False)
    
    def get_help(self) -> str:
        return "Музыка: 'включи музыку', 'Spotify', 'YouTube Music'"
