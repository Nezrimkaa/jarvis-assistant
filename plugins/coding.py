"""Coding Plugin — создаёт файлы и код напрямую, без посредников."""
import os
import re
from typing import Optional

from .base import BasePlugin, PluginResult


class CodingPlugin(BasePlugin):
    """Создание файлов и кода напрямую через AI."""
    
    name = "coding"
    description = "Создание файлов, написание кода, помощь с программированием"
    version = "3.0.0"
    priority = 100
    
    # Триггеры для создания файлов и кода
    triggers = [
        # Создание файлов
        (r"создай\s+(?:файл|скрипт|программу|приложение)", "create"),
        (r"напиши\s+(?:код|скрипт|программу)", "create"),
        (r"сделай\s+(?:файл|скрипт|программу)", "create"),
        (r"запиши\s+(?:в\s+файл|файл)", "create"),
        # Помощь с кодом
        (r"помоги\s+(?:с\s+)?код", "help"),
        (r"помоги\s+(?:с\s+)?программированием", "help"),
        (r"как\s+(?:написать|сделать)\s+.*код", "help"),
        # Исправление
        (r"исправь\s+(?:код|ошибку|баг)", "fix"),
        (r"пофикси\s+(?:код|ошибку|баг)", "fix"),
        (r"не\s+работает\s+(?:код|программа)", "fix"),
        # Объяснение
        (r"объясни\s+(?:код|что\s+делает)", "explain"),
        (r"разберись\s+в\s+коде", "explain"),
        # Улучшение
        (r"улучши\s+код", "improve"),
        (r"рефакторинг\s+кода", "improve"),
        (r"оптимизируй\s+код", "improve"),
    ]
    
    def __init__(self, jarvis_instance=None):
        super().__init__(jarvis_instance)
        self.desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        self.documents = os.path.join(os.path.expanduser("~"), "Documents")
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        """Главный обработчик — создаём файлы напрямую."""
        lowered = text.lower()
        
        # Получаем доступ к brain (опционально, для fallback)
        brain = None
        if self.jarvis and hasattr(self.jarvis, 'brain'):
            brain = self.jarvis.brain
        
        # Определяем что делать локально (быстро)
        intent = self._detect_intent(lowered)
        
        if intent == "create":
            return self._create_file(text)
        elif intent == "help":
            return self._help_code(text, brain)
        elif intent == "fix":
            return self._fix_code(text, brain)
        elif intent == "explain":
            return self._explain_code(text, brain)
        elif intent == "improve":
            return self._improve_code(text, brain)
        else:
            # Если не определили — отдаём AI
            return self._ai_response(text, brain)
    
    def _detect_intent(self, text: str) -> str:
        """Определить намерение локально."""
        if any(k in text for k in ["создай", "напиши", "сделай", "запиши"]):
            if any(k in text for k in ["файл", "скрипт", "программ", "код", "приложение"]):
                return "create"
        if any(k in text for k in ["помоги", "помочь"]) and "код" in text:
            return "help"
        if any(k in text for k in ["исправь", "пофикси", "не работает"]):
            return "fix"
        if "объясни" in text and "код" in text:
            return "explain"
        if any(k in text for k in ["улучши", "рефакторинг", "оптимизируй"]):
            return "improve"
        return "general"
    
    def _create_file(self, text: str) -> PluginResult:
        """Создать файл напрямую."""
        # Определяем имя файла из запроса
        filename = self._extract_filename(text)
        if not filename:
            filename = "script.py"  # По умолчанию
        
        # Полный путь
        filepath = os.path.join(self.desktop, filename)
        
        # Генерируем содержимое через AI — напрямую в Ollama, без personality
        code = self._generate_code_direct(text)
        
        if not code:
            return PluginResult(
                success=False,
                response="Прошу прощения, сэр, не удалось сгенерировать код. Попробуйте ещё раз."
            )
        
        try:
            # Создаём файл
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            
            return PluginResult(
                success=True,
                response=f"Готово, сэр. Файл создан: {filepath}\n\n```python\n{code[:500]}{'...' if len(code) > 500 else ''}\n```"
            )
                
        except PermissionError:
            # Пробуем Documents если Desktop недоступен
            try:
                filepath = os.path.join(self.documents, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(code)
                return PluginResult(
                    success=True,
                    response=f"Готово, сэр. Файл сохранён в Documents: {filepath}"
                )
            except Exception as e:
                return PluginResult(
                    success=False,
                    response=f"Прошу прощения, сэр, нет прав на создание файла: {e}"
                )
        except Exception as e:
            return PluginResult(
                success=False,
                response=f"Прошу прощения, сэр, ошибка: {e}"
            )
    
    def _generate_code_direct(self, text: str) -> Optional[str]:
        """Генерировать код напрямую через Ollama, без personality system prompt."""
        try:
            import requests
            
            # Чистый prompt без personality
            prompt = f"""Ты — программист. Напиши код для запроса.
            
Запрос: {text}

ВАЖНО:
- Отвечай ТОЛЬКО кодом в markdown блоке
- Никаких объяснений до или после кода
- Только рабочий код

Формат:
```python
[код]
```"""
            
            # Прямой запрос к Ollama
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.1:8b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 2048
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "")
                
                # Извлекаем код
                code = self._extract_code(ai_response)
                if code:
                    return code
                
                # Если нет markdown — возвращаем весь ответ
                return ai_response.strip()
            
            return None
            
        except Exception as e:
            print(f"[CodingPlugin] Code generation error: {e}")
            return None
    
    def _extract_filename(self, text: str) -> Optional[str]:
        """Извлечь имя файла из текста."""
        # Ищем "файл something.py" или "назови something.py"
        patterns = [
            r'(?:файл|назови|имя)\s+["\']?(\S+\.(?:py|txt|html|js|css|bat|ps1|md))["\']?',
            r'(\S+\.(?:py|txt|html|js|css|bat|ps1|md))',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_code(self, text: str) -> Optional[str]:
        """Извлечь код из markdown блока."""
        # Ищем ```python ... ``` или просто ``` ... ```
        match = re.search(r'```(?:python)?\s*\n(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
    
    def _help_code(self, text: str, brain) -> PluginResult:
        """Помощь с кодом."""
        try:
            response = brain.chat(text, use_tools=False)
            return PluginResult(success=True, response=response)
        except Exception as e:
            return PluginResult(success=False, response=f"Ошибка: {e}")
    
    def _fix_code(self, text: str, brain) -> PluginResult:
        """Исправить код."""
        try:
            response = brain.chat(text, use_tools=False)
            return PluginResult(success=True, response=response)
        except Exception as e:
            return PluginResult(success=False, response=f"Ошибка: {e}")
    
    def _explain_code(self, text: str, brain) -> PluginResult:
        """Объяснить код."""
        try:
            response = brain.chat(text, use_tools=False)
            return PluginResult(success=True, response=response)
        except Exception as e:
            return PluginResult(success=False, response=f"Ошибка: {e}")
    
    def _improve_code(self, text: str, brain) -> PluginResult:
        """Улучшить код."""
        try:
            response = brain.chat(text, use_tools=False)
            return PluginResult(success=True, response=response)
        except Exception as e:
            return PluginResult(success=False, response=f"Ошибка: {e}")
    
    def _ai_response(self, text: str, brain) -> PluginResult:
        """Общий ответ от AI."""
        try:
            response = brain.chat(text, use_tools=False)
            return PluginResult(success=True, response=response)
        except Exception as e:
            return PluginResult(success=False, response=f"Ошибка: {e}")
