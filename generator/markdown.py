"""Markdown 报告生成器"""


def generate_markdown(items, date, config):
    """
    生成 Markdown 格式的报告
    
    Args:
        items: 条目列表
        date: 日期
        config: 输出配置
        
    Returns:
        str: Markdown 内容
    """
    max_items = config.get("max_items", 20)
    categories = config.get("categories", [])
    
    # 按分类分组
    categorized = {cat["name"]: [] for cat in categories}
    categorized["其他"] = []
    
    for item in items:
        placed = False
        for cat in categories:
            if _matches_category(item, cat.get("keywords", [])):
                categorized[cat["name"]].append(item)
                placed = True
                break
        
        if not placed:
            categorized["其他"].append(item)
    
    # 生成 Markdown
    lines = [
        f"# DailyBrief - {date}",
        "",
        f"> 自动更新于 {date}，共收录 {len(items)} 条内容",
        "",
    ]
    
    for cat_name, cat_items in categorized.items():
        if not cat_items:
            continue
        
        lines.append(f"## {cat_name}")
        lines.append("")
        
        for item in cat_items:
            title = item["title"]
            url = item["url"]
            source = item["source"]
            score = item.get("score", 0)
            
            # 格式：标题（链接）| 来源 | 分数
            score_str = f" ⭐{score}" if score else ""
            lines.append(f"- [{title}]({url}) `{source}`{score_str}")
        
        lines.append("")
    
    # 添加来源说明
    lines.extend([
        "---",
        "",
        f"*由 [DailyBrief](https://github.com/liuyunss/DailyBrief) 自动生成*",
    ])
    
    return "\n".join(lines)


def _matches_category(item, keywords):
    """检查条目是否匹配分类"""
    if not keywords:
        return False
    
    title = item.get("title", "") or ""
    description = item.get("description", "") or ""
    title = title.lower()
    description = description.lower()
    
    for keyword in keywords:
        if keyword.lower() in title or keyword.lower() in description:
            return True
    
    return False
