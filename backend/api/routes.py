from fastapi import APIRouter, HTTPException
from typing import List, Dict
import akshare as ak
from backend.core.news_crawler import NewsCrawler
from backend.core.sentiment_analyzer import SentimentAnalyzer
from backend.core.stock_cache import StockCache
from backend.utils.config import Config

router = APIRouter()
news_crawler = NewsCrawler()
sentiment_analyzer = SentimentAnalyzer()
stock_cache = StockCache()


@router.get("/stocks/search")
async def search_stocks(query: str) -> List[Dict]:
    """搜索股票

    Args:
        query: 股票名称或代码关键词

    Returns:
        List[Dict]: 股票列表，包含代码和名称
    """
    try:
        # 使用缓存获取股票数据
        def fetch_stocks(q: str) -> Dict:
            # 使用akshare获取股票列表
            stock_df = ak.stock_info_a_code_name()
            # 过滤匹配的股票
            matched_stocks = stock_df[
                stock_df['name'].str.contains(q) |
                stock_df['code'].str.contains(q)
            ]
            return {
                'stocks': [
                    {"code": row['code'], "name": row['name']}
                    for _, row in matched_stocks.iterrows()
                ]
            }
        
        # 从缓存获取或重新获取股票数据
        result = stock_cache.get_stocks(query, lambda q: fetch_stocks(q))
        return result['stocks']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock-analysis/{stock_code}")
async def get_stock_analysis(
    stock_code: str,
    days: int = Config.DEFAULT_DAYS,
    max_news: int = Config.MAX_NEWS_PER_STOCK
) -> Dict:
    """获取股票新闻分析结果

    Args:
        stock_code: 股票代码
        days: 获取最近几天的新闻，默认7天
        max_news: 最大新闻条数，默认20条

    Returns:
        Dict: 分析结果，包含:
            - stock_info: 股票信息
            - analysis_summary: 分析摘要
            - time_analysis: 时间维度分析
            - topic_analysis: 主题维度分析
            - source_analysis: 来源维度分析
            - impact_analysis: 影响力分析
            - risk_analysis: 风险分析
            - news_analysis: 新闻列表
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
            news_list=news_list
        )

        return {
            "stock_info": {
                "code": stock_info['code'],
                "name": stock_info['name']
            },
            **analysis_result
        }

    except IndexError:
        raise HTTPException(
            status_code=404,
            detail=f"Stock with code {stock_code} not found"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
