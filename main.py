#!/usr/bin/env python3
"""DailyBrief - 每日技术精选"""

import sys
import yaml
import logging
from pathlib import Path
from datetime import datetime

from adapters.github import GitHubAdapter
from adapters.hackernews import HackerNewsAdapter
from adapters.reddit import RedditAdapter
from adapters.rss import RSSAdapter
from adapters.v2ex import V2EXAdapter
from adapters.zhihu import ZhihuAdapter
from adapters.bilibili import BilibiliAdapter
from adapters.juejin import JuejinAdapter
from adapters.devto import DevtoAdapter
from adapters.arxiv import ArxivAdapter

from filters.dedup import deduplicate
from filters.keyword import filter_by_keywords
from generator.markdown import generate_markdown

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("dailybrief.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 适配器映射
ADAPTERS = {
    "github": GitHubAdapter(),
    "github_new": GitHubAdapter(),
    "hackernews": HackerNewsAdapter(),
    "reddit": RedditAdapter(),
    "rss": RSSAdapter(),
    "v2ex": V2EXAdapter(),
    "zhihu": ZhihuAdapter(),
    "bilibili": BilibiliAdapter(),
    "juejin": JuejinAdapter(),
    "devto": DevtoAdapter(),
    "arxiv": ArxivAdapter(),
}

# 合法的源类型
VALID_TYPES = list(ADAPTERS.keys())


def load_config():
    """加载全局配置"""
    config_path = Path("config.yaml")
    if not config_path.exists():
        logger.error("config.yaml 不存在")
        sys.exit(1)
    
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_sources():
    """加载所有启用的源"""
    sources_dir = Path("sources")
    if not sources_dir.exists():
        logger.error("sources/ 目录不存在")
        sys.exit(1)
    
    sources = []
    for source_file in sorted(sources_dir.glob("*.yaml")):
        with open(source_file, "r", encoding="utf-8") as f:
            source = yaml.safe_load(f)
        
        # 检查类型
        source_type = source.get("type")
        if source_type not in VALID_TYPES:
            logger.error(f"{source_file.name} 的 type '{source_type}' 不合法")
            logger.error(f"可选值: {VALID_TYPES}")
            sys.exit(1)
        
        # 检查是否启用
        if not source.get("enabled", True):
            logger.info(f"跳过已禁用的源: {source.get('name', source_file.name)}")
            continue
        
        sources.append(source)
    
    return sources


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("DailyBrief 开始运行")
    
    # 加载配置
    config = load_config()
    sources = load_sources()
    logger.info(f"加载了 {len(sources)} 个源")
    
    # 收集所有内容
    all_items = []
    for source in sources:
        source_type = source["type"]
        adapter = ADAPTERS.get(source_type)
        
        if not adapter:
            logger.warning(f"未找到适配器: {source_type}")
            continue
        
        logger.info(f"抓取: {source.get('name', source_type)}")
        try:
            items = adapter.fetch(source.get("config", {}))
            all_items.extend(items)
            logger.info(f"  → 获取 {len(items)} 条")
        except Exception as e:
            logger.error(f"  → 抓取失败: {e}")
    
    logger.info(f"共获取 {len(all_items)} 条内容")
    
    # 关键词过滤
    exclude_keywords = config.get("filter", {}).get("exclude_keywords", [])
    if exclude_keywords:
        all_items = filter_by_keywords(all_items, exclude_keywords)
        logger.info(f"关键词过滤后: {len(all_items)} 条")
    
    # 去重
    threshold = config.get("filter", {}).get("dedup_threshold", 0.7)
    all_items = deduplicate(all_items, threshold)
    logger.info(f"去重后: {len(all_items)} 条")
    
    # 按源分组，每个源取固定数量（保证多样性）
    source_groups = {}
    for item in all_items:
        source = item.get("source", "其他")
        if source not in source_groups:
            source_groups[source] = []
        source_groups[source].append(item)
    
    # 每个源取前 N 条
    max_items = config.get("output", {}).get("max_items", 20)
    per_source = max(2, max_items // len(source_groups)) if source_groups else max_items
    
    balanced_items = []
    for source, items in source_groups.items():
        items.sort(key=lambda x: x.get("score", 0), reverse=True)
        balanced_items.extend(items[:per_source])
    
    # 最终排序
    balanced_items.sort(key=lambda x: x.get("score", 0), reverse=True)
    all_items = balanced_items[:max_items]
    
    # 生成报告
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path("daily")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{today}.md"
    
    markdown = generate_markdown(all_items, today, config.get("output", {}))
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown)
    
    logger.info(f"报告已生成: {output_file}")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
