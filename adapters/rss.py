"""RSS 适配器"""

import logging
import feedparser
import requests
from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class RSSAdapter(BaseAdapter):
    """RSS/Atom 订阅适配器"""
    
    def fetch(self, config):
        url = config.get("url")
        max_items = config.get("max_items", 10)
        
        if not url:
            logger.warning("RSS 适配器: 未配置 URL")
            return []
        
        try:
            headers = {"User-Agent": "DailyBrief/1.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            
            feed = feedparser.parse(resp.text)
            
            items = []
            for entry in feed.entries[:max_items]:
                items.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "source": feed.feed.get("title", "RSS"),
                    "score": 0,
                    "description": entry.get("summary", "")[:200],
                })
            
            return self.standardize_all(items)
        except Exception as e:
            logger.error(f"RSS 抓取失败 ({url}): {e}")
            return []
