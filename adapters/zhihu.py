"""知乎热榜适配器"""

import logging
import requests
from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class ZhihuAdapter(BaseAdapter):
    """知乎热榜适配器"""
    
    def fetch(self, config):
        limit = config.get("limit", 20)
        
        # 知乎热榜 API（无需认证）
        url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.zhihu.com/hot"
        }
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            items = []
            for item in data.get("data", [])[:limit]:
                target = item.get("target", {})
                title = target.get("title", "")
                excerpt = target.get("excerpt", "")
                url = f"https://www.zhihu.com/question/{target.get('id', '')}"
                heat = item.get("detail_text", "0 热度")
                
                # 提取数字
                try:
                    score = int("".join(filter(str.isdigit, heat.split()[0])))
                except:
                    score = 0
                
                items.append({
                    "title": title,
                    "url": url,
                    "source": "知乎热榜",
                    "score": score,
                    "description": excerpt,
                })
            
            return self.standardize_all(items)
        except Exception as e:
            logger.error(f"知乎热榜抓取失败: {e}")
            return []
