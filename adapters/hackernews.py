"""Hacker News 适配器 - 需要二次请求获取详情"""

import logging
import requests
from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class HackerNewsAdapter(BaseAdapter):
    """Hacker News 热门适配器"""
    
    def fetch(self, config):
        limit = config.get("limit", 10)
        min_score = config.get("min_score", 100)
        
        # 获取热门故事 ID 列表
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            story_ids = resp.json()[:limit * 2]  # 多取一些，后面过滤
            
            items = []
            for story_id in story_ids[:limit]:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_resp = requests.get(story_url, timeout=5)
                story = story_resp.json()
                
                if story and story.get("score", 0) >= min_score:
                    items.append({
                        "title": story.get("title", ""),
                        "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                        "source": "Hacker News",
                        "score": story.get("score", 0),
                        "description": "",
                        "metric_label": "points",
                    })
            
            return items
            
        except Exception as e:
            logger.error(f"Hacker News 请求失败: {e}")
            return []
