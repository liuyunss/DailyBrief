"""去重过滤器"""

from difflib import SequenceMatcher


def deduplicate(items, threshold=0.7):
    """
    去重：标题相似度 > threshold 视为重复
    
    Args:
        items: 条目列表
        threshold: 相似度阈值
        
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
                if item.get("score", 0) > existing.get("score", 0):
                    unique.remove(existing)
                    unique.append(item)
                break
        
        if not is_duplicate:
            unique.append(item)
    
    return unique
