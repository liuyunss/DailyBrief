"""掘金适配器"""

import logging
import requests
from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class JuejinAdapter(BaseAdapter):
    """掘金热门文章适配器"""
    
    def fetch(self, config):
        limit = config.get("limit", 20)
        
        # 掘金推荐文章 API（无需认证）
        url = "https://api.juejin.cn/recommend_api/v1/article/recommend_all_feed"
        payload = {
            "id_type": 2,
            "sort_type": 200,
            "cursor": "0",
            "limit": limit
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
        
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            items = []
            for item in data.get("data", []):
                article_info = item.get("item_info", {}).get("article_info", {})
                items.append({
                    "title": article_info.get("title", ""),
                    "url": f"https://juejin.cn/post/{article_info.get('article_id', '')}",
                    "source": "掘金",
                    "score": article_info.get("digg_count", 0),
                    "description": article_info.get("brief_content", "")[:100],
                })
            
            return self.standardize_all(items)
        except Exception as e:
            logger.error(f"掘金抓取失败: {e}")
            return []
