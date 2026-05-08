"""RSS 适配器 - 基于 feedparser"""

import feedparser
import requests
import re
from adapters.base import BaseAdapter


class RSSAdapter(BaseAdapter):
    """RSS/Atom 适配器
    
    通过配置文件定义：
    - url: RSS 源地址
    - fields: 字段映射
    - metric_label: 热度标签（可选）
    """
    
    def fetch(self, config):
        """从 RSS 源获取数据"""
        url = config["url"]
        source_name = config.get("name", "RSS")
        metric_label = config.get("metric_label", "")
        
        # 获取 RSS 内容
        headers = config.get("headers", {})
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        feed = feedparser.parse(resp.content)
        
        # 字段映射
        fields = config.get("fields", {})
        
        result = []
        for entry in feed.entries:
            title = getattr(entry, fields.get("title", "title"), None)
            link = getattr(entry, fields.get("url", "link"), None)
            
            if not title or not link:
                continue
            
            # 获取描述
            desc_field = fields.get("description", "summary")
            description = getattr(entry, desc_field, "")
            if description:
                description = self._clean_html(str(description))
            
            # 获取分数（RSS 通常没有）
            score_field = fields.get("score", "")
            score = getattr(entry, score_field, None) if score_field else None
            try:
                score = int(score) if score else None
            except (ValueError, TypeError):
                score = None
            
            result.append({
                "title": str(title).strip(),
                "url": str(link).strip(),
                "source": source_name,
                "score": score,
                "description": description,
                "metric_label": metric_label,
            })
        
        return result
    
    def _clean_html(self, text):
        """清理 HTML 标签"""
        if not text:
            return ""
        clean = re.sub(r'<[^>]+>', '', text)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean
