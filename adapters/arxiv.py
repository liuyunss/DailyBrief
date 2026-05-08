"""ArXiv 适配器 - XML 解析"""

import logging
import requests
import xml.etree.ElementTree as ET
from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class ArxivAdapter(BaseAdapter):
    """ArXiv 论文适配器"""
    
    def fetch(self, config):
        category = config.get("category", "cs.AI")
        limit = config.get("limit", 10)
        
        # ArXiv API（无需认证）
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"cat:{category}",
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": limit
        }
        
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            
            # 解析 XML
            root = ET.fromstring(resp.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            
            items = []
            for entry in root.findall("atom:entry", ns):
                title = entry.find("atom:title", ns)
                link = entry.find("atom:link[@type='text/html']", ns)
                summary = entry.find("atom:summary", ns)
                
                if title is None or link is None:
                    continue
                
                title_text = title.text.strip().replace("\n", " ")
                link_url = link.get("href", "")
                summary_text = summary.text.strip().replace("\n", " ") if summary is not None else ""
                
                # 截取简介前 100 字
                if len(summary_text) > 100:
                    summary_text = summary_text[:100] + "..."
                
                items.append({
                    "title": title_text,
                    "url": link_url,
                    "source": f"ArXiv {category}",
                    "score": None,
                    "description": summary_text,
                    "metric_label": "",
                })
            
            return items
            
        except Exception as e:
            logger.error(f"ArXiv 请求失败: {e}")
            return []
