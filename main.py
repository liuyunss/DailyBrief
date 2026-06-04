"""DailyBrief - 每日技术精选"""

import os
import yaml
import logging
from datetime import datetime, timedelta
from pathlib import Path

from adapters.api import GenericAPIAdapter
from adapters.rss import RSSAdapter
from adapters.bilibili import BilibiliAdapter
from adapters.hackernews import HackerNewsAdapter
from adapters.arxiv import ArxivAdapter
from cache_manager import load_recent_urls, save_urls
from filters.dedup import deduplicate, deduplicate_by_url
from generator.markdown import generate_markdown
from utils import group_by_source, find_source_config, clean_html

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('dailybrief.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 适配器映射
ADAPTERS = {
    "api": GenericAPIAdapter,
    "rss": RSSAdapter,
    "bilibili": BilibiliAdapter,
    "hackernews": HackerNewsAdapter,
    "arxiv": ArxivAdapter,
}


def load_sources(sources_dir="sources"):
    """加载所有源配置"""
    sources = []
    sources_path = Path(sources_dir)
    
    if not sources_path.exists():
        logger.error(f"sources 目录不存在: {sources_dir}")
        return sources
    
    for yaml_file in sorted(sources_path.glob("*.yaml")):
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not config:
                logger.warning(f"跳过空文件: {yaml_file.name}")
                continue
            
            # 检查是否启用
            if not config.get("enabled", True):
                logger.info(f"跳过已禁用的源: {yaml_file.name}")
                continue
            
            # 检查类型
            source_type = config.get("type")
            if source_type not in ADAPTERS:
                logger.error(f"无效类型 '{source_type}'，文件: {yaml_file.name}，有效值: {list(ADAPTERS.keys())}")
                continue
            
            sources.append(config)
            logger.info(f"已加载源: {config.get('name', yaml_file.name)}")
            
        except Exception as e:
            logger.error(f"加载 {yaml_file.name} 失败: {e}")
    
    return sources


def fetch_all(sources):
    """从所有源获取数据"""
    all_items = []
    
    for source in sources:
        source_type = source["type"]
        adapter_class = ADAPTERS[source_type]
        adapter = adapter_class()
        
        logger.info(f"抓取: {source.get('name', source_type)}")
        try:
            items = adapter.fetch(source)
            logger.info(f"  → 获取 {len(items)} 条")
            all_items.extend(items)
        except Exception as e:
            logger.error(f"  {source.get('name', source_type)} 抓取失败: {e}")
            logger.info(f"  → 获取 0 条")
    
    logger.info(f"共获取 {len(all_items)} 条内容")
    return all_items


def load_config(config_path="config.yaml"):
    """加载全局配置"""
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def main():
    """主入口"""
    logger.info("=" * 50)
    logger.info("DailyBrief 开始运行")
    
    # 加载配置
    config = load_config()
    
    # 加载源
    sources = load_sources()
    if not sources:
        logger.error("没有可用的源，退出")
        return
    
    # 获取数据
    all_items = fetch_all(sources)
    
    # ========== 1. 关键词过滤 ==========
    exclude_keywords = config.get("filter", {}).get("exclude_keywords", [])
    if exclude_keywords:
        filtered = []
        for item in all_items:
            title = item.get("title", "").lower()
            if not any(kw.lower() in title for kw in exclude_keywords):
                filtered.append(item)
        all_items = filtered
        logger.info(f"关键词过滤后: {len(all_items)} 条")
    
    # ========== 2. 每源取前 N 条（按 score 排序）==========
    source_groups = group_by_source(all_items)
    limited_items = []
    for source, items in source_groups.items():
        items.sort(key=lambda x: x.get("score", 0) or 0, reverse=True)
        src_config = find_source_config(source, sources)
        limit = src_config.get("limit", 10) if src_config else 10
        limited_items.extend(items[:limit])
    logger.info(f"每源取前 {limit} 条后: {len(limited_items)} 条")
    
    # ========== 3. 跨天 URL 去重 ==========
    global_dedup_days = config.get("dedup_days", 7)
    deduplicated_items = []
    for source, items in group_by_source(limited_items).items():
        src_config = find_source_config(source, sources)
        dedup_days = src_config.get("dedup_days", global_dedup_days) if src_config else global_dedup_days
        
        recent_urls = load_recent_urls(days=dedup_days)
        before_count = len(items)
        items = [item for item in items if item["url"] not in recent_urls]
        logger.info(f"  {source}: 跨天去重 {before_count} → {len(items)} (天数: {dedup_days})")
        deduplicated_items.extend(items)
    
    all_items = deduplicated_items
    logger.info(f"跨天去重后: {len(all_items)} 条")
    
    # ========== 4. 同 URL 去重（保留 score 更高的）==========
    if config.get("url_dedup", False):
        before = len(all_items)
        all_items = deduplicate_by_url(all_items)
        logger.info(f"URL 去重: {before} → {len(all_items)}")
    
    # ========== 5. 标题相似度去重 ==========
    threshold = config.get("filter", {}).get("dedup_threshold", 0.85)
    all_items = deduplicate(all_items, threshold)
    logger.info(f"标题去重后: {len(all_items)} 条")
    
    # ========== 6. 生成报告 ==========
    today = datetime.now().strftime("%Y-%m-%d")
    report = generate_markdown(all_items, today, config.get("output", {}))
    
    # 保存到 daily/YYYY/MM/YYYY-MM-DD.md
    year, month, day = today.split("-")
    daily_dir = Path(f"daily/{year}/{month}")
    daily_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = daily_dir / f"{today}.md"
    report_path.write_text(report, encoding='utf-8')
    logger.info(f"报告已生成: {report_path}")
    
    # 保存 URL 缓存
    urls = [item["url"] for item in all_items]
    save_urls(today, urls)
    
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
