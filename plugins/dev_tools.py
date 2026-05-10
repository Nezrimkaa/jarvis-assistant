"""Dev Tools Plugin — VS Code, terminal, task manager, calculator, settings."""
import re
from typing import Optional

from .base import BasePlugin, PluginResult


class DevToolsPlugin(BasePlugin):
    """Инструменты разработки и системные утилиты."""
    
    name = "dev_tools"
    description = "VS Code, терминал, диспетчер задач, калькулятор, настройки"
    version = "1.0.0"
    priority = 70
    
    triggers = [
        (r"открой вс код|открой vscode|открой code", "vscode"),
        (r"открой терминал|открой cmd|командная строка", "cmd"),
        (r"открой powershell|powershell", "powershell"),
        (r"открой git bash|git bash", "git_bash"),
        (r"диспетчер задач|task manager", "taskmgr"),
        (r"калькулятор", "calc"),
        (r"настройки|параметры", "settings"),
        (r"панель управления|control panel", "control"),
    ]
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        lowered = text.lower()
        commands = self._get_commands()
        
        if not commands:
            return PluginResult(success=False, response="Утилиты недоступны")
        
        if any(k in lowered for k in ("вс код", "vscode", "code")):
            return PluginResult(success=True, response=commands.open_app("vscode"))
        elif any(k in lowered for k in ("терминал", "cmd", "командная строка")):
            return PluginResult(success=True, response=commands.open_cmd())
        elif "powershell" in lowered:
            return PluginResult(success=True, response=commands.open_powershell())
        elif "git bash" in lowered:
            return PluginResult(success=True, response=commands.open_app("git bash"))
        elif any(k in lowered for k in ("диспетчер задач", "task manager")):
            return PluginResult(success=True, response=commands.open_task_manager())
        elif "калькулятор" in lowered:
            return PluginResult(success=True, response=commands.open_calculator())
        elif any(k in lowered for k in ("настройки", "параметры")):
            return PluginResult(success=True, response=commands.open_settings())
        elif any(k in lowered for k in ("панель управления", "control panel")):
            return PluginResult(success=True, response=commands.open_control_panel())
        
        return PluginResult(success=False)
    
    def get_help(self) -> str:
        return "Утилиты: 'открой VS Code', 'терминал', 'диспетчер задач', 'калькулятор'"
