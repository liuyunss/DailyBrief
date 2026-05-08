"""B站热门适配器"""

import logging
import requests
from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class BilibiliAdapter(BaseAdapter):
    """B站热门视频适配器"""
    
    def fetch(self, config):
        limit = config.get("limit", 20)
        
        # B站热门视频 API（无需认证）
        url = "https://api.bilibili.com/x/web-interface/popular"
        params = {"ps": limit, "pn": 1}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.bilibili.com"
        }
        
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            items = []
            for item in data.get("data", {}).get("list", []):
                stat = item.get("stat", {})
                items.append({
                    "title": item.get("title", ""),
                    "url": f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                    "source": "B站热门",
                    "score": stat.get("view", 0),
                    "description": item.get("desc", "")[:100],
                })
            
            return self.standardize_all(items)
        except Exception as e:
            logger.error(f"B站热门抓取失败: {e}")
            return []
