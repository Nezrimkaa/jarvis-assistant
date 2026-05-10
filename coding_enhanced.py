"""Enhanced Coding Assistant using LLM."""
import os
import tempfile
import subprocess
from typing import Optional

from config import Config


class CodeSandbox:
    """Safe code execution environment."""
    
    def execute_python(self, code: str) -> str:
        """Execute Python code safely."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            result = subprocess.run(
                ['python', temp_path],
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            os.unlink(temp_path)
            
            if result.returncode == 0:
                return f"Результат:\n{result.stdout}" if result.stdout else "Код выполнен успешно"
            else:
                return f"Ошибка:\n{result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Ошибка: код выполнялся слишком долго (timeout)"
        except Exception as e:
            return f"Ошибка выполнения: {e}"
    
    def analyze_code(self, code: str) -> str:
        """Analyze code for errors and improvements."""
        issues = []
        
        # Basic checks
        if "import os" in code and "os.system" in code:
            issues.append("⚠ Обнаружен потенциально опасный вызов os.system")
        
        if "eval(" in code or "exec(" in code:
            issues.append("⚠ Использование eval/exec может быть небезопасным")
        
        if not issues:
            return "✓ Базовая проверка пройдена"
        
        return "\n".join(issues)


class EnhancedCodingAssistant:
    """Enhanced coding assistant with LLM integration."""
    
    def __init__(self, brain=None):
        self.brain = brain
        self.sandbox = CodeSandbox()
    
    def generate_code(self, description: str, language: str = "python") -> str:
        """Generate code using LLM."""
        if self.brain:
            prompt = f"Напиши код на {language}: {description}"
            return self.brain.chat(prompt, [])
        
        # Fallback to templates
        return self._template_fallback(description, language)
    
    def _template_fallback(self, description: str, language: str) -> str:
        """Fallback code templates."""
        templates = {
            "python": f"# {description}\n# TODO: Implement\n\ndef main():\n    pass\n\nif __name__ == '__main__':\n    main()",
            "html": f"<!-- {description} -->\n<!DOCTYPE html>\n<html>\n<body>\n  <!-- TODO -->\n</body>\n</html>",
        }
        return templates.get(language, f"# {description}\n# TODO: Implement")
    
    def execute_and_fix(self, code: str, max_attempts: int = 3) -> str:
        """Execute code and auto-fix errors."""
        for attempt in range(max_attempts):
            result = self.sandbox.execute_python(code)
            
            if "Ошибка" not in result:
                return result
            
            if self.brain and attempt < max_attempts - 1:
                fix_prompt = f"Исправь ошибку в коде:\n\n{code}\n\nОшибка: {result}"
                code = self.brain.chat(fix_prompt, [])
                # Extract code from response
                if "```python" in code:
                    code = code.split("```python")[1].split("```")[0]
            else:
                return result
        
        return result
    
    def read_file(self, filepath: str) -> str:
        """Read file content."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Ошибка чтения: {e}"
    
    def save_file(self, filepath: str, content: str) -> str:
        """Save file."""
        try:
            os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Сохранено: {filepath}"
        except Exception as e:
            return f"Ошибка сохранения: {e}"
