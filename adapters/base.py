"""适配器基类"""

from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    """数据源适配器基类"""
    
    @abstractmethod
    def fetch(self, config):
        """
        抓取数据
        
        Args:
            config: 源配置
            
        Returns:
            list: 条目列表，每个条目包含:
                - title: 标题
                - url: 链接
                - source: 来源
                - score: 分数（可选）
                - description: 描述（可选）
        """
        pass
