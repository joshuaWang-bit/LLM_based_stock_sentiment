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

- FastAPI (Web 框架)
- Poetry (依赖管理)
- google.genai (Gemini API 调用)
- akshare (股票数据获取)
- pathlib (跨平台路径处理)
- asyncio (异步处理)

### 2.3 缓存机制

- 新闻数据缓存：避免重复爬取
- 情感分析缓存：减少 API 调用
- 缓存有效期：1 天
- 缓存存储：本地文件系统

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
│   ├── utils/
│   │   ├── config.py      # 配置管理
│   │   └── gemini_utils.py # LLM工具
│   └── data/
│       ├── news_cache/    # 新闻缓存
│       └── sentiment_cache/ # 情感分析缓存
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

### 4.3 组件详细设计

#### 4.3.1 SearchBar.vue

```vue
<template>
  <div class="search-bar glass-effect">
    <el-input
      v-model="searchQuery"
      placeholder="输入股票名称或代码"
      :suffix-icon="Search"
    />
  </div>
</template>

<style>
.glass-effect {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}
</style>
```

#### 4.3.2 SentimentDashboard.vue

- 整体情感得分仪表盘
- 市场预期显示
- 多维度分析雷达图
- 风险等级指示器

#### 4.3.3 TrendChart.vue

- 情感走势折线图
- 关键事件标注点
- 时间轴可选择范围

#### 4.3.4 NewsList.vue

- 新闻列表卡片式展示
- 支持分页
- 每条新闻显示标题、来源、时间、情感倾向
- 点击展开显示详细内容

### 4.4 数据可视化设计

#### 4.4.1 情感得分仪表盘

```javascript
// ECharts仪表盘配置
{
  series: [
    {
      type: "gauge",
      startAngle: 180,
      endAngle: 0,
      min: -1,
      max: 1,
      splitNumber: 8,
      axisLine: {
        lineStyle: {
          width: 6,
          color: [
            [-0.5, "#ff4b55"], // 红色
            [0, "#ffeb3b"], // 黄色
            [1, "#4CAF50"], // 绿色
          ],
        },
      },
      pointer: {
        icon: "path://M12.8,0.7l12,40.1H0.7L12.8,0.7z",
        length: "12%",
        width: 20,
        offsetCenter: [0, "-60%"],
        itemStyle: {
          color: "auto",
        },
      },
      axisTick: {
        length: 12,
        lineStyle: {
          color: "auto",
          width: 2,
        },
      },
      splitLine: {
        length: 20,
        lineStyle: {
          color: "auto",
          width: 5,
        },
      },
      title: {
        offsetCenter: [0, "-20%"],
        fontSize: 20,
      },
      detail: {
        fontSize: 30,
        offsetCenter: [0, "0%"],
        valueAnimation: true,
        formatter: function (value) {
          return value.toFixed(2);
        },
        color: "auto",
      },
    },
  ];
}
```

#### 4.4.2 情感趋势图

```javascript
// ECharts折线图配置
{
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross'
    }
  },
  xAxis: {
    type: 'time',
    boundaryGap: false,
    axisLine: {
      lineStyle: {
        color: '#666'
      }
    }
  },
  yAxis: {
    type: 'value',
    min: -1,
    max: 1,
    splitLine: {
      lineStyle: {
        color: 'rgba(255,255,255,0.1)'
      }
    }
  },
  series: [{
    type: 'line',
    smooth: true,
    symbolSize: 8,
    itemStyle: {
      color: '#00f0ff'
    },
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(0,240,255,0.3)' },
        { offset: 1, color: 'rgba(0,240,255,0)' }
      ])
    }
  }]
}
```

#### 4.4.3 主题分析雷达图

```javascript
// ECharts雷达图配置
{
  radar: {
    indicator: [
      { name: '公司经营', max: 1 },
      { name: '财务表现', max: 1 },
      { name: '市场竞争', max: 1 },
      { name: '产品技术', max: 1 },
      { name: '行业政策', max: 1 },
      { name: '资本市场', max: 1 }
    ],
    splitArea: {
      areaStyle: {
        color: ['rgba(255,255,255,0.05)']
      }
    },
    axisLine: {
      lineStyle: {
        color: 'rgba(255,255,255,0.2)'
      }
    }
  },
  series: [{
    type: 'radar',
    lineStyle: {
      color: '#7b42ff'
    },
    areaStyle: {
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(123,66,255,0.3)' },
        { offset: 1, color: 'rgba(123,66,255,0)' }
      ])
    }
  }]
}
```

### 4.5 交互设计

#### 4.5.1 搜索交互

- 输入防抖（300ms）
- 搜索建议实时显示
- 支持键盘上下键选择

#### 4.5.2 图表交互

- 鼠标悬停显示详细数据
- 支持时间范围选择
- 关键事件点击展示详情
- 雷达图维度点击筛选

#### 4.5.3 新闻列表交互

- 无限滚动加载
- 点击展开/收起动画
- 情感标签颜色区分
- 来源图标显示

#### 4.5.4 响应式适配

