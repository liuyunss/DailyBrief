"""通用 JSON API 适配器 - 配置驱动，无需写代码"""

import re
import requests
from datetime import datetime, timedelta
from adapters.base import BaseAdapter


class GenericAPIAdapter(BaseAdapter):
    """通用 JSON API 适配器
    
    通过配置文件定义：
    - url: API 地址
    - path: JSON 路径（点号分隔）
    - fields: 字段映射
    - metric_label: 热度标签
    - url_prefix / url_suffix: URL 构造（当 URL 需要拼接时）
    """
    
    def fetch(self, config):
        """从 API 获取数据"""
        url = config["url"]
        method = config.get("method", "GET").upper()
        headers = config.get("headers", {})
        params = config.get("params", {})
        
        # 替换占位符：{today} -> YYYY-MM-DD, {yesterday} -> 昨天
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        def replace_placeholders(val):
            if isinstance(val, str):
                return val.replace("{today}", today).replace("{yesterday}", yesterday)
            return val
        
        url = replace_placeholders(url)
        params = {k: replace_placeholders(v) for k, v in params.items()}
        headers = {k: replace_placeholders(v) for k, v in headers.items()}
        
        # 发送请求
        if method == "GET":
            resp = requests.get(url, headers=headers, params=params, timeout=30)
        else:
            resp = requests.post(url, headers=headers, json=params, timeout=30)
        
        resp.raise_for_status()
        data = resp.json()
        
        # 获取列表路径
        path = config.get("path", "")
        items = self._get_nested(data, path) if path else data
        
        if not isinstance(items, list):
            raise ValueError(f"路径 '{path}' 返回的不是数组，而是 {type(items).__name__}")
        
        # 字段映射
        fields = config.get("fields", {})
        metric_label = config.get("metric_label", "")
        source_name = config.get("name", "未知")
        url_prefix = config.get("url_prefix", "")
        url_suffix = config.get("url_suffix", "")
        
        result = []
        for item in items:
            if not isinstance(item, dict):
                continue
            
            title = self._get_nested(item, fields.get("title", "title"))
            url_val = self._get_nested(item, fields.get("url", "url"))
            
            if not title or not url_val:
                continue
            
            # URL 构造：prefix + 值 + suffix
            url_val = f"{url_prefix}{url_val}{url_suffix}"
            
            # 补全相对 URL
            if url_val and not url_val.startswith("http"):
                base_url = url.rsplit("/", 1)[0]
                url_val = f"{base_url}/{url_val.lstrip('/')}"
            
            description = self._get_nested(item, fields.get("description", ""))
            score = self._get_nested(item, fields.get("score", ""))
            
            # 尝试转数字
            try:
                score = int(score) if score else None
            except (ValueError, TypeError):
                score = None
            
            result.append({
                "title": str(title),
                "url": str(url_val),
                "source": source_name,
                "score": score,
                "description": str(description) if description else "",
                "metric_label": metric_label,
            })
        
        return result
    
    def _get_nested(self, data, path):
        """获取嵌套字段值，支持点号路径
        
        例如: "data.list" -> data["list"]
              "stat.view" -> item["stat"]["view"]
        """
        if not path:
            return data
        
        keys = path.split(".")
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                idx = int(key)
                if 0 <= idx < len(current):
                    current = current[idx]
                else:
                    return None
            else:
                return None
        
        return current
