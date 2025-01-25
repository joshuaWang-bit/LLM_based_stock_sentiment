import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict

# 加载.env文件
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


class Config:
    """配置管理类"""

    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

    # News limits
    MAX_NEWS_PER_STOCK = 20  # 每个股票最大新闻数量
    MAX_NEWS_FOR_SENTIMENT = 20  # 用于情感分析的最大新闻数量
    DEFAULT_DAYS = 7  # 默认获取天数

    # Cache settings
    CACHE_VALID_DAYS = 1  # 缓存有效期（天）
    NEWS_CACHE_DIR = Path(__file__).parent.parent.parent / \
        'data' / 'news_cache'
    SENTIMENT_CACHE_DIR = Path(
        __file__).parent.parent.parent / 'data' / 'sentiment_cache'

    # News topics for analysis
    NEWS_TOPICS: Dict[str, str] = {
        'company_operation': '公司经营',
        'financial_performance': '财务表现',
        'market_competition': '市场竞争',
        'product_technology': '产品技术',
        'industry_policy': '行业政策',
        'capital_market': '资本市场'
    }

    # Sentiment analysis prompt template
    SENTIMENT_PROMPT = '''你是一位专业的股票分析师，请对以下新闻进行多维度定量分析，并以JSON格式返回分析结果。注意所有分析结果都应该尽可能数值化，以便于数据可视化展示。

新闻内容：
{news_content}

请从以下维度进行分析并返回结构化的JSON结果：

1. 整体市场情绪分析：
- 总体情感得分（-1到1）和标签
- 信心指数（0-100）
- 市场预期强度（-100到100）
- 投资者情绪指标（恐慌-0到贪婪-100）

2. 时间维度分析：
- 按日期的情感变化趋势
- 重要时间节点的影响强度
- 趋势预测的置信度

3. 主题维度分析（对每个主题）：
- 相关度得分（0-1）
- 情感倾向（-1到1）
- 重要性评分（0-10）
- 可信度评分（0-1）

4. 来源维度分析：
- 不同来源的可信度评分
- 报道立场的客观性评分
- 信息重要性评分

5. 影响力分析：
- 短期影响力指数（0-100）
- 中期影响力指数（0-100）
- 长期影响力指数（0-100）
- 市场敏感度评分（0-10）

6. 风险收益分析：
- 潜在收益评分（0-100）
- 风险程度评分（0-100）
- 风险收益比
- 建议持仓时长（天数）

7. 技术面分析：
- 成交量影响预期（-1到1）
- 价格趋势影响（-1到1）
- 技术指标影响（-1到1）

8. 基本面分析：
- 业绩影响评分（-10到10）
- 行业地位变化（-1到1）
- 竞争力评分变化（-1到1）

请按照以下JSON格式返回分析结果：
{{
    "overall_sentiment": {{
        "score": 0.0,  # 情感得分，范围-1到1
        "label": "string",  # 情感标签：极度看好/看好/中性/看空/极度看空
        "confidence_index": 0,  # 信心指数，0-100
        "market_expectation_strength": 0,  # 市场预期强度，-100到100
        "investor_sentiment": 0,  # 投资者情绪指标，0-100
        "summary": "string",  # 整体分析总结，100字以内
        "key_factors": [  # 关键影响因素
            {{
                "factor": "string",
                "impact_score": 0.0,  # -1到1
                "confidence": 0.0  # 0到1
            }}
        ]
    }},
    "time_analysis": {{
        "trend": [
            {{
                "date": "YYYY-MM-DD",
                "sentiment_score": 0.0,  # -1到1
                "impact_strength": 0.0,  # 0到1
                "key_events": ["string"],
                "confidence": 0.0  # 0到1
            }}
        ],
        "trend_prediction": {{
            "direction": "string",  # 上升/下降/震荡
            "confidence": 0.0,  # 0到1
            "duration_days": 0  # 预期持续天数
        }}
    }},
    "topic_analysis": {{
        "company_operation": {{
            "relevance": 0.0,  # 相关度，0到1
            "sentiment": 0.0,  # 情感倾向，-1到1
            "importance": 0,  # 重要性，0到10
            "confidence": 0.0,  # 可信度，0到1
            "key_points": [
                {{
                    "point": "string",
                    "impact_score": 0.0  # -1到1
                }}
            ]
        }},
        "financial_performance": {{...}},
        "market_competition": {{...}},
        "product_technology": {{...}},
        "industry_policy": {{...}},
        "capital_market": {{...}}
    }},
    "source_analysis": {{
        "mainstream_media": {{
            "credibility": 0.0,  # 0到1
            "objectivity": 0.0,  # 0到1
            "importance": 0.0,  # 0到1
            "sentiment": 0.0,  # -1到1
            "article_count": 0  # 文章数量
        }},
        "industry_media": {{...}},
        "self_media": {{...}},
        "official_announcement": {{...}}
    }},
    "impact_analysis": {{
        "short_term": {{
            "index": 0,  # 0到100
            "confidence": 0.0,  # 0到1
            "key_factors": ["string"]
        }},
        "mid_term": {{...}},
        "long_term": {{...}},
        "market_sensitivity": 0,  # 0到10
        "importance_level": "string"  # 高/中/低
    }},
    "risk_reward_analysis": {{
        "potential_reward": {{
            "score": 0,  # 0到100
            "factors": ["string"]
        }},
        "risk_level": {{
            "score": 0,  # 0到100
            "factors": ["string"]
        }},
        "risk_reward_ratio": 0.0,  # 风险收益比
        "suggested_holding_period": 0,  # 建议持仓天数
        "confidence": 0.0  # 0到1
    }},
    "technical_analysis": {{
        "volume_impact": {{
            "score": 0.0,  # -1到1
            "prediction": "string"
        }},
        "price_trend": {{
            "score": 0.0,  # -1到1
            "pattern": "string"
        }},
        "technical_indicators": {{
            "score": 0.0,  # -1到1
            "key_indicators": ["string"]
        }}
    }},
    "fundamental_analysis": {{
        "performance_impact": {{
            "score": 0,  # -10到10
            "key_metrics": ["string"]
        }},
        "industry_position": {{
            "change": 0.0,  # -1到1
            "factors": ["string"]
        }},
        "competitiveness": {{
            "change": 0.0,  # -1到1
            "advantages": ["string"],
            "challenges": ["string"]
        }}
    }}
}}

注意：
1. 所有数值指标必须在指定范围内
2. 所有预测和评分都应该附带置信度
3. 关键因素应该按重要性排序
4. 时间维度分析应考虑新闻发布时间的先后顺序
5. 所有分析结果都应尽可能量化，便于数据可视化
6. 对于重要指标，应该说明判断依据
7. 确保分析的全面性和数据的可靠性'''

    # 新闻爬取配置
    NEWS_CACHE_DAYS = 1  # 新闻缓存天数

    # 主题分类
    NEWS_TOPICS = {
        'company_operation': '公司经营',
        'financial_performance': '财务表现',
        'market_competition': '市场竞争',
        'product_technology': '产品技术',
        'industry_policy': '行业政策',
        'capital_market': '资本市场'
    }

    # 情感分析配置
    SENTIMENT_PROMPT = '''你是一位专业的股票分析师，请对以下新闻进行多维度分析，并以JSON格式返回分析结果。

新闻内容：
{news_content}

请从以下维度进行分析并返回结构化的JSON结果：

1. 整体市场情绪分析：
- 总体情感得分和标签
- 关键观点总结
- 市场预期分析

2. 时间维度分析：
- 按日期的情感变化趋势
- 重要时间节点识别
- 趋势预测

3. 主题维度分析：
- 公司经营相关新闻分析
- 财务表现相关新闻分析
- 市场竞争相关新闻分析
- 产品技术相关新闻分析
- 行业政策相关新闻分析
- 资本市场相关新闻分析

4. 来源维度分析：
- 主流媒体观点
- 行业媒体观点
- 自媒体观点
- 官方发布观点

5. 影响力分析：
- 新闻重要性评级
- 市场影响力评估
- 持续影响时间预测

请按照以下JSON格式返回分析结果：
{{
    "overall_sentiment": {{
        "score": 0.0,  # 情感得分，范围-1到1
        "label": "string",  # 情感标签：极度看好/看好/中性/看空/极度看空
        "summary": "string",  # 整体分析总结，100字以内
        "market_expectation": "string"  # 市场预期分析
    }},
    "time_analysis": {{
        "trend": [
            {{
                "date": "YYYY-MM-DD",
                "score": 0.0,
                "key_events": ["string"]
            }}
        ],
        "trend_prediction": "string"  # 趋势预测
    }},
    "topic_analysis": {{
        "company_operation": {{
            "score": 0.0,
            "summary": "string",
            "key_points": ["string"]
        }},
        "financial_performance": {{
            "score": 0.0,
            "summary": "string",
            "key_points": ["string"]
        }},
        "market_competition": {{
            "score": 0.0,
            "summary": "string",
            "key_points": ["string"]
        }},
        "product_technology": {{
            "score": 0.0,
            "summary": "string",
            "key_points": ["string"]
        }},
        "industry_policy": {{
            "score": 0.0,
            "summary": "string",
            "key_points": ["string"]
        }},
        "capital_market": {{
            "score": 0.0,
            "summary": "string",
            "key_points": ["string"]
        }}
    }},
    "source_analysis": {{
        "mainstream_media": {{
            "score": 0.0,
            "summary": "string"
        }},
        "industry_media": {{
            "score": 0.0,
            "summary": "string"
        }},
        "self_media": {{
            "score": 0.0,
            "summary": "string"
        }},
        "official_announcement": {{
            "score": 0.0,
            "summary": "string"
        }}
    }},
    "impact_analysis": {{
        "importance_level": "string",  # 高/中/低
        "market_impact": {{
            "score": 0.0,  # 影响力得分，范围0-1
            "duration": "string",  # 预计持续时间
            "key_factors": ["string"]
        }}
    }},
    "risk_analysis": {{
        "risk_level": "string",  # 高/中/低
        "risk_factors": [
            {{
                "factor": "string",
                "description": "string",
                "severity": "string"  # 高/中/低
            }}
        ]
    }}
}}

注意：
1. 所有得分均在相应范围内
2. 分析内容应简明扼要，突出重点
3. 确保返回格式严格符合上述JSON结构
4. 时间维度分析应考虑新闻发布时间的先后顺序
5. 主题分类应准确，一条新闻可能属于多个主题
6. 来源分析应考虑不同类型媒体的可信度
7. 影响力分析应基于新闻内容的重要性和市场敏感度'''
