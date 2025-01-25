import os
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from backend.utils.config import Config
from backend.utils.gemini_utils import GeminiClient


class SentimentAnalyzer:
    """情感分析类"""

    def __init__(self):
        """初始化情感分析器"""
        self.cache_dir = Path(__file__).parent.parent.parent / \
            'data' / 'sentiment_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 初始化Gemini客户端
        self.gemini_client = GeminiClient(
            api_key=Config.GEMINI_API_KEY,
            model=Config.GEMINI_MODEL
        )

        # 重试配置
        self.max_retries = 3
        self.retry_delay = 1  # 秒
        self.timeout = 30  # API超时时间（秒）

        # 关键词配置
        self.positive_keywords = ['利好', '增长', '突破', '创新高', '获得', '中标', '战略合作']
        self.negative_keywords = ['下滑', '亏损', '违规', '处罚', '风险', '下跌', '减持']

    def _get_cache_path(self, news_list: List[Dict]) -> Path:
        """获取缓存文件路径"""
        # 使用所有新闻标题和时间生成唯一标识
        news_key = "|".join(
            f"{news['title']}|{news['publish_time']}"
            for news in news_list
        )
        return self.cache_dir / f"{hash(news_key)}.json"

    def _load_cache(self, news_list: List[Dict]) -> Optional[Dict]:
        """加载缓存的情感分析结果"""
        try:
            cache_path = self._get_cache_path(news_list)
            if not cache_path.exists():
                return None

            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                cache_date = datetime.strptime(cache_data['date'], '%Y-%m-%d')
                if cache_date.date() == datetime.now().date():
                    return cache_data['analysis_result']
        except Exception as e:
            print(f"读取情感分析缓存出错: {e}")
        return None

    def _save_cache(self, news_list: List[Dict], analysis_result: Dict):
        """保存情感分析结果到缓存"""
        try:
            cache_data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'analysis_result': analysis_result
            }
            with open(self._get_cache_path(news_list), 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存情感分析缓存出错: {e}")

    def _analyze_by_keywords(self, news_list: List[Dict]) -> Dict:
        """使用关键词进行简单情感分析"""
        total_score = 0.0
        risk_factors = []

        for news in news_list:
            title = news['title'].lower()
            content = news['content'].lower()
            text = title + ' ' + content

            # 计算情感得分
            positive_count = sum(
                1 for word in self.positive_keywords if word in text)
            negative_count = sum(
                1 for word in self.negative_keywords if word in text)

            # 标题权重加倍
            title_positive = sum(
                1 for word in self.positive_keywords if word in title)
            title_negative = sum(
                1 for word in self.negative_keywords if word in title)

            score = (positive_count + title_positive * 2 -
                     negative_count - title_negative * 2) / 10
            score = max(-1.0, min(1.0, score))  # 限制在-1到1之间
            total_score += score

            # 收集风险因素
            for word in self.negative_keywords:
                if word in text:
                    risk_factors.append({
                        "factor": word,
                        "description": f"新闻中提到{word}相关内容，需要关注"
                    })

        # 计算平均得分
        avg_score = total_score / len(news_list) if news_list else 0.0

        # 确定情感标签
        if avg_score >= 0.7:
            label = "极度看好"
        elif avg_score >= 0.3:
            label = "看好"
        elif avg_score >= -0.3:
            label = "中性"
        elif avg_score >= -0.7:
            label = "看空"
        else:
            label = "极度看空"

        # 生成分析结果
        return {
            "overall_sentiment": {
                "score": avg_score,
                "label": label,
                "summary": f"基于关键词分析，新闻整体情感倾向为{label}，得分为{avg_score:.2f}"
            },
            "dimension_analysis": {
                "fundamental": {
                    "score": avg_score,
                    "analysis": "基于关键词的简单分析，具体情况请参考原始新闻"
                },
                "technical": {
                    "score": 0.0,
                    "analysis": "关键词分析无法提供准确的技术面分析"
                },
                "industry": {
                    "score": avg_score,
                    "analysis": "基于关键词的简单分析，具体情况请参考原始新闻"
                }
            },
            "risk_analysis": {
                "risk_level": "高" if avg_score < -0.3 else "中" if avg_score < 0.3 else "低",
                "risk_factors": risk_factors[:3]  # 最多返回3个风险因素
            }
        }

    async def analyze_sentiment(self, news_list: List[Dict], max_news: int = 5) -> Dict:
        """分析新闻情感

        Args:
            news_list: 新闻列表
            max_news: 用于分析的最大新闻数量

        Returns:
            Dict: 情感分析结果，包含多维度分析
        """
        if not news_list:
            return {
                'analysis_summary': {
                    'overall_score': 0.0,
                    'sentiment_label': '中性',
                    'analysis_period': {
                        'start_date': None,
                        'end_date': None
                    }
                },
                'news_analysis': []
            }

        # 只分析最新的n条新闻
        news_to_analyze = news_list[:max_news]

        # 尝试加载缓存
        cached_result = self._load_cache(news_to_analyze)
        if cached_result is not None:
            return self._format_response(cached_result, news_to_analyze)

        try:
            # 准备新闻内容
            news_content = "\n\n".join([
                f"标题：{news['title']}\n"
                f"来源：{news['source']}\n"
                f"时间：{news['publish_time']}\n"
                f"内容：{news['content']}"
                for news in news_to_analyze
            ])

            # 使用模板构建提示词
            prompt = Config.SENTIMENT_PROMPT.format(news_content=news_content)

            try:
                # 使用GeminiClient进行分析
                analysis_result = await self.gemini_client.analyze_sentiment(prompt)
            except Exception as e:
                print(f"Gemini API分析失败，使用关键词分析作为备选: {e}")
                # 如果API调用失败，使用关键词分析
                analysis_result = self._analyze_by_keywords(news_to_analyze)

            # 保存缓存
            self._save_cache(news_to_analyze, analysis_result)

            # 格式化响应
            return self._format_response(analysis_result, news_to_analyze)

        except Exception as e:
            print(f"情感分析出错: {e}")
            # 发生错误时使用关键词分析作为备选方案
            analysis_result = self._analyze_by_keywords(news_to_analyze)
            return self._format_response(analysis_result, news_to_analyze)

    def _format_response(self, analysis_result: Dict, news_list: List[Dict]) -> Dict:
        """格式化API响应"""
        try:
            # 获取分析时间范围
            dates = [datetime.strptime(news['publish_time'], '%Y-%m-%d %H:%M:%S')
                     for news in news_list]
            start_date = min(dates) if dates else None
            end_date = max(dates) if dates else None

            return {
                'analysis_summary': {
                    'overall_score': analysis_result['overall_sentiment']['score'],
                    'sentiment_label': analysis_result['overall_sentiment']['label'],
                    'summary': analysis_result['overall_sentiment']['summary'],
                    'analysis_period': {
                        'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
                        'end_date': end_date.strftime('%Y-%m-%d') if end_date else None
                    }
                },
                'news_analysis': news_list,
                'dimension_analysis': analysis_result['dimension_analysis'],
                'risk_analysis': analysis_result['risk_analysis']
            }
        except Exception as e:
            print(f"格式化响应时出错: {e}")
            # 如果格式化失败，返回一个基本的响应
            return {
                'analysis_summary': {
                    'overall_score': 0.0,
                    'sentiment_label': '中性',
                    'summary': '数据处理过程中出现错误',
                    'analysis_period': {
                        'start_date': None,
                        'end_date': None
                    }
                },
                'news_analysis': news_list,
                'dimension_analysis': None,
                'risk_analysis': None
            }
