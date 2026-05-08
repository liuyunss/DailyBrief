"""适配器基类"""

from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    """数据源适配器基类"""
    
    def standardize(self, item):
        """
        标准化单条数据，确保字段完整且类型正确
        
        Args:
            item: 原始数据字典
            
        Returns:
            dict: 标准化后的数据
        """
        return {
            "title": str(item.get("title") or "").strip(),
            "url": str(item.get("url") or "").strip(),
            "source": str(item.get("source") or "").strip(),
            "score": int(item.get("score") or 0),
            "description": str(item.get("description") or "").strip(),
        }
    
    def standardize_all(self, items):
        """批量标准化，过滤掉无效条目"""
        result = []
        for item in items:
            standardized = self.standardize(item)
            # 标题和 URL 不能为空
            if standardized["title"] and standardized["url"]:
                result.append(standardized)
        return result
    
    @abstractmethod
    def fetch(self, config):
        """
        抓取数据
        
        Args:
            config: 源配置
            
        Returns:
            list: 标准化的条目列表
        """
        pass
