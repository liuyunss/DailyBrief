"""Hacker News 适配器"""

import requests
from adapters.base import BaseAdapter


class HackerNewsAdapter(BaseAdapter):
    """Hacker News 热门适配器"""
    
    def fetch(self, config):
        items = []
        min_score = config.get("min_score", 100)
        top_n = config.get("top_n", 20)
        
        # 获取热门故事
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            story_ids = resp.json()[:top_n * 2]  # 多取一些，后面过滤
            
            for story_id in story_ids[:top_n]:
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
                    })
        except Exception as e:
            print(f"Hacker News 抓取失败: {e}")
        
        return items
