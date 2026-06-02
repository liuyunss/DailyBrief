"""去重过滤器"""

from difflib import SequenceMatcher


def deduplicate_by_url(items):
    """按 URL 去重，保留 score 更高的"""
    seen = {}
    for item in items:
        url = item.get("url", "")
        if url in seen:
            existing = seen[url]
            if (item.get("score") or 0) > (existing.get("score") or 0):
                seen[url] = item
        else:
            seen[url] = item
    return list(seen.values())


def deduplicate(items, threshold=0.85):
    """
    按标题相似度去重，保留 score 更高的
    
    Args:
        items: 条目列表
        threshold: 相似度阈值（中文建议 0.85+）
        
    Returns:
        list: 去重后的列表
    """
    if not items:
        return []
    
    unique = [items[0]]
    
    for item in items[1:]:
        is_duplicate = False
        
        for existing in unique:
            similarity = SequenceMatcher(
                None, 
                item["title"].lower(), 
                existing["title"].lower()
            ).ratio()
            
            if similarity > threshold:
                is_duplicate = True
                # 保留分数更高的
                if (item.get("score") or 0) > (existing.get("score") or 0):
                    unique.remove(existing)
                    unique.append(item)
                break
        
        if not is_duplicate:
            unique.append(item)
    
    return unique
