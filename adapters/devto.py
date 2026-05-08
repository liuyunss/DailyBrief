"""Dev.to 适配器"""

import logging
import requests
from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class DevtoAdapter(BaseAdapter):
    """Dev.to 热门文章适配器"""
    
    def fetch(self, config):
        limit = config.get("limit", 20)
        
        # Dev.to API（无需认证）
        url = "https://dev.to/api/articles"
        params = {"per_page": limit, "top": 1}  # top=1 表示最近 1 天
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            items = []
            for article in data:
                items.append({
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "source": "Dev.to",
                    "score": article.get("public_reactions_count", 0),
                    "description": article.get("description", "")[:100],
                })
            
            return self.standardize_all(items)
        except Exception as e:
            logger.error(f"Dev.to 抓取失败: {e}")
            return []
