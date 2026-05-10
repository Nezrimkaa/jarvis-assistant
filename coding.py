"""Модуль кодинга для J.A.R.V.I.S. — генерация и выполнение кода."""
import os
import subprocess
import tempfile
from typing import Optional


class CodingAssistant:
    """Помощник по программированию."""

    def __init__(self):
        self.history = []
        
    def generate_code(self, description: str, language: str = "python") -> str:
        """Сгенерировать код по описанию."""
        # Простые шаблоны для быстрого ответа
        templates = {
            "python": self._generate_python_template,
            "javascript": self._generate_js_template,
            "html": self._generate_html_template,
            "batch": self._generate_batch_template,
        }
        
        if language.lower() in templates:
            return templates[language.lower()](description)
        
        return f"# Код на {language}:\n# {description}\n# TODO: реализовать"
    
    def _generate_python_template(self, desc: str) -> str:
        return f'''# {desc}
def main():
    print("{desc}")
    # TODO: Добавить логику
    
if __name__ == "__main__":
    main()
'''
    
    def _generate_js_template(self, desc: str) -> str:
        return f'''// {desc}
function main() {{
    console.log("{desc}");
    // TODO: Добавить логику
}}

main();
'''
    
    def _generate_html_template(self, desc: str) -> str:
        return f'''<!DOCTYPE html>
<html>
<head>
    <title>{desc}</title>
</head>
<body>
    <h1>{desc}</h1>
    <!-- TODO: Добавить контент -->
</body>
</html>
'''
    
    def _generate_batch_template(self, desc: str) -> str:
        return f'''@echo off
REM {desc}
echo {desc}
REM TODO: Добавить команды
pause
'''
    
    def execute_python(self, code: str) -> str:
        """Выполнить Python код."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file = f.name
            
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            os.unlink(temp_file)
            
            if result.returncode == 0:
                return f"✓ Результат:\n{result.stdout}"
            else:
                return f"✗ Ошибка:\n{result.stderr}"
                
        except Exception as e:
            return f"✗ Ошибка выполнения: {e}"
    
    def save_snippet(self, code: str, filename: str) -> str:
        """Сохранить код в файл."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)
            return f"✓ Код сохранён: {filename}"
        except Exception as e:
            return f"✗ Ошибка сохранения: {e}"
    
    def read_file(self, filepath: str) -> str:
        """Прочитать файл с кодом."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"✗ Ошибка чтения: {e}"
