# 股票新闻情感分析可视化系统设计文档

## 1. 项目概述

本项目是一个基于 FastAPI 和 Vue.js 的全栈网站，支持电脑和手机浏览器自适应。主要功能是分析近七天的个股新闻情感，并以现代化的可视化方式呈现。

### 1.1 核心功能

- 支持通过股票名称搜索，自动转换为股票代码
- 分析并展示近 7 天的新闻情感数据
- 预留付费用户 30 天数据分析功能
- 响应式设计，支持多端访问

## 2. 技术栈选择

### 2.1 前端技术栈

- Vue 3 (Options API)
- Element Plus (UI 框架)
- ECharts (数据可视化)
- Vuex (状态管理)
- Axios (HTTP 客户端)

### 2.2 后端技术栈

- FastAPI
- 新闻爬虫
- LLM 情感分析
- APScheduler (可选，用于定时爬取)

## 3. 系统架构

### 3.1 目录结构

```
project/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchBar.vue
│   │   │   ├── SentimentDashboard.vue
│   │   │   ├── TrendChart.vue
│   │   │   └── NewsList.vue
│   │   ├── views/
│   │   │   ├── Home.vue
│   │   │   └── Analysis.vue
│   │   ├── api/
│   │   │   ├── stock.js
│   │   │   └── news.js
│   │   ├── store/
│   │   │   └── index.js
│   │   └── styles/
│   │       └── theme.css
│   └── public/
├── backend/
│   ├── api/
│   │   └── routes.py      # API路由
│   ├── core/
│   │   ├── crawler.py     # 新闻爬虫
│   │   └── analyzer.py    # 情感分析
│   ├── services/
│   │   └── stock.py       # 股票服务
│   └── utils/
└── docs/
```

## 4. 界面设计

### 4.1 视觉主题

- 主色调：深空蓝 (#1a1f3c)
- 强调色：霓虹蓝 (#00f0ff)
- 辅助色：科技紫 (#7b42ff)
- 背景：深色渐变 + 毛玻璃效果
- 卡片背景：rgba(255, 255, 255, 0.1) + 高斯模糊

### 4.2 页面布局

```
┌────────────────────────────────┐
│        搜索栏（毛玻璃效果）      │
├────────────────────────────────┤
│     整体情感分析仪表盘面板       │
│  (霓虹边框 + 半透明背景 + 模糊)  │
├──────────────┬─────────────────┤
│   走势图面板  │    数据统计      │
│              │                 │
├──────────────┴─────────────────┤
│        新闻列表（分页展示）      │
└────────────────────────────────┘
```

## 5. 功能模块设计

### 5.1 新闻爬虫模块

```python
class NewsCrawler:
    async def fetch_news(self, stock_code: str, days: int = 7) -> List[dict]:
        """
        爬取指定股票的新闻
        返回格式：
        [
            {
                "title": str,
                "summary": str,
                "content": str,
                "publish_date": datetime,
                "source": str
            },
            ...
        ]
        """
        pass

```

### 5.2 情感分析模块

```python
class SentimentAnalyzer:
    async def analyze(self, news_list: List[dict]) -> List[dict]:
        """
        分析新闻情感
        返回格式：
        [
            {
                "news": {...},  # 原新闻数据
                "sentiment": {
                    "score": float,  # 0-1之间
                    "label": str     # positive/negative/neutral
                }
            },
            ...
        ]
        """
        pass
```

### 5.3 数据流转过程

1. 用户输入股票名称
2. 后端转换为股票代码
3. 爬虫获取新闻数据
4. LLM 进行情感分析
5. 返回分析结果
6. 前端展示数据

## 6. API 接口设计

### 6.1 前端 API

```javascript
// 股票搜索
GET /api/stocks/search?query=${query}

// 获取股票新闻及情感分析
GET /api/stock-analysis/${stockCode}?days=${days}
```

### 6.2 后端 API

```python
@app.get("/api/stocks/search")
async def search_stocks(query: str):
    """搜索股票，返回股票代码和名称"""
    return [{"code": "000001", "name": "平安银行"}, ...]

@app.get("/api/stock-analysis/{stock_code}")
async def get_stock_analysis(stock_code: str, days: int = 7):
    """获取股票新闻分析结果"""
    # 1. 爬取新闻
    news_list = await crawler.fetch_news(stock_code, days)
    # 2. 情感分析
    analysis_results = await analyzer.analyze(news_list)
    # 3. 返回结果
    return {
        "stock_info": {"code": stock_code, "name": "xxx"},
        "analysis": analysis_results
    }
```

## 7. 扩展性考虑

### 7.1 未来可能的数据持久化方案

- 添加 SQLite 数据库存储历史数据
- 使用 Redis 缓存热门查询结果
- 实现定时爬虫任务

### 7.2 性能优化

- 实现请求缓存
- 并行处理新闻爬取
- 批量情感分析

### 7.3 功能扩展

- 非交易日新闻处理
- 实时数据更新
- 自定义时间范围
- 多维度分析

## 8. 开发计划

### 8.1 第一阶段：基础功能

- 搭建前后端框架
- 实现新闻爬虫
- 实现情感分析
- 完成基础 UI 组件

### 8.2 第二阶段：功能完善

- 优化视觉效果
- 添加交互动画
- 完善错误处理
- 优化性能

### 8.3 第三阶段：系统优化（可选）

- 添加数据持久化
- 优化查询性能
- 完善日志系统
- 添加监控指标
