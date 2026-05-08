#!/usr/bin/env python3
"""DailyBrief - 每日技术精选"""

import yaml
from pathlib import Path
from datetime import datetime

from adapters.github import GitHubAdapter
from adapters.hackernews import HackerNewsAdapter
from adapters.reddit import RedditAdapter
from adapters.rss import RSSAdapter
from filters.dedup import deduplicate
from filters.keyword import filter_by_keywords
from generator.markdown import generate_markdown


def load_config():
    """加载数据源配置"""
    config_path = Path(__file__).parent / "sources.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


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
    config = load_config()
    all_items = []
    
    # 抓取所有启用的源
    for source in config["sources"]:
        if not source.get("enabled", True):
            continue
        
        adapter = get_adapter(source["type"])
        if adapter:
            items = adapter.fetch(source["config"])
            all_items.extend(items)
    
    # 去重
    all_items = deduplicate(all_items, config["filter"]["dedup_threshold"])
    
    # 关键词过滤
    all_items = filter_by_keywords(all_items, config["filter"]["exclude_keywords"])
    
    # 生成报告
    today = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path(__file__).parent / "daily"
    output_dir.mkdir(exist_ok=True)
    
    report = generate_markdown(all_items, today, config["output"])
    output_path = output_dir / f"{today}.md"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"报告已生成: {output_path}")


if __name__ == "__main__":
    main()