- 桌面端：多列布局
- 平板端：双列布局
- 移动端：单列布局
- 图表自适应容器大小

### 4.6 性能优化

#### 4.6.1 加载优化

- 骨架屏加载
- 图片懒加载
- 组件异步加载
- 数据分页加载

#### 4.6.2 渲染优化

- 虚拟列表
- 防抖节流
- 组件缓存
- 长列表性能优化

## 5. 功能模块设计

### 5.1 新闻爬虫模块

```python
class NewsCrawler:
    def __init__(self):
        self.cache_dir = Path(__file__).parent.parent.parent / 'data' / 'news_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def get_stock_news(
        self,
        stock_code: str,
        days: int = 7,
        max_news: int = 20
    ) -> List[Dict]:
        """
        获取股票新闻，优先从缓存加载

        Args:
            stock_code: 股票代码
            days: 获取天数
            max_news: 最大新闻数量

        Returns:
            List[Dict]: 新闻列表
            [
                {
                    "title": str,
                    "content": str,
                    "publish_time": str,  # YYYY-MM-DD HH:MM:SS
                    "source": str,
                    "url": str
                },
                ...
            ]
        """
```

### 5.2 情感分析模块

```python
class SentimentAnalyzer:
    def __init__(self):
        self.cache_dir = Path(__file__).parent.parent.parent / 'data' / 'sentiment_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.gemini_client = GeminiClient(
            api_key=Config.GEMINI_API_KEY,
            model=Config.GEMINI_MODEL
        )

    async def analyze_sentiment(
        self,
        news_list: List[Dict],
        max_news: int = 20
    ) -> Dict:
        """
        分析新闻情感，优先从缓存加载

        Args:
            news_list: 新闻列表
            max_news: 分析的最大新闻数量

        Returns:
            Dict: 多维度情感分析结果
            {
                "analysis_summary": {
                    "overall_score": float,  # -1到1
                    "sentiment_label": str,
                    "summary": str,
                    "market_expectation": str,
                    "analysis_period": {
                        "start_date": str,
                        "end_date": str
                    }
                },
                "time_analysis": {...},
                "topic_analysis": {...},
                "source_analysis": {...},
                "impact_analysis": {...},
                "risk_analysis": {...},
                "news_analysis": [...]
            }
        """
```

## 6. API 接口设计

### 6.1 股票分析接口

```python
@router.get("/api/stock-analysis/{stock_code}")
async def get_stock_analysis(
    stock_code: str,
    days: int = 7,
    max_news: int = 20,
    sentiment_news: int = 5
) -> Dict:
    """
    获取股票新闻情感分析结果

    Args:
        stock_code: 股票代码
        days: 分析天数，默认7天
        max_news: 爬取的最大新闻数量，默认20条
        sentiment_news: 进行情感分析的新闻数量，默认5条

    Returns:
        Dict: 详细的多维度分析结果
    """
```

### 6.2 返回数据结构

```python
{
    "stock_info": {
        "code": str,
        "name": str
    },
    "analysis_summary": {
        "overall_score": float,  # -1到1之间
        "sentiment_label": str,  # 情感标签
        "summary": str,         # 整体分析总结
        "market_expectation": str,  # 市场预期
        "analysis_period": {
            "start_date": str,  # YYYY-MM-DD
            "end_date": str     # YYYY-MM-DD
        }
    },
    "time_analysis": {
        "trend": [
            {
                "date": str,    # YYYY-MM-DD
                "score": float,
                "key_events": [str]
            }
        ],
        "trend_prediction": str
    },
    "topic_analysis": {
        "company_operation": {
            "score": float,
            "summary": str,
            "key_points": [str]
        },
        "financial_performance": {...},
        "market_competition": {...},
        "product_technology": {...},
        "industry_policy": {...},
        "capital_market": {...}
    },
    "source_analysis": {
        "mainstream_media": {"score": float, "summary": str},
        "industry_media": {"score": float, "summary": str},
        "self_media": {"score": float, "summary": str},
        "official_announcement": {"score": float, "summary": str}
    },
    "impact_analysis": {
        "importance_level": str,  # 高/中/低
        "market_impact": {
            "score": float,      # 0-1
            "duration": str,
            "key_factors": [str]
        }
    },
    "risk_analysis": {
        "risk_level": str,      # 高/中/低
        "risk_factors": [
            {
                "factor": str,
                "description": str,
                "severity": str  # 高/中/低
            }
        ]
    },
    "news_analysis": [
        {
            "title": str,
            "content": str,
            "publish_time": str,  # YYYY-MM-DD HH:MM:SS
            "source": str,
            "url": str
        }
    ]
}
```

## 7. 错误处理

### 7.1 API 错误

- 400: 请求参数错误
- 404: 股票代码不存在
- 429: API 调用频率超限
- 500: 服务器内部错误
- 503: 第三方服务不可用

### 7.2 错误恢复机制

- 新闻爬取失败：返回缓存数据或空列表
- LLM API 调用失败：使用关键词分析作为备选方案
- 缓存读写失败：继续处理但不缓存结果

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
