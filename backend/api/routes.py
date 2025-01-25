from fastapi import APIRouter, HTTPException
from typing import List, Dict
import akshare as ak
from backend.core.news_crawler import NewsCrawler
from backend.core.sentiment_analyzer import SentimentAnalyzer

router = APIRouter()
news_crawler = NewsCrawler()
sentiment_analyzer = SentimentAnalyzer()


@router.get("/stocks/search")
async def search_stocks(query: str) -> List[Dict]:
    """搜索股票

    Args:
        query: 股票名称或代码关键词

    Returns:
        List[Dict]: 股票列表，包含代码和名称
    """
    try:
        # 使用akshare获取股票列表
        stock_df = ak.stock_info_a_code_name()
        # 过滤匹配的股票
        matched_stocks = stock_df[
            stock_df['name'].str.contains(query) |
            stock_df['code'].str.contains(query)
        ]
        return [
            {"code": row['code'], "name": row['name']}
            for _, row in matched_stocks.iterrows()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock-analysis/{stock_code}")
async def get_stock_analysis(
    stock_code: str,
    days: int = 7,
    max_news: int = 20,
    sentiment_news: int = 5
) -> Dict:
    """获取股票新闻分析结果

    Args:
        stock_code: 股票代码
        days: 获取最近几天的新闻
        max_news: 最大新闻条数
        sentiment_news: 用于情感分析的新闻条数

    Returns:
        Dict: 分析结果，包含:
            - stock_info: 股票信息
            - analysis_summary: 分析摘要
            - news_analysis: 新闻分析列表
    """
    try:
        # 获取股票信息
        stock_df = ak.stock_info_a_code_name()
        stock_info = stock_df[stock_df['code'] == stock_code].iloc[0]

        # 获取新闻
        news_list = news_crawler.get_stock_news(
            stock_code=stock_code,
            days=days,
            max_news=max_news
        )

        # 分析情感
        analysis_result = await sentiment_analyzer.analyze_sentiment(
            news_list=news_list,
            max_news=sentiment_news
        )

        return {
            "stock_info": {
                "code": stock_info['code'],
                "name": stock_info['name']
            },
            **analysis_result  # 包含 analysis_summary 和 news_analysis
        }

    except IndexError:
        raise HTTPException(
            status_code=404,
            detail=f"Stock with code {stock_code} not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
