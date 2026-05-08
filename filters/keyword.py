"""关键词过滤器"""


def filter_by_keywords(items, exclude_keywords):
    """
    根据关键词过滤
    
    Args:
        items: 条目列表
        exclude_keywords: 排除关键词列表
        
    Returns:
        list: 过滤后的列表
    """
    if not exclude_keywords:
        return items
    
    filtered = []
    
    for item in items:
        title = item.get("title", "") or ""
        description = item.get("description", "") or ""
        title = title.lower()
        description = description.lower()
        
        # 检查是否包含排除关键词
        excluded = False
        for keyword in exclude_keywords:
            if keyword.lower() in title or keyword.lower() in description:
                excluded = True
                break
        
        if not excluded:
            filtered.append(item)
    
    return filtered
