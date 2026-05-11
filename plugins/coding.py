"""Coding Plugin — intelligent code assistant using AI context."""
import os
import re
from typing import Optional

from .base import BasePlugin, PluginResult


class CodingPlugin(BasePlugin):
    """Умный помощник по программированию — работает через AI контекст."""
    
    name = "coding"
    description = "Генерация кода, создание файлов, помощь с программированием"
    version = "2.0.0"
    priority = 100
    
    # Больше НЕТ жёстких триггеров — AI сам решает что делать
    triggers = [
        (r".*", "ai_handle")  # Любой текст — передаём AI
    ]
    
    def __init__(self, jarvis_instance=None):
        super().__init__(jarvis_instance)
        self._pending_save = None
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        """Обработать запрос через AI — без жёстких триггеров."""
        lowered = text.lower()
        
        # Получаем доступ к brain
        brain = None
        if self.jarvis and hasattr(self.jarvis, 'brain'):
            brain = self.jarvis.brain
        
        if brain is None:
            return PluginResult(
                success=False, 
                response="Сэр, система AI временно недоступна. Попробуйте позже."
            )
        
        # Определяем намерение через AI
        intent_prompt = f"""Анализируй запрос пользователя и определи намерение:
        
Запрос: {text}

Возможные намерения:
- create_file: создать файл (если просят "создай файл", "напиши скрипт", "сделай программу")
- write_code: написать код (если просят "напиши код", "как сделать", "помоги с кодом")
- explain_code: объяснить код (если просят "объясни", "разберись", "что делает")
- fix_code: исправить код (если просят "исправь", "пофикси", "не работает")
- improve_code: улучшить код (если просят "улучши", "рефакторинг", "оптимизируй")
- general: общий вопрос

Ответь ТОЛЬКО одним словом: create_file, write_code, explain_code, fix_code, improve_code, или general"""
        
        try:
            intent = brain.chat(intent_prompt, use_tools=False).strip().lower()
        except:
            intent = "general"
        
        # Обрабатываем по намерению
        if intent == "create_file":
            return self._create_file_ai(text, brain)
        elif intent == "write_code":
            return self._write_code_ai(text, brain)
        elif intent == "explain_code":
            return self._explain_code_ai(text, brain)
        elif intent == "fix_code":
            return self._fix_code_ai(text, brain)
        elif intent == "improve_code":
            return self._improve_code_ai(text, brain)
        else:
            # Общий запрос — просто отдаём AI
            return self._general_ai(text, brain)
    
    def _create_file_ai(self, text: str, brain) -> PluginResult:
        """Создать файл через AI."""
        # Получаем реальный путь к рабочему столу
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
        prompt = f"""Пользователь просит создать файл.
        
Запрос: {text}

ВАЖНО: Рабочий стол пользователя находится здесь: {desktop_path}
Используй ТОЛЬКО этот путь. Не используй /Users/ или другие пути.

Твоя задача:
1. Определи имя файла
2. Напиши содержимое файла
3. Ответь в формате:
   ФАЙЛ: {desktop_path}\\[имя_файла]
   ```[язык]
   [содержимое]
   ```

Пиши РАБОЧИЙ код с комментариями."""
        
        try:
            response = brain.chat(prompt, use_tools=False)
            
            # Извлекаем файл и создаём
            file_match = re.search(r'ФАЙЛ:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
            code_match = re.search(r'```(?:\w+)?\s*\n(.*?)```', response, re.DOTALL)
            
            if file_match and code_match:
                filepath = file_match.group(1).strip()
                code = code_match.group(1).strip()
                
                # Фиксим путь если AI написал неправильный
                if "/Users/" in filepath or "/Users\\" in filepath:
                    # AI сгенерировал маковский путь — заменяем
                    filename = os.path.basename(filepath.replace("/", "\\"))
                    filepath = os.path.join(desktop_path, filename)
                
                # Создаём директории если нужно
                dir_path = os.path.dirname(os.path.abspath(filepath))
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)
                
                # Записываем файл
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                return PluginResult(
                    success=True,
                    response=f"Готово, сэр. Файл создан: {filepath}"
                )
            else:
                # Не смогли распарсить — просто показываем ответ
                return PluginResult(
                    success=True,
                    response=f"Сэр, вот что я подготовил:\n\n{response}"
                )
        except PermissionError as e:
            return PluginResult(
                success=False,
                response=f"Прошу прощения, сэр, нет прав на запись в эту папку. Попробуйте сохранить на рабочий стол или в Documents."
            )
        except Exception as e:
            return PluginResult(
                success=False,
                response=f"Прошу прощения, сэр, при создании файла возникла ошибка: {e}"
            )
    
    def _write_code_ai(self, text: str, brain) -> PluginResult:
        """Написать код через AI."""
        prompt = f"""Пользователь просит написать код.
        
Запрос: {text}

Напиши рабочий код с комментариями. Объясни кратко что делает."""
        
        try:
            response = brain.chat(prompt, use_tools=False)
            return PluginResult(success=True, response=response)
        except Exception as e:
            return PluginResult(
                success=False,
                response=f"Прошу прощения, сэр, ошибка при генерации кода: {e}"
            )
    
    def _explain_code_ai(self, text: str, brain) -> PluginResult:
        """Объяснить код через AI."""
        prompt = f"""Пользователь просит объяснить код.
        
Запрос: {text}

Подробно объясни, как работает этот код, построчно если нужно."""
        
        try:
            response = brain.chat(prompt, use_tools=False)
            return PluginResult(success=True, response=response)
        except Exception as e:
            return PluginResult(
                success=False,
                response=f"Прошу прощения, сэр, ошибка: {e}"
            )
    
    def _fix_code_ai(self, text: str, brain) -> PluginResult:
        """Исправить код через AI."""
        prompt = f"""Пользователь просит исправить код.
        
Запрос: {text}

Найди ошибки и исправь их. Объясни что было не так."""
        
        try:
            response = brain.chat(prompt, use_tools=False)
            return PluginResult(success=True, response=response)
        except Exception as e:
            return PluginResult(
                success=False,
                response=f"Прошу прощения, сэр, ошибка: {e}"
            )
    
    def _improve_code_ai(self, text: str, brain) -> PluginResult:
        """Улучшить код через AI."""
        prompt = f"""Пользователь просит улучшить код.
        
Запрос: {text}

Улучши код: оптимизируй, добавь комментарии, улучши структуру. Объясни изменения."""
        
        try:
            response = brain.chat(prompt, use_tools=False)
            return PluginResult(success=True, response=response)
        except Exception as e:
            return PluginResult(
                success=False,
                response=f"Прошу прощения, сэр, ошибка: {e}"
            )
    
    def _general_ai(self, text: str, brain) -> PluginResult:
        """Общий запрос — просто ответ через AI."""
        try:
            response = brain.chat(text, use_tools=False)
            return PluginResult(success=True, response=response)
        except Exception as e:
            return PluginResult(
                success=False,
                response=f"Прошу прощения, сэр, ошибка: {e}"
            )
