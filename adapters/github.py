"""GitHub 适配器"""

import requests
from adapters.base import BaseAdapter


class GitHubAdapter(BaseAdapter):
    """GitHub Trending 适配器"""
    
    def fetch(self, config):
        items = []
        language = config.get("language", "all")
        since = config.get("since", "daily")
        limit = config.get("limit", 20)
        
        # GitHub Trending 页面
        url = "https://api.github.com/search/repositories"
        params = {
            "q": f"created:>={self._get_date()}",
            "sort": "stars",
            "order": "desc",
            "per_page": limit,
        }
        
        if language != "all":
            params["q"] += f" language:{language}"
        
        headers = {"Accept": "application/vnd.github.v3+json"}
        
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            for repo in data.get("items", []):
                items.append({
                    "title": f"{repo['full_name']} - {repo.get('description', '')}",
                    "url": repo["html_url"],
                    "source": "GitHub",
                    "score": repo["stargazers_count"],
                    "description": repo.get("description", ""),
                })
        except Exception as e:
            print(f"GitHub 抓取失败: {e}")
        
        return items
    
    def _get_date(self):
        """获取日期"""
        from datetime import datetime, timedelta
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
