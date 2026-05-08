# DailyBrief

每日技术精选 — 发现有意思的内容，不用再逐个网站翻看。

## 这是什么

DailyBrief 每天自动从多个技术社区（GitHub、Hacker News、Reddit、RSS 等）抓取热门内容，经过筛选和去重后，生成一份简洁的技术日报。

**目标：** 让你每天花 5 分钟就能了解技术圈发生了什么。

## 每日报告

每天的报告会自动生成并发布在 [daily/](./daily/) 目录下，格式为 Markdown。

| 日期 | 报告 |
|------|------|
| 2026-05-08 | [查看](./daily/2026-05-08.md) |

> 报告每日自动更新，由 GitHub Actions 生成。

## 项目结构

```
DailyBrief/
├── daily/                  # 每日报告（自动生成）
│   └── 2026-05-08.md
├── sources.yaml            # 数据源配置（用户改这个）
├── adapters/               # 数据源适配器
│   ├── base.py            # 基类
│   ├── github.py          # GitHub Trending
│   ├── hackernews.py      # Hacker News
│   ├── reddit.py          # Reddit
│   └── rss.py             # RSS 订阅
├── filters/                # 过滤器
│   ├── dedup.py           # 去重
│   └── keyword.py         # 关键词过滤
├── generator/              # 报告生成器
│   └── markdown.py        # Markdown 输出
├── main.py                 # 入口
└── README.md
```

## 快速开始

### 1. 配置数据源

编辑 `sources.yaml`，添加或修改你想要的数据源：

```yaml
sources:
  - name: GitHub Trending
    type: github
    enabled: true
    config:
      language: all
      since: daily
      limit: 20
```

### 2. 运行

```bash
pip install -r requirements.txt
python main.py
```

### 3. 查看结果

报告会生成在 `daily/` 目录下，文件名格式为 `YYYY-MM-DD.md`。

## 支持的数据源

| 类型 | 说明 | 认证 |
|------|------|------|
| `github` | GitHub Trending | 无需 |
| `github_new` | GitHub 新项目 | 无需（可选 Token 提升限额） |
| `hackernews` | Hacker News 热门 | 无需 |
| `reddit` | Reddit 子版块 | 无需 |
| `rss` | RSS/Atom 订阅 | 无需 |

## 添加新数据源

1. 在 `adapters/` 下创建新文件，继承 `BaseAdapter`
2. 实现 `fetch()` 方法
3. 在 `sources.yaml` 中添加配置
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
