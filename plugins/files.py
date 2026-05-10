"""Files Plugin — screenshot, folders, recycle bin, explorer."""
import re
from typing import Optional

from .base import BasePlugin, PluginResult


class FilesPlugin(BasePlugin):
    """Файлы и папки: скриншот, корзина, проводник, создание папок."""
    
    name = "files"
    description = "Скриншоты, папки, корзина, проводник"
    version = "1.0.0"
    priority = 60
    
    triggers = [
        (r"скриншот|снимок экрана|screenshot|фото экрана", "screenshot"),
        (r"очисти корзину|пустая корзина|удали корзину", "empty_bin"),
        (r"перезапусти проводник|explorer|проводник", "restart_explorer"),
        (r"создай папку\s+(.+)", "create_folder"),
    ]
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        lowered = text.lower()
        commands = self._get_commands()
        
        if not commands:
            return PluginResult(success=False, response="Файловые операции недоступны")
        
        if any(k in lowered for k in ("скриншот", "снимок экрана", "screenshot", "фото экрана")):
            return PluginResult(success=True, response=commands.screenshot())
        elif any(k in lowered for k in ("очисти корзину", "пустая корзина", "удали корзину")):
            return PluginResult(success=True, response=commands.empty_recycle_bin())
        elif any(k in lowered for k in ("перезапусти проводник", "explorer", "проводник")):
            return PluginResult(success=True, response=commands.restart_explorer())
        elif match and "создай папку" in lowered:
            folder_name = match.group(1).strip()
            return PluginResult(success=True, response=commands.create_folder(folder_name))
        
        return PluginResult(success=False)
    
    def get_help(self) -> str:
        return "Файлы: 'скриншот', 'очисти корзину', 'создай папку [имя]'"
