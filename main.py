"""DailyBrief - 每日技术精选"""

import os
import sys
import yaml
import logging
from datetime import datetime
from pathlib import Path

from adapters.base import BaseAdapter
from adapters.api import GenericAPIAdapter
from adapters.rss import RSSAdapter
from adapters.bilibili import BilibiliAdapter
from adapters.hackernews import HackerNewsAdapter
from adapters.arxiv import ArxivAdapter
from cache_manager import load_recent_urls, save_urls
from filters.dedup import deduplicate
from generator.markdown import generate_markdown

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

VALID_TYPES = list(ADAPTERS.keys())


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
            if source_type not in VALID_TYPES:
                logger.error(f"无效类型 '{source_type}'，文件: {yaml_file.name}，有效值: {VALID_TYPES}")
                sys.exit(1)
            
            sources.append(config)
            logger.info(f"已加载源: {config.get('name', yaml_file.name)}")
            
        except Exception as e:
            logger.error(f"加载 {yaml_file.name} 失败: {e}")
            sys.exit(1)
    
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


def update_readme(daily_dir="daily"):
    """更新 README 报告索引"""
    readme_path = Path("README.md")
    
    # 读取现有 README
    existing_content = ""
    if readme_path.exists():
        existing_content = readme_path.read_text(encoding='utf-8')
    
    # 找到索引分隔标记
    marker = "<!-- REPORT_INDEX_START -->"
    end_marker = "<!-- REPORT_INDEX_END -->"
    
    # 扫描所有报告文件
    daily_path = Path(daily_dir)
    reports = []
    
    if daily_path.exists():
        for md_file in sorted(daily_path.rglob("*.md"), reverse=True):
            # 从路径提取日期
            parts = md_file.parts
            if len(parts) >= 4:  # daily/YYYY/MM/YYYY-MM-DD.md
                date_str = md_file.stem  # YYYY-MM-DD
                rel_path = str(md_file)
                reports.append((date_str, rel_path))
    
    # 按月份分组
    monthly = {}
    for date_str, rel_path in reports:
        month_key = date_str[:7]  # YYYY-MM
        if month_key not in monthly:
            monthly[month_key] = []
        monthly[month_key].append((date_str, rel_path))
    
    # 生成索引内容
    index_lines = [marker, "", "## 最近报告", ""]
    
    for month_key in sorted(monthly.keys(), reverse=True):
        year, month = month_key.split("-")
        index_lines.append(f"### {year}-{month}")
        
        for date_str, rel_path in sorted(monthly[month_key], reverse=True):
            index_lines.append(f"- [{date_str}]({rel_path})")
        
        index_lines.append("")
    
    index_lines.append(end_marker)
    index_content = "\n".join(index_lines)
    
    # 替换或追加索引
    if marker in existing_content and end_marker in existing_content:
        # 替换现有索引
        start = existing_content.index(marker)
        end = existing_content.index(end_marker) + len(end_marker)
        new_content = existing_content[:start] + index_content + existing_content[end:]
    else:
        # 追加索引
        new_content = existing_content.rstrip() + "\n\n" + index_content + "\n"
    
    readme_path.write_text(new_content, encoding='utf-8')
    logger.info("README 已更新")


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
    
    # 跨天去重（每个源可能有不同的 dedup_days）
    # 先获取全局默认值
    global_dedup_days = config.get("dedup_days", 3)
    
    # 按源分组，分别去重
    source_groups = {}
    for item in all_items:
        source = item.get("source", "其他")
        if source not in source_groups:
            source_groups[source] = []
        source_groups[source].append(item)
    
    deduplicated_items = []
    for source, items in source_groups.items():
        # 从源配置中读取 dedup_days
        dedup_days = global_dedup_days
        for src in sources:
            if src.get("name") == source or src.get("name", "").lower() in source.lower():
                dedup_days = src.get("dedup_days", global_dedup_days)
                break
        
        recent_urls = load_recent_urls(days=dedup_days)
        before_count = len(items)
        items = [item for item in items if item["url"] not in recent_urls]
        logger.info(f"  {source}: 去重 {before_count} → {len(items)} (去重天数: {dedup_days})")
        deduplicated_items.extend(items)
    
    all_items = deduplicated_items
    logger.info(f"跨天去重后: {len(all_items)} 条")
    
    # 关键词过滤
    exclude_keywords = config.get("filter", {}).get("exclude_keywords", [])
    if exclude_keywords:
        filtered = []
        for item in all_items:
            title = item.get("title", "").lower()
            if not any(kw.lower() in title for kw in exclude_keywords):
                filtered.append(item)
        all_items = filtered
        logger.info(f"关键词过滤后: {len(all_items)} 条")
    
    # 标题去重
    threshold = config.get("filter", {}).get("dedup_threshold", 0.7)
    all_items = deduplicate(all_items, threshold)
    logger.info(f"去重后: {len(all_items)} 条")
    
    # 每源取前 N 条
    source_groups = {}
    for item in all_items:
        source = item.get("source", "其他")
        if source not in source_groups:
            source_groups[source] = []
        source_groups[source].append(item)
    
    all_items = []
    for source, items in source_groups.items():
        items.sort(key=lambda x: x.get("score", 0) or 0, reverse=True)
        limit = 10  # 默认 10 条
        # 从源配置中读取 limit
        for src in sources:
            if src.get("name") == source or src.get("type") == source.lower():
                limit = src.get("limit", 10)
                break
        all_items.extend(items[:limit])
    
    logger.info(f"最终 {len(all_items)} 条")
    
    # 生成报告
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
    
    # 更新 README
    update_readme()
    
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
