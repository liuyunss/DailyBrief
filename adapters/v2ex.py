"""V2EX 适配器"""

import logging
import requests
from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class V2EXAdapter(BaseAdapter):
    """V2EX 热门适配器"""
    
    def fetch(self, config):
        limit = config.get("limit", 15)
        
        # V2EX 热门 API（无需认证）
        url = "https://www.v2ex.com/api/topics/hot.json"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            items = []
            for topic in data[:limit]:
                items.append({
                    "title": topic.get("title", ""),
                    "url": topic.get("url", ""),
                    "source": "V2EX",
                    "score": topic.get("replies", 0),
                    "description": topic.get("content", "")[:100],
                })
            
            return self.standardize_all(items)
        except Exception as e:
            logger.error(f"V2EX 抓取失败: {e}")
            return []
