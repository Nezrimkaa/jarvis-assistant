"""GitHub Integration for J.A.R.V.I.S.

Provides full GitHub API access for repository management,
code reading, commits, PRs, and issues.
"""
import os
import base64
from typing import Dict, List, Optional, Tuple
import requests

from config import Config


class GitHubClient:
    """GitHub API client with full repository access.
    
    Features:
    - Read repositories and files
    - Search code across repos
    - Create/edit files and commits
    - Manage PRs and issues
    """
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """Initialize with GitHub token.
        
        Args:
            token: GitHub Personal Access Token
        """
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        } if self.token else {}
    
    def is_authenticated(self) -> bool:
        """Check if token is valid."""
        if not self.token:
            return False
        try:
            resp = requests.get(f"{self.BASE_URL}/user", headers=self.headers)
            return resp.status_code == 200
        except:
            return False
    
    def get_user(self) -> Optional[Dict]:
        """Get authenticated user info."""
        try:
            resp = requests.get(f"{self.BASE_URL}/user", headers=self.headers)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"[GitHub] Error: {e}")
        return None
    
    def get_repo(self, owner: str, repo: str) -> Optional[Dict]:
        """Get repository info.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository data or None
        """
        try:
            resp = requests.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}",
                headers=self.headers
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"[GitHub] Error: {e}")
        return None
    
    def get_file_content(self, owner: str, repo: str, path: str, ref: str = "main") -> Optional[str]:
        """Get file content from repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            ref: Branch or commit SHA
            
        Returns:
            File content or None
        """
        try:
            resp = requests.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}?ref={ref}",
                headers=self.headers
            )
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict) and "content" in data:
                    content = base64.b64decode(data["content"]).decode('utf-8')
                    return content
        except Exception as e:
            print(f"[GitHub] Error reading file: {e}")
        return None
    
    def search_code(self, query: str, language: Optional[str] = None) -> List[Dict]:
        """Search code on GitHub.
        
        Args:
            query: Search query
            language: Optional language filter
            
        Returns:
            List of search results
        """
        try:
            q = query
            if language:
                q += f" language:{language}"
            
            resp = requests.get(
                f"{self.BASE_URL}/search/code",
                headers=self.headers,
                params={"q": q, "per_page": 5}
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("items", [])
        except Exception as e:
            print(f"[GitHub] Search error: {e}")
        return []
    
    def create_file(self, owner: str, repo: str, path: str, content: str, message: str, branch: str = "main") -> bool:
        """Create or update file in repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            content: File content
            message: Commit message
            branch: Target branch
            
        Returns:
            True if successful
        """
        try:
            # Check if file exists
            get_resp = requests.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}?ref={branch}",
                headers=self.headers
            )
            
            sha = None
            if get_resp.status_code == 200:
                sha = get_resp.json().get("sha")
            
            # Create/update file
            data = {
                "message": message,
                "content": base64.b64encode(content.encode()).decode(),
                "branch": branch,
            }
            if sha:
                data["sha"] = sha
            
            resp = requests.put(
                f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}",
                headers=self.headers,
                json=data
            )
            return resp.status_code in [200, 201]
        except Exception as e:
            print(f"[GitHub] Error creating file: {e}")
        return False
    
    def get_issues(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        """Get repository issues.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open/closed/all)
            
        Returns:
            List of issues
        """
        try:
            resp = requests.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/issues",
                headers=self.headers,
                params={"state": state, "per_page": 10}
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"[GitHub] Error: {e}")
        return []
    
    def create_issue(self, owner: str, repo: str, title: str, body: str = "") -> Optional[Dict]:
        """Create issue in repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            title: Issue title
            body: Issue body
            
        Returns:
            Created issue or None
        """
        try:
            resp = requests.post(
                f"{self.BASE_URL}/repos/{owner}/{repo}/issues",
                headers=self.headers,
                json={"title": title, "body": body}
            )
            if resp.status_code == 201:
                return resp.json()
        except Exception as e:
            print(f"[GitHub] Error: {e}")
        return None
