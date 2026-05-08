"""ArXiv 适配器"""

import logging
import requests
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
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.text)
            
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            items = []
            
            for entry in root.findall("atom:entry", ns):
                title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
                summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")[:200]
                link = entry.find("atom:id", ns).text
                
                items.append({
                    "title": title,
                    "url": link,
                    "source": f"ArXiv {category}",
                    "score": 0,
                    "description": summary,
                })
            
            return self.standardize_all(items)
        except Exception as e:
            logger.error(f"ArXiv 抓取失败: {e}")
            return []
