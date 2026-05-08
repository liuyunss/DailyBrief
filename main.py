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
from filters.dedup import deduplicate
from filters.keyword import filter_by_keywords
from generator.markdown import generate_markdown

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# 合法的源类型
VALID_TYPES = ["github", "github_new", "hackernews", "reddit", "rss"]


def load_config():
    """加载全局配置"""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_sources():
    """加载所有源配置"""
    sources_dir = Path(__file__).parent / "sources"
    sources = []
    
    for source_file in sorted(sources_dir.glob("*.yaml")):
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                source = yaml.safe_load(f)
                source["_file"] = source_file.name
                sources.append(source)
        except Exception as e:
            logger.error(f"加载源配置失败: {source_file.name} - {e}")
    
    return sources


def validate_source(source):
    """校验源配置"""
    source_type = source.get("type", "")
    source_name = source.get("name", "未命名")
    source_file = source.get("_file", "未知文件")
    
    if source_type not in VALID_TYPES:
        logger.error(f"源类型错误: {source_file} 的 type '{source_type}' 不合法")
        logger.error(f"可选值: {VALID_TYPES}")
        return False
    
    if not source.get("name"):
        logger.warning(f"源配置缺少 name: {source_file}")
    
    return True


def get_adapter(source_type):
    """根据类型获取适配器"""
    adapters = {
        "github": GitHubAdapter,
        "github_new": GitHubAdapter,
        "hackernews": HackerNewsAdapter,
        "reddit": RedditAdapter,
        "rss": RSSAdapter,
    }
    return adapters.get(source_type)()


def main():
    """主函数"""
    logger.info("DailyBrief 开始运行")
    
    # 加载配置
    config = load_config()
    sources = load_sources()
    
    # 校验所有源
    valid_sources = []
    for source in sources:
        if validate_source(source):
            valid_sources.append(source)
    
    logger.info(f"共加载 {len(valid_sources)} 个有效源")
    
    # 抓取所有启用的源
    all_items = []
    for source in valid_sources:
        if not source.get("enabled", True):
            logger.info(f"跳过禁用源: {source.get('name')}")
            continue
        
        adapter = get_adapter(source["type"])
        if adapter:
            logger.info(f"抓取: {source.get('name')}")
            items = adapter.fetch(source.get("config", {}))
            all_items.extend(items)
            logger.info(f"  -> 获取 {len(items)} 条")
    
    logger.info(f"共获取 {len(all_items)} 条内容")
    
    # 去重
    all_items = deduplicate(all_items, config["filter"]["dedup_threshold"])
    logger.info(f"去重后 {len(all_items)} 条")
    
    # 关键词过滤
    all_items = filter_by_keywords(all_items, config["filter"]["exclude_keywords"])
    logger.info(f"过滤后 {len(all_items)} 条")
    
    # 生成报告
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path(__file__).parent / "daily"
    output_dir.mkdir(exist_ok=True)
    
    report = generate_markdown(all_items, today, config["output"])
    output_path = output_dir / f"{today}.md"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info(f"报告已生成: {output_path}")
    logger.info("DailyBrief 运行完成")


if __name__ == "__main__":
    main()
