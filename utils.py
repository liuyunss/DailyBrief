"""共享工具函数"""

import re


def clean_html(text):
    """清理 HTML 标签"""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def group_by_source(items):
    """按源分组"""
    groups = {}
    for item in items:
        source = item.get("source", "其他")
        if source not in groups:
            groups[source] = []
        groups[source].append(item)
    return groups


def find_source_config(source_name, sources):
    """从源配置列表中查找匹配的配置"""
    for src in sources:
        if src.get("name") == source_name:
            return src
        # 模糊匹配：源名称包含配置名
        if src.get("name", "").lower() in source_name.lower():
            return src
    return None
