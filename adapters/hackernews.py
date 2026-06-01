"""Hacker News 适配器 - 使用 Algolia API 获取每周精选"""

import logging
import requests
from datetime import datetime, timedelta
from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class HackerNewsAdapter(BaseAdapter):
    """Hacker News Algolia 适配器 - 按 points 排序获取每周精选"""

    def fetch(self, config):
        limit = config.get("limit", 10)

        # 计算7天前的 Unix 时间戳
        week_ago = datetime.now() - timedelta(days=7)
        week_ago_unix = int(week_ago.timestamp())

        url = "https://hn.algolia.com/api/v1/search"
        params = {
            "tags": "story",
            "numericFilters": f"created_at_i>{week_ago_unix}",
            "hitsPerPage": 30,
            "query": "",
        }

        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            # Algolia 默认按 relevance，我们手动按 points 降序排序
            hits = data.get("hits", [])
            hits.sort(key=lambda h: h.get("points", 0), reverse=True)

            items = []
            for hit in hits[:limit]:
                items.append({
                    "title": hit.get("title", ""),
                    "url": hit.get("url", f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"),
                    "source": "Hacker News",
                    "score": hit.get("points", 0),
                    "description": hit.get("description", "") or hit.get("story_text", "") or "",
                    "metric_label": "points",
                })

            return items

        except Exception as e:
            logger.error(f"Hacker News Algolia 请求失败: {e}")
            return []
