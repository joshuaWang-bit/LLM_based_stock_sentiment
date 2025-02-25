# 股票新闻情感分析系统

![系统主页](assets/homepage.png)

基于 FastAPI 和 Vue.js 的股票新闻情感分析系统，支持分析 A 股上市公司的新闻情感倾向。

## 功能特点

### 数据获取与处理

- 实时股票搜索：支持按股票代码或名称快速检索
- 智能新闻爬取：自动获取近 7 天相关新闻，支持多源数据采集
- 大模型情感分析：使用 Gemini API 进行新闻情感倾向分析，提供深度洞察

### 性能优化

- 多级缓存机制：
  - 股票基础信息缓存
  - 新闻数据本地缓存
  - 情感分析结果缓存

### 可视化与交互

- 多维度数据展示：
  - 情感趋势图表
  - 新闻时间分布
  - 关键信息提取
- 响应式界面设计：支持多设备访问
- 交互式数据筛选

## 后端 API

### 环境要求

- Python 3.8+
- Poetry 包管理工具

### 安装步骤

1. 克隆项目

```bash
git clone [项目地址]
cd [项目目录]
```

2. 安装依赖

```bash

# 使用 Poetry 安装项目依赖
poetry install
```

3. 配置环境变量
   复制 .env.example 文件并重命名为 .env，然后修改配置：

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，修改以下配置
GEMINI_API_KEY=your_api_key  # 替换为你的 Gemini API 密钥
GEMINI_MODEL=gemini-1.5-flash
```

4. 运行后端服务

```bash
# 激活虚拟环境
.venv\Scripts\activate

# 进入后端目录
cd backend

# 启动后端服务
uvicorn main:app --reload
```

## 前端

### 启动步骤

1. 进入前端目录

```bash
cd frontend
```

2. 安装依赖

```bash
npm install
```

3. 启动开发服务器

```bash
npm run dev
```

4. 在浏览器中访问终端输出的地址（通常是 http://localhost: ****）

## 使用说明

1. 启动后端和前端服务
2. 在浏览器中访问前端地址
3. 在搜索框中直接输入股票代码（如：000001）
4. 等待系统分析完成，查看股票相关新闻的情感分析结果
