"""缓存管理 - 跨天去重"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)


def load_recent_urls(days=3):
    """
    加载最近 N 天的已抓取 URL
    
    Args:
        days: 保留最近几天的数据
        
    Returns:
        set: URL 集合
    """
    urls = set()
    today = datetime.now()
    
    for i in range(days):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        cache_file = CACHE_DIR / f"{date}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    urls.update(data.get("urls", []))
            except Exception as e:
                logger.warning(f"读取缓存失败: {cache_file}, {e}")
    
    return urls


def save_urls(date, urls):
    """
    保存当天的 URL 到缓存
    
    Args:
        date: 日期字符串 (YYYY-MM-DD)
        urls: URL 列表
    """
    cache_file = CACHE_DIR / f"{date}.json"
    
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({
                "date": date,
                "urls": list(urls),
                "count": len(urls)
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"缓存已保存: {cache_file}, {len(urls)} 条")
    except Exception as e:
        logger.error(f"保存缓存失败: {e}")
