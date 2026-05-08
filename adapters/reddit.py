"""Reddit 适配器"""

import logging
import requests
from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class RedditAdapter(BaseAdapter):
    """Reddit 适配器"""
    
    def fetch(self, config):
        subreddit = config.get("subreddit", "programming")
        sort = config.get("sort", "hot")
        limit = config.get("limit", 20)
        min_upvotes = config.get("min_upvotes", 100)
        
        url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
        params = {"limit": limit}
        headers = {"User-Agent": "DailyBrief/1.0"}
        
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            items = []
            for post in data.get("data", {}).get("children", []):
                post_data = post.get("data", {})
                ups = post_data.get("ups", 0)
                
                if ups >= min_upvotes:
                    items.append({
                        "title": post_data.get("title", ""),
                        "url": f"https://reddit.com{post_data.get('permalink', '')}",
                        "source": f"Reddit r/{subreddit}",
                        "score": ups,
                        "description": post_data.get("selftext", "")[:200],
                    })
            
            return self.standardize_all(items)
        except Exception as e:
            logger.error(f"Reddit 抓取失败: {e}")
            return []
