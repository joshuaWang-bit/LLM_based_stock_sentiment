# 股票新闻情感分析系统

基于 FastAPI 和 Vue.js 的股票新闻情感分析系统，支持分析 A 股上市公司的新闻情感倾向。

## 功能特点

- 支持股票名称和代码搜索
- 获取近 7 天的相关新闻
- 使用 Gemini API 进行情感分析
- 数据缓存优化
- 响应式界面设计

## 后端 API

### 环境要求

- Python 3.8+
- 依赖包：见 requirements.txt

### 安装步骤

1. 克隆项目

```bash
git clone [项目地址]
cd [项目目录]
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 配置环境变量
   创建.env 文件，添加以下配置：

```
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-1.5-flash
```

4. 运行后端服务

```bash
cd backend
uvicorn main:app --reload
```

### API 接口

1. 股票搜索

```
GET /api/stocks/search?query={查询词}
```

2. 股票新闻分析

```
GET /api/stock-analysis/{stock_code}?days=7&max_news=20&sentiment_news=5
```

## 前端开发中...
