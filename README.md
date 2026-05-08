# DailyBrief

每日技术精选 — 发现有意思的内容，不用再逐个网站翻看。

## 这是什么

DailyBrief 每天自动从多个技术社区（GitHub、Hacker News、Reddit、RSS 等）抓取热门内容，经过筛选和去重后，生成一份简洁的技术日报。

**目标：** 让你每天花 5 分钟就能了解技术圈发生了什么。

## 每日报告

每天的报告会自动生成并发布在 [daily/](./daily/) 目录下，格式为 Markdown。

> 报告每日自动更新，由 GitHub Actions 生成。

## 项目结构

```
DailyBrief/
├── daily/                  # 每日报告（自动生成）
│   └── 2026/05/            # 按年月归档
├── sources/                # 数据源配置（用户改这个）
│   ├── github-trending.yaml
│   ├── hackernews.yaml
│   └── ...
├── adapters/               # 数据源适配器
│   ├── api.py             # 通用 JSON API 适配器（大部分源用这个）
│   ├── rss.py             # RSS 适配器
│   ├── bilibili.py        # B站（特殊处理）
│   ├── hackernews.py      # Hacker News（需要二次请求）
│   └── arxiv.py           # ArXiv（XML 解析）
├── filters/                # 过滤器
│   ├── dedup.py           # 去重
│   └── keyword.py         # 关键词过滤
├── generator/              # 报告生成器
│   └── markdown.py        # Markdown 输出
├── main.py                 # 入口
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行

```bash
python main.py
```

### 3. 查看结果

报告会生成在 `daily/YYYY/MM/YYYY-MM-DD.md` 目录下。

## 数据源配置

每个源一个 YAML 文件，放在 `sources/` 目录下。

### 通用 API 源配置模板

```yaml
# sources/template.yaml
name: 示例源
type: api
enabled: true

url: "https://api.example.com/hot"
method: GET

# JSON 路径：列表在返回数据中的位置
path: "data.items"

# 字段映射：支持点号嵌套
fields:
  title: "title"
  url: "url"
  description: "summary"
  score: "view_count"

# 热度标签
metric_label: "播放"

# 每源取多少条
limit: 10

# 去重天数
dedup_days: 3

# 分类信息（可选）
category:
  name: "技术文章"
  keywords: ["python", "tutorial"]
```

### 支持的源类型

| 类型 | 说明 | 认证 |
|------|------|------|
| `api` | 通用 JSON API（配置驱动） | 无需 |
| `rss` | RSS/Atom 订阅 | 无需 |
| `bilibili` | B站热门 | 无需 |
| `hackernews` | Hacker News | 无需 |
| `arxiv` | ArXiv 论文 | 无需 |

## 添加新源

### 方式一：通用 API 适配器（推荐）

大部分 JSON API 源只需要写配置文件，不用写代码：

1. 复制配置模板
2. 填写 URL、字段路径、热度标签
3. 运行 `python main.py` 测试
4. 提交 PR

### 方式二：自定义适配器

少数需要特殊处理的源（如 B站有签名逻辑），需要写适配器：

1. 在 `adapters/` 下创建新文件，继承 `BaseAdapter`
2. 实现 `fetch()` 方法
3. 在 `main.py` 的 `ADAPTERS` 字典中注册
4. 提交 PR

```python
from adapters.base import BaseAdapter

class MyAdapter(BaseAdapter):
    def fetch(self, config):
        # 你的抓取逻辑
        return [{"title": "...", "url": "...", "source": "my_source"}]
```

## 自动运行

项目通过 GitHub Actions 每天自动运行，生成报告并提交到 `daily/` 目录。

## 开源协议

MIT

<!-- REPORT_INDEX_START -->

## 最近报告

### 2026-05
- [2026-05-08](daily/2026/05/2026-05-08.md)

<!-- REPORT_INDEX_END -->
