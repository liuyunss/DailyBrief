"""RSS 适配器"""

import feedparser
import requests
from adapters.base import BaseAdapter


class RSSAdapter(BaseAdapter):
    """RSS/Atom 订阅适配器"""
    
    def fetch(self, config):
        items = []
        url = config.get("url")
        max_items = config.get("max_items", 10)
        
        if not url:
            return items
        
        try:
            # 使用 requests 获取内容，然后用 feedparser 解析
            headers = {"User-Agent": "DailyBrief/1.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            
            feed = feedparser.parse(resp.text)
            
            for entry in feed.entries[:max_items]:
                items.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "source": feed.feed.get("title", "RSS"),
                    "score": 0,
                    "description": entry.get("summary", "")[:200],
                })
        except Exception as e:
            print(f"RSS 抓取失败 ({url}): {e}")
        
        return items
