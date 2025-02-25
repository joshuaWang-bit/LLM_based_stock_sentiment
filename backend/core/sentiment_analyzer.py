import os
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from utils.config import Config
from utils.gemini_utils import GeminiClient
import math


class SentimentAnalyzer:
    """情感分析类"""

    def __init__(self):
        """初始化情感分析器"""
        # 确保缓存目录存在
        self.cache_dir = Config.SENTIMENT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 初始化Gemini客户端
        self.gemini_client = GeminiClient(
            api_key=Config.GEMINI_API_KEY,
            model=Config.GEMINI_MODEL
        )

        # 关键词配置
        self.positive_keywords = ['利好', '增长', '突破', '创新高', '获得', '中标', '战略合作']
        self.negative_keywords = ['下滑', '亏损', '违规', '处罚', '风险', '下跌', '减持']

    def _generate_cache_key(self, news_list: List[Dict], max_news: int) -> str:
        """生成缓存键

        Args:
            news_list: 新闻列表
            max_news: 分析的新闻数量

        Returns:
            str: 缓存键
        """
        # 使用新闻内容和参数生成唯一标识
        news_key = "|".join(
            f"{news['title']}|{news['publish_time']}"
            for news in news_list[:max_news]  # 只使用实际分析的新闻生成缓存键
        )
        # 使用abs确保hash值为正数
        return f"{abs(hash(news_key))}_{max_news}"

    def _get_cache_file_path(self, cache_key: str) -> Path:
        """获取缓存文件路径

        Args:
            cache_key: 缓存键

        Returns:
            Path: 缓存文件路径
        """
        return self.cache_dir / f"{cache_key}.json"

    def _load_from_cache(self, news_list: List[Dict], max_news: int) -> Optional[Dict]:
        """从缓存加载情感分析结果

        Args:
            news_list: 新闻列表
            max_news: 分析的新闻数量

        Returns:
            Optional[Dict]: 缓存的分析结果，如果没有有效缓存则返回None
        """
        try:
            cache_key = self._generate_cache_key(news_list, max_news)
            cache_path = self._get_cache_file_path(cache_key)

            if not cache_path.exists():
                return None

            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
                cache_date = datetime.strptime(cache_data['date'], '%Y-%m-%d')
                if (datetime.now() - cache_date).days <= Config.CACHE_VALID_DAYS:
                    return cache_data['analysis_result']
        except Exception as e:
            print(f"读取情感分析缓存出错: {e}")
        return None

    def _save_to_cache(self, news_list: List[Dict], max_news: int, analysis_result: Dict):
        """保存情感分析结果到缓存

        Args:
            news_list: 新闻列表
            max_news: 分析的新闻数量
            analysis_result: 分析结果
        """
        try:
            cache_key = self._generate_cache_key(news_list, max_news)
            cache_path = self._get_cache_file_path(cache_key)

            # 打印调试信息
            print(f"缓存目录: {self.cache_dir}")
            print(f"缓存目录是否存在: {self.cache_dir.exists()}")

            # 确保缓存目录存在（包括所有父目录）
            os.makedirs(str(self.cache_dir), exist_ok=True)

            print(f"创建目录后，缓存目录是否存在: {self.cache_dir.exists()}")
            print(f"正在保存缓存到: {cache_path}")

            cache_data = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'analysis_result': analysis_result
            }

            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            print(f"缓存保存成功: {cache_path}")
        except Exception as e:
            print(f"保存情感分析缓存出错: {e}")
            print(f"缓存路径: {cache_path}")
            print(f"缓存目录是否存在: {self.cache_dir.exists()}")
            # 打印完整的异常堆栈
            import traceback
            print(f"异常堆栈: {traceback.format_exc()}")

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

            # 计算得分并归一化到0-1范围
            raw_score = (positive_count + title_positive * 2 -
                         negative_count - title_negative * 2) / 10
            score = (raw_score + 1) / 2  # 将-1到1的范围转换为0到1
            score = max(0.0, min(1.0, score))  # 限制在0到1之间
            total_score += score

            # 收集风险因素
            for word in self.negative_keywords:
                if word in text:
                    risk_factors.append({
                        "factor": word,
                        "description": f"新闻中提到{word}相关内容，需要关注",
                        "severity": "高" if score < 0.2 else "中" if score < 0.5 else "低"
                    })

        # 计算平均得分
        avg_score = total_score / \
            len(news_list) if news_list else 0.5  # 默认为中性0.5

        # 确定情感标签
        if avg_score >= 0.85:
            label = "极度看好"
        elif avg_score >= 0.65:
            label = "看好"
        elif avg_score >= 0.35:
            label = "中性"
        elif avg_score >= 0.15:
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
            "time_analysis": {
                "trend": [],
                "trend_prediction": "基于关键词分析无法提供准确的趋势预测"
            },
            "topic_analysis": {
                topic: {
                    "score": avg_score,
                    "summary": "基于关键词的简单分析",
                    "key_points": []
                } for topic in Config.NEWS_TOPICS.keys()
            },
            "source_analysis": {
                "mainstream_media": {"score": avg_score, "summary": "基于关键词分析"},
                "industry_media": {"score": avg_score, "summary": "基于关键词分析"},
                "self_media": {"score": avg_score, "summary": "基于关键词分析"},
                "official_announcement": {"score": avg_score, "summary": "基于关键词分析"}
            },
            "impact_analysis": {
                "importance_level": "高" if avg_score > 0.8 or avg_score < 0.2 else "中" if avg_score > 0.65 or avg_score < 0.35 else "低",
                "market_impact": {
                    # 将0-1范围的偏离中性程度转换为0-1的影响力
                    "score": abs(avg_score - 0.5) * 2,
                    "duration": "短期",
                    "key_factors": []
                }
            },
            "risk_analysis": {
                "risk_level": "高" if avg_score < 0.35 else "中" if avg_score < 0.65 else "低",
                "risk_factors": risk_factors[:3]  # 最多返回3个风险因素
            }
        }

    async def analyze_sentiment(
        self,
        news_list: List[Dict],
    ) -> Dict:
        """分析新闻情感

        Args:
            news_list: 新闻列表

        Returns:
            Dict: 情感分析结果，包含多维度分析
        """
        print(f"开始情感分析，新闻数量: {len(news_list)}")

        if not news_list:
            print("没有新闻数据可供分析")
            return self._format_response({
                'overall_sentiment': {
                    'score': 0.0,
                    'label': '中性',
                    'summary': '没有可分析的新闻',
                    'market_expectation': ''
                }
            }, [])

        # 按时间排序新闻
        news_to_analyze = sorted(
            news_list,
            key=lambda x: x['publish_time'],
            reverse=True
        )

        print(f"将分析 {len(news_to_analyze)} 条新闻")

        # 尝试加载缓存
        cached_result = self._load_from_cache(
            news_to_analyze, len(news_to_analyze))
        if cached_result is not None:
            print("使用缓存的分析结果")
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

            print("已准备新闻内容用于分析")

            # 使用模板构建提示词
            prompt = Config.SENTIMENT_PROMPT.format(news_content=news_content)
            print("已构建分析提示词")

            try:
                print("开始调用 Gemini API 进行分析...")
                # 使用GeminiClient进行分析
                analysis_result = await self.gemini_client.analyze_sentiment(prompt)
                print("Gemini API 分析完成，结果类型:", type(analysis_result))
                print("分析结果:", json.dumps(
                    analysis_result, ensure_ascii=False, indent=2))

                # 保存缓存
                print("正在保存分析结果到缓存...")
                self._save_to_cache(news_to_analyze, len(
                    news_to_analyze), analysis_result)
            except Exception as e:
                print(f"Gemini API分析失败，详细错误: {str(e)}")
                print("使用关键词分析作为备选方案")
                # 如果API调用失败，使用关键词分析
                analysis_result = self._analyze_by_keywords(news_to_analyze)

            # 格式化响应
            print("正在格式化分析结果...")
            formatted_result = self._format_response(
                analysis_result, news_to_analyze)
            print("格式化完成")
            return formatted_result

        except Exception as e:
            print(f"情感分析过程中出错: {str(e)}")
            print("错误的完整堆栈跟踪:")
            import traceback
            print(traceback.format_exc())
            # 发生错误时使用关键词分析作为备选方案
            print("使用关键词分析作为备选方案")
            analysis_result = self._analyze_by_keywords(news_to_analyze)
            return self._format_response(analysis_result, news_to_analyze)

    def _calculate_confidence_index(self, news_list: List[Dict], analysis_result: Dict) -> float:
        """计算置信度指数

        基于以下因素计算：
        1. 新闻来源的可靠性
        2. 新闻的时效性
        3. 情感倾向的一致性

        Returns:
            float: 0-1之间的置信度指数
        """
        if not news_list:
            return 0.0

        # 1. 计算来源可靠性得分
        source_weights = {
            'official_announcement': 1.0,  # 官方公告
            'mainstream_media': 0.8,       # 主流媒体
            'industry_media': 0.6,         # 行业媒体
            'self_media': 0.4              # 自媒体
        }

        source_scores = []
        for news in news_list:
            source_type = 'self_media'  # 默认为自媒体
            if '公告' in news['source'] or '互动易' in news['source']:
                source_type = 'official_announcement'
            elif any(media in news['source'] for media in ['新闻', '日报', '时报']):
                source_type = 'mainstream_media'
            elif any(media in news['source'] for media in ['证券', '财经', '金融']):
                source_type = 'industry_media'
            source_scores.append(source_weights[source_type])

        source_reliability = sum(source_scores) / len(source_scores)

        # 2. 计算时效性得分
        current_time = datetime.now()
        time_scores = []
        for news in news_list:
            news_time = datetime.strptime(
                news['publish_time'], '%Y-%m-%d %H:%M:%S')
            days_diff = (current_time - news_time).days
            # 使用指数衰减，7天以内的新闻时效性较高
            time_score = max(0.2, min(1.0, math.exp(-days_diff / 7)))
            time_scores.append(time_score)

        timeliness = sum(time_scores) / len(time_scores)

        # 3. 计算情感一致性得分
        sentiment_scores = []
        overall_score = analysis_result['overall_sentiment']['score']

        # 从time_analysis中获取每条新闻的情感分数
        if 'time_analysis' in analysis_result and 'trend' in analysis_result['time_analysis']:
            for trend in analysis_result['time_analysis']['trend']:
                if 'score' in trend:
                    sentiment_scores.append(trend['score'])

        if sentiment_scores:
            # 计算情感分数的标准差，标准差越小表示一致性越高
            mean_score = sum(sentiment_scores) / len(sentiment_scores)
            variance = sum((score - mean_score) **
                           2 for score in sentiment_scores) / len(sentiment_scores)
            std_dev = math.sqrt(variance)
            # 将标准差映射到0-1区间，标准差越小，一致性得分越高
            consistency = max(0.0, min(1.0, 1 - std_dev))
        else:
            consistency = 0.5  # 如果没有足够的数据，给一个中等的一致性分数

        # 综合计算置信度，给予不同因素不同的权重
        confidence_index = (
            0.4 * source_reliability +  # 来源可靠性占40%
            0.3 * timeliness +         # 时效性占30%
            0.3 * consistency          # 一致性占30%
        )

        return round(confidence_index, 2)

    def _format_key_events(self, events: List) -> List[Dict]:
        """格式化关键事件列表，确保符合新的数据结构

        Args:
            events: 原始事件列表，可能是字符串列表或已经是新格式

        Returns:
            List[Dict]: 格式化后的事件列表，每个事件包含title和description
        """
        formatted_events = []
        for event in events:
            # 如果已经是新格式，直接使用
            if isinstance(event, dict) and 'title' in event and 'description' in event:
                formatted_events.append(event)
            # 如果是旧格式（字符串），转换为新格式
            elif isinstance(event, str):
                formatted_events.append({
                    'title': event,  # 使用原字符串作为标题
                    'description': ''  # 暂时为空，因为旧格式没有描述
                })
            # 忽略其他格式
        return formatted_events

    def _format_response(self, analysis_result: Dict, news_list: List[Dict]) -> Dict:
        """格式化API响应"""
        print("开始格式化响应...")
        print("输入的 analysis_result 类型:", type(analysis_result))
        print("输入的 analysis_result 内容:", json.dumps(
            analysis_result, ensure_ascii=False, indent=2))

        try:
            # 获取分析时间范围
            dates = [datetime.strptime(
                news['publish_time'], '%Y-%m-%d %H:%M:%S') for news in news_list]
            start_date = min(dates) if dates else None
            end_date = max(dates) if dates else None

            # 验证必要的字段是否存在
            if not isinstance(analysis_result, dict):
                print(f"错误：analysis_result 不是字典类型，而是 {type(analysis_result)}")
                raise ValueError("analysis_result must be a dictionary")

            if 'overall_sentiment' not in analysis_result:
                print("错误：缺少 overall_sentiment 字段")
                raise ValueError(
                    "Missing overall_sentiment in analysis_result")

            # 从LLM响应中获取置信度指数
            confidence_index = analysis_result['overall_sentiment'].get(
                'confidence_index')
            print(f"从LLM获取的置信度指数: {confidence_index}")

            # 如果LLM没有返回置信度指数，则计算一个
            if confidence_index is None:
                confidence_index = self._calculate_confidence_index(
                    news_list, analysis_result)
                print(f"计算得到的置信度指数: {confidence_index}")

            # 格式化时间分析中的key_events
            if 'time_analysis' in analysis_result and 'trend' in analysis_result['time_analysis']:
                for trend in analysis_result['time_analysis']['trend']:
                    if 'key_events' in trend:
                        trend['key_events'] = self._format_key_events(
                            trend['key_events'])

            formatted_response = {
                'analysis_summary': {
                    'overall_score': analysis_result['overall_sentiment']['score'],
                    'sentiment_label': analysis_result['overall_sentiment']['label'],
                    'summary': analysis_result['overall_sentiment']['summary'],
                    'market_expectation': analysis_result['overall_sentiment'].get('market_expectation', ''),
                    'investor_sentiment': analysis_result['overall_sentiment'].get('investor_sentiment', '无'),
                    'analysis_period': {
                        'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
                        'end_date': end_date.strftime('%Y-%m-%d') if end_date else None
                    },
                    'confidence_index': confidence_index
                },
                'time_analysis': analysis_result.get('time_analysis', {
                    'trend': [],
                    'trend_prediction': ''
                }),
                'topic_analysis': analysis_result.get('topic_analysis', {
                    topic: {
                        'score': 0.0,
                        'summary': '',
                        'key_points': []
                    } for topic in Config.NEWS_TOPICS.keys()
                }),
                'source_analysis': analysis_result.get('source_analysis', {
                    'mainstream_media': {'score': 0.0, 'summary': ''},
                    'industry_media': {'score': 0.0, 'summary': ''},
                    'self_media': {'score': 0.0, 'summary': ''},
                    'official_announcement': {'score': 0.0, 'summary': ''}
                }),
                'impact_analysis': analysis_result.get('impact_analysis', {
                    'importance_level': '中',
                    'market_impact': {
                        'score': 0.0,
                        'duration': '',
                        'key_factors': []
                    }
                }),
                'risk_analysis': analysis_result.get('risk_analysis', {
                    'risk_level': '中',
                    'risk_factors': []
                }),
                'news_analysis': news_list
            }

            print("响应格式化成功")
            return formatted_response

        except Exception as e:
            print(f"格式化响应时出错: {str(e)}")
            print("错误的完整堆栈跟踪:")
            import traceback
            print(traceback.format_exc())
            # 如果格式化失败，返回一个基本的响应
            return {
                'analysis_summary': {
                    'overall_score': 0.0,
                    'sentiment_label': '中性',
                    'summary': '数据处理过程中出现错误',
                    'market_expectation': '',
                    'investor_sentiment': '无',
                    'analysis_period': {
                        'start_date': None,
                        'end_date': None
                    },
                    'confidence_index': 0.0
                },
                'time_analysis': {
                    'trend': [],
                    'trend_prediction': ''
                },
                'topic_analysis': {
                    topic: {
                        'score': 0.0,
                        'summary': '',
                        'key_points': []
                    } for topic in Config.NEWS_TOPICS.keys()
                },
                'source_analysis': {
                    'mainstream_media': {'score': 0.0, 'summary': ''},
                    'industry_media': {'score': 0.0, 'summary': ''},
                    'self_media': {'score': 0.0, 'summary': ''},
                    'official_announcement': {'score': 0.0, 'summary': ''}
                },
                'impact_analysis': {
                    'importance_level': '中',
                    'market_impact': {
                        'score': 0.0,
                        'duration': '',
                        'key_factors': []
                    }
                },
                'risk_analysis': {
                    'risk_level': '中',
                    'risk_factors': []
                },
                'news_analysis': []
            }
