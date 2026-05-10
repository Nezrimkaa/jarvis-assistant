"""GitHub Plugin — repository management and code operations."""
import re
from typing import Optional

from .base import BasePlugin, PluginResult


class GitHubPlugin(BasePlugin):
    """GitHub: чтение репозиториев, поиск кода, управление файлами."""
    
    name = "github"
    description = "GitHub: репозитории, код, коммиты, issues"
    version = "1.0.0"
    priority = 35  # Before app_launcher
    
    triggers = [
        (r"github|гитхаб|репозиторий|repo", "github"),
        (r"покажи код из\s+(.+)", "show_code"),
        (r"найди в github\s+(.+)", "search"),
        (r"прочитай файл\s+(.+)", "read_file"),
    ]
    
    def __init__(self, jarvis_instance=None):
        super().__init__(jarvis_instance)
        self._github = None
    
    def _get_github(self):
        """Lazy initialization of GitHub client."""
        if self._github is None:
            try:
                from github.client import GitHubClient
                self._github = GitHubClient()
            except ImportError:
                pass
        return self._github
    
    def execute(self, text: str, match: Optional[re.Match] = None) -> PluginResult:
        github = self._get_github()
        
        if not github or not github.is_authenticated():
            return PluginResult(
                success=True,
                response="GitHub не настроен. Добавьте GITHUB_TOKEN в .env файл."
            )
        
        lowered = text.lower()
        
        # Parse owner/repo from text
        repo_match = re.search(r"([\w-]+)/([\w-]+)", text)
        if not repo_match:
            return PluginResult(
                success=True,
                response="Укажите репозиторий в формате owner/repo"
            )
        
        owner, repo = repo_match.groups()
        
        # Read file
        if any(k in lowered for k in ("прочитай", "покажи файл", "код из")):
            file_match = re.search(r"(?:файл|код)\s+([\w./-]+)", text)
            if file_match:
                path = file_match.group(1)
                content = github.get_file_content(owner, repo, path)
                if content:
                    # Truncate if too long
                    if len(content) > 2000:
                        content = content[:2000] + "\n... (truncated)"
                    return PluginResult(success=True, response=f"```{path}```\n```\n{content}\n```")
                return PluginResult(success=True, response=f"Файл {path} не найден")
        
        # Search code
        if "найди" in lowered:
            query = text.split("найди")[-1].strip()
            results = github.search_code(f"repo:{owner}/{repo} {query}")
            if results:
                response = "Найдено:\n"
                for item in results[:5]:
                    response += f"- {item.get('path', 'unknown')}\n"
                return PluginResult(success=True, response=response)
            return PluginResult(success=True, response="Ничего не найдено")
        
        # Get repo info
        repo_data = github.get_repo(owner, repo)
        if repo_data:
            response = (
                f"📁 {repo_data.get('full_name')}\n"
                f"⭐ Stars: {repo_data.get('stargazers_count')}\n"
                f"🍴 Forks: {repo_data.get('forks_count')}\n"
                f"📝 {repo_data.get('description', 'No description')}\n"
                f"🔗 {repo_data.get('html_url')}"
            )
            return PluginResult(success=True, response=response)
        
        return PluginResult(success=False)
    
    def get_help(self) -> str:
        return "GitHub: 'покажи код из owner/repo файл.py', 'найди в github функция'"
