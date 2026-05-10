"""Coding Plugin — code generation and execution."""
import os
import re
from typing import Optional

from .base import BasePlugin, PluginResult


class CodingPlugin(BasePlugin):
    """Программирование: генерация и выполнение кода."""
    
    name = "coding"
    description = "Генерация и выполнение кода"
    version = "1.2.0"
    priority = 110
    
    triggers = [
        # Создание файлов (ВЫСОКИЙ приоритет — должны быть первыми!)
        (r"создай файл питона\s+(.+)", "create_file"),
        (r"создай python файл\s+(.+)", "create_file"),
        (r"создай файл\s+(.+)", "create_file"),
        (r"создай питон\s+(.+)", "create_file"),
        (r"создай python\s+(.+)", "create_file"),
        # Генерация кода
        (r"напиши код\s+(.+)", "generate"),
        (r"создай скрипт\s+(.+)", "generate"),
        (r"напиши html\s+(.+)", "generate_html"),
        (r"создай страницу\s+(.+)", "generate_html"),
        (r"напиши batch\s+(.+)", "generate_batch"),
        (r"создай bat\s+(.+)", "generate_batch"),
        # Выполнение
        (r"выполни код\s+```(.+)```", "execute"),
        # Чтение файлов
        (r"покажи код\s+(.+)", "read"),
        (r"покажи файл\s+(.+)", "read"),
        # Сохранение
        (r"сохрани код|сохрани файл", "save"),
        # Помощь с кодом (широкие паттерны)
        (r"помоги.*код.*", "help_coding"),
        (r"помочь.*код.*", "help_coding"),
        (r"улучши.*код.*", "improve_code"),
        (r"улучшить.*код.*", "improve_code"),
        (r"рефакторинг.*", "improve_code"),
        (r"исправь.*код.*", "fix_code"),
        (r"пофикси.*код.*", "fix_code"),
        (r"объясни.*код.*", "explain_code"),
        (r"разберись.*код.*", "explain_code"),
        (r"добавь.*интеллект.*", "meta_improve"),
        (r"добавь себе.*интеллект.*", "meta_improve"),
        # Общие кодинг-запросы без захвата
        (r".*\bкод\b.*", "general_coding"),
        (r".*\bскрипт\b.*", "general_coding"),
        (r".*\bпрограммирование\b.*", "general_coding"),
        (r".*\bpython\b.*", "general_coding"),
        (r".*\bhtml\b.*", "general_coding"),
    ]
    
    def __init__(self, jarvis_instance=None):
        super().__init__(jarvis_instance)
        self._pending_save = None
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        lowered = text.lower()
        
        coding = None
        if self.jarvis and hasattr(self.jarvis, 'coding'):
            coding = self.jarvis.coding
        
        if coding is None:
            # Try to create file directly without coding assistant
            intent = self._detect_intent(lowered)
            if intent == "create_file":
                return self._create_file_direct(text, lowered)
            return PluginResult(success=True, response="Сэр, coding assistant временно недоступен, но я могу помочь с базовыми операциями.")
        
        # Determine intent from text
        intent = self._detect_intent(lowered)
        
        # Create file
        if intent == "create_file":
            return self._create_file(text, lowered, coding)
        
        # Execute Python
        if intent == "execute" or "выполни код" in lowered:
            if match:
                code = match.group(1).strip()
                return PluginResult(success=True, response=coding.execute_python(code))
            # Try to extract code from markdown blocks
            code_match = re.search(r'```(?:python)?\s*\n?(.+?)```', text, re.DOTALL)
            if code_match:
                return PluginResult(success=True, response=coding.execute_python(code_match.group(1).strip()))
            return PluginResult(success=False, response="Не вижу код для выполнения. Оберните его в ```код```")
        
        # Read file
        elif intent == "read" or any(k in lowered for k in ("покажи код", "покажи файл", "открой код")):
            if match and match.groups():
                filename = match.group(1).strip()
                return PluginResult(success=True, response=coding.read_file(filename))
            # Try to extract filename
            file_match = re.search(r'(?:файл|код)\s+["\']?([\w./\\~-]+)["\']?', lowered)
            if file_match:
                return PluginResult(success=True, response=coding.read_file(file_match.group(1)))
            return PluginResult(success=False, response="Укажите имя файла")
        
        # Save code
        elif intent == "save" or any(k in lowered for k in ("сохрани код", "сохрани файл")):
            save_match = re.search(r"сохрани код\s+в\s+(.+)", lowered)
            if save_match:
                self._pending_save = save_match.group(1).strip()
                return PluginResult(success=True, response="Отправьте код для сохранения")
            elif self._pending_save:
                result = coding.save_file(self._pending_save, text)
                self._pending_save = None
                return PluginResult(success=True, response=result)
            return PluginResult(success=False, response="Укажите путь для сохранения")
        
        # Help with coding / general questions
        elif intent in ("help_coding", "general_coding"):
            # Extract what user wants help with
            query = self._extract_query(text)
            if query:
                return PluginResult(
                    success=True, 
                    response=f"Конечно, сэр! {coding.generate_code(query, 'python')}"
                )
            return PluginResult(
                success=True,
                response="Сэр, я готов помочь с кодом. Что именно нужно? Напишите код, исправить, объяснить или улучшить?"
            )
        
        # Improve/refactor code
        elif intent == "improve_code":
            query = self._extract_query(text)
            if query:
                return PluginResult(
                    success=True,
                    response=f"Сэр, вот улучшенная версия:\n\n{coding.generate_code(f'Refactor and improve: {query}', 'python')}"
                )
            return PluginResult(
                success=True,
                response="Сэр, пришлите код для улучшения. Я могу оптимизировать, добавить комментарии или улучшить структуру."
            )
        
        # Fix code
        elif intent == "fix_code":
            query = self._extract_query(text)
            if query:
                return PluginResult(
                    success=True,
                    response=f"Сэр, исправленная версия:\n\n{coding.generate_code(f'Fix bugs in: {query}', 'python')}"
                )
            return PluginResult(
                success=True,
                response="Сэр, пришлите код с ошибкой. Я найду и исправлю проблемы."
            )
        
        # Explain code
        elif intent == "explain_code":
            query = self._extract_query(text)
            if query:
                return PluginResult(
                    success=True,
                    response=f"Сэр, разбор кода:\n\n{coding.generate_code(f'Explain this code in detail: {query}', 'python')}"
                )
            return PluginResult(
                success=True,
                response="Сэр, пришлите код для анализа. Я подробно объясню, как он работает."
            )
        
        # Meta-improve (add intelligence)
        elif intent == "meta_improve":
            return PluginResult(
                success=True,
                response="Сэр, я постоянно учусь! Для улучшения моих возможностей вы можете:\n1. Указать Hugging Face API ключ в настройках для облачного AI\n2. Загрузить более мощную модель в Ollama (например, qwen2.5:14b)\n3. Использовать команду 'напиши код' для сложных задач\n4. Включить плагины в разделе 'Плагины'\n\nЧем конкретнее могу помочь?"
            )
        
        # Default: generate code from match
        elif match and match.groups():
            query = match.group(1).strip()
            if "html" in lowered or "страниц" in lowered:
                return PluginResult(success=True, response=coding.generate_code(query, "html"))
            elif "batch" in lowered or "bat" in lowered:
                return PluginResult(success=True, response=coding.generate_code(query, "batch"))
            else:
                return PluginResult(success=True, response=coding.generate_code(query, "python"))
        
        # Last resort - try to help anyway
        return PluginResult(
            success=True,
            response="Сэр, я готов помочь с программированием. Что именно нужно сделать?"
        )
    
    def _create_file(self, text: str, lowered: str, coding) -> PluginResult:
        """Create a file with code."""
        import os
        
        # Determine path
        path = None
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        
        # Check for desktop reference
        if any(k in lowered for k in ("рабочий стол", "desktop", "стол")):
            path = desktop
        
        # Extract filename
        filename = None
        # Pattern: "создай файл [name] на рабочем столе"
        name_match = re.search(r'(?:файл|питон|python)\s+([\w\-]+)', lowered)
        if name_match:
            filename = name_match.group(1)
            if not filename.endswith('.py'):
                filename += '.py'
        
        # If no filename found, use default
        if not filename:
            filename = 'script.py'
        
        # Full path
        if path:
            filepath = os.path.join(path, filename)
        else:
            filepath = os.path.join(os.getcwd(), filename)
        
        # Extract code to write
        code = self._extract_code_from_text(text)
        if not code:
            # Generate code from description
            query = self._extract_query(text) or "hello world"
            code = coding.generate_code(query, 'python')
            # Extract just the code part if wrapped in markdown
            code_match = re.search(r'```python\s*\n?(.*?)```', code, re.DOTALL)
            if code_match:
                code = code_match.group(1).strip()
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            return PluginResult(
                success=True,
                response=f"Сэр, файл создан: {filepath}\n\nСодержимое:\n```python\n{code}\n```"
            )
        except Exception as e:
            return PluginResult(
                success=False,
                response=f"Сэр, ошибка при создании файла: {e}"
            )
    
    def _create_file_direct(self, text: str, lowered: str) -> PluginResult:
        """Create a file directly without coding assistant."""
        import os
        
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        path = desktop if any(k in lowered for k in ("рабочий стол", "desktop", "стол")) else os.getcwd()
        
        # Extract filename
        filename = None
        name_match = re.search(r'(?:файл|питон|python)\s+([\w\-]+)', lowered)
        if name_match:
            filename = name_match.group(1)
            if not filename.endswith('.py'):
                filename += '.py'
        
        if not filename:
            filename = 'script.py'
        
        filepath = os.path.join(path, filename)
        
        # Extract code from text or use default
        code = self._extract_code_from_text(text)
        if not code:
            # Check if user specified what to write
            if "print" in lowered or "принт" in lowered:
                if "hello" in lowered or "хелло" in lowered or "привет" in lowered:
                    code = 'print("Hello, World!")'
                else:
                    code = 'print("Hello")'
            else:
                code = '# Файл создан J.A.R.V.I.S.\nprint("Hello, World!")'
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            return PluginResult(
                success=True,
                response=f"Сэр, файл создан: {filepath}\n\nСодержимое:\n```python\n{code}\n```"
            )
        except Exception as e:
            return PluginResult(
                success=True,
                response=f"Сэр, ошибка при создании файла: {e}"
            )
    
    def _extract_code_from_text(self, text: str) -> str:
        """Extract code from user text."""
        # Look for code in markdown blocks
        code_match = re.search(r'```(?:python)?\s*\n?(.*?)```', text, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # Look for "напиши/напиши ... код ..." pattern
        code_match = re.search(r'(?:напиши|создай|напиши)\s+(?:код|скрипт)?\s*(?:который|чтобы|где)?\s*(.+)', text, re.IGNORECASE | re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        return ""
    
    def _detect_intent(self, text: str) -> str:
        """Detect coding intent from text."""
        if any(k in text for k in ("создай файл", "создай питон", "создай python", "создай файл питона", "создай python файл")):
            return "create_file"
        elif any(k in text for k in ("выполни код", "запусти код", "run code")):
            return "execute"
        elif any(k in text for k in ("покажи код", "покажи файл", "открой код", "read code")):
            return "read"
        elif any(k in text for k in ("сохрани код", "сохрани файл", "save code")):
            return "save"
        elif any(k in text for k in ("помоги с код", "помочь с код", "help with code", "кодинг")):
            return "help_coding"
        elif any(k in text for k in ("улучши код", "улучшить код", "рефакторинг", "refactor", "optimize")):
            return "improve_code"
        elif any(k in text for k in ("исправь код", "пофикси код", "fix code", "debug")):
            return "fix_code"
        elif any(k in text for k in ("объясни код", "разберись с код", "explain code")):
            return "explain_code"
        elif any(k in text for k in ("добавь интеллект", "добавь себе", "умней", " smarter")):
            return "meta_improve"
        return "general_coding"
    
    def _extract_query(self, text: str) -> Optional[str]:
        """Extract the actual query/payload from text."""
        # Try to extract after common prefixes
        prefixes = [
            r'(?:напиши|создай|помоги|помочь|улучши|улучшить|исправь|пофикси|объясни|разберись)\s+(?:с\s+)?(?:код|кодом|скрипт|программу|файл|питон|python)\s+(?:для|который|чтобы)?\s*',
            r'(?:мне нужен|мне нужно|хочу|нужен)\s+',
            r'(?:код|скрипт|файл)\s+(?:для|который|чтобы)?\s*',
        ]
        for prefix in prefixes:
            match = re.search(prefix + r'(.+)', text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def get_help(self) -> str:
        return (
            "Кодинг: 'напиши код [задача]', 'создай файл питона [имя] на рабочем столе', "
            "'помоги с кодом', 'улучши код', 'исправь код', 'объясни код'"
        )
