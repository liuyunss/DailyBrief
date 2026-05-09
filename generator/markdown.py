"""Markdown 报告生成器"""

from datetime import datetime
from lunardate import LunarDate
from utils import clean_html


def generate_markdown(items, date_str, config):
    """
    生成 Markdown 格式的报告
    
    Args:
        items: 条目列表
        date_str: 日期字符串 YYYY-MM-DD
        config: 输出配置
        
    Returns:
        str: Markdown 内容
    """
    # 解析日期
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    
    # 星期
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday = weekdays[dt.weekday()]
    
    # ISO 周数
    week_num = dt.isocalendar()[1]
    
    # 阴历
    lunar = LunarDate.fromSolarDate(dt.year, dt.month, dt.day)
    lunar_months = ["正月", "二月", "三月", "四月", "五月", "六月",
                    "七月", "八月", "九月", "十月", "冬月", "腊月"]
    lunar_days = ["初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
                  "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
                  "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"]
    lunar_str = f"农历{lunar_months[lunar.month - 1]}{lunar_days[lunar.day - 1]}"
    
    # 按分类分组
    categories = config.get("categories", [])
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
        f"# DailyBrief - {date_str}",
        "",
        f"> {lunar_str} {weekday} 第{week_num}周",
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
            score = item.get("score")
            metric_label = item.get("metric_label", "")
            description = item.get("description", "")
            
            # 格式：标题（链接）
            score_str = f" · {metric_label} {_format_number(score)}" if score and metric_label else ""
            lines.append(f"- [{title}]({url}) `{source}`{score_str}")
            
            # 简介用引用框展示
            if description:
                desc = clean_html(description)
                if len(desc) > 100:
                    desc = desc[:100] + "..."
                lines.append(f"> {desc}")
        
        lines.append("")
    
    # 添加来源说明
    lines.extend([
        "---",
        "",
        f"*由 [DailyBrief](https://github.com/liuyunss/DailyBrief) 自动生成*",
    ])
    
    return "\n".join(lines)


def _format_number(num):
    """数字格式化：亿 > 万 > 千 > 百"""
    if num is None:
        return ""
    
    try:
        num = int(num)
    except (ValueError, TypeError):
        return str(num)
    
    if num >= 100_000_000:
        return f"{num / 100_000_000:.1f}亿"
    elif num >= 10_000:
        return f"{num / 10_000:.1f}万"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}千"
    elif num >= 100:
        return f"{num}"
    else:
        return str(num)


def _matches_category(item, keywords):
    """检查条目是否匹配分类"""
    if not keywords:
        return False
    
    title = (item.get("title", "") or "").lower()
    description = (item.get("description", "") or "").lower()
    
    for keyword in keywords:
        if keyword.lower() in title or keyword.lower() in description:
            return True
    
    return False
