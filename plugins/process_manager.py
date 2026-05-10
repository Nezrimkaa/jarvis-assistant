"""Process Manager Plugin — kill processes."""
import re
from typing import Optional

from .base import BasePlugin, PluginResult


class ProcessManagerPlugin(BasePlugin):
    """Управление процессами: завершение."""
    
    name = "process_manager"
    description = "Завершение процессов"
    version = "1.0.0"
    priority = 170
    
    triggers = [
        (r"закрой процесс\s+(.+)", "kill"),
        (r"заверши процесс\s+(.+)", "kill"),
    ]
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        commands = self._get_commands()
        
        if not commands:
            return PluginResult(success=False, response="Управление процессами недоступно")
        
        if match:
            process_name = match.group(1).strip()
            return PluginResult(success=True, response=commands.kill_process(process_name))
        
        return PluginResult(success=False)
    
    def get_help(self) -> str:
        return "Процессы: 'закрой процесс [имя]'"
