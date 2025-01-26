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
    SENTIMENT_PROMPT = '''你是一位专业的股票分析师，请对以下新闻进行多维度分析，并以JSON格式返回分析结果。

新闻内容：
{news_content}

请从以下维度进行分析并返回结构化的JSON结果：

1. 整体市场情绪分析：
- 总体情感得分（0到1，0表示极度负面，1表示极度正面）
- 情感标签（极度看好/看好/中性/看空/极度看空）
- 关键观点总结（100字以内）
- 市场预期分析
- 投资者情绪指数（0到100的整数）：
  * 基于新闻中投资者行为（如买入、卖出、增持、减持等）
  * 基于机构投资者动态（如机构调研、评级、持仓变化等）
  * 基于散户投资者表现（如交易活跃度、情绪倾向等）
  * 如果新闻中没有明显的投资者相关信息，返回"无"
- 置信度指数（必须提供，0到1之间的浮点数）：
  * 基于新闻来源可靠性（官方公告>主流媒体>行业媒体>自媒体）
  * 基于新闻时效性（越新越可靠）
  * 基于新闻内容一致性（观点一致性越高越可靠）
  * 基于数据支撑充分性（有具体数据支撑的更可靠）

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
        "score": 0.0,  # 情感得分，范围0到1
        "label": "string",  # 情感标签：极度看好/看好/中性/看空/极度看空
        "summary": "string",  # 整体分析总结，100字以内
        "market_expectation": "string",  # 市场预期分析
        "investor_sentiment": 0,  # 投资者情绪指数，范围0-100，如无相关信息则为"无"
        "confidence_index": 0.0  # 置信度指数，范围0到1，基于新闻来源可靠性、时效性、一致性和数据支撑
    }},
    "time_analysis": {{
        "trend": [
            {{
                "date": "YYYY-MM-DD",
                "score": 0.0,
                "key_events": [
                    {{
                        "title": "string",  # 事件标题，5字以内，如"解禁消息"
                        "description": "string"  # 事件描述，20字以内，如"1.2亿股限售股将于2月1日解禁"
                    }}
                ]
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
7. 影响力分析应基于新闻内容的重要性和市场敏感度
8. 置信度指数必须提供，且需要综合考虑新闻来源可靠性、时效性、一致性和数据支撑
9. key_events中的每个事件必须包含title和description两个字段，title应该简短精炼（5字以内），description应该对title进行补充说明（20字以内）
10. 投资者情绪指数必须基于新闻中的投资者行为相关信息，如果没有相关信息则返回"无"'''

#     # 新闻爬取配置
#     NEWS_CACHE_DAYS = 1  # 新闻缓存天数

#     # 主题分类
#     NEWS_TOPICS = {
#         'company_operation': '公司经营',
#         'financial_performance': '财务表现',
#         'market_competition': '市场竞争',
#         'product_technology': '产品技术',
#         'industry_policy': '行业政策',
#         'capital_market': '资本市场'
#     }

#     # 情感分析配置
#     SENTIMENT_PROMPT = '''你是一位专业的股票分析师，请对以下新闻进行多维度分析，并以JSON格式返回分析结果。

# 新闻内容：
# {news_content}

# 请从以下维度进行分析并返回结构化的JSON结果：

# 1. 整体市场情绪分析：
# - 总体情感得分和标签
# - 关键观点总结
# - 市场预期分析

# 2. 时间维度分析：
# - 按日期的情感变化趋势
# - 重要时间节点识别
# - 趋势预测

# 3. 主题维度分析：
# - 公司经营相关新闻分析
# - 财务表现相关新闻分析
# - 市场竞争相关新闻分析
# - 产品技术相关新闻分析
# - 行业政策相关新闻分析
# - 资本市场相关新闻分析

# 4. 来源维度分析：
# - 主流媒体观点
# - 行业媒体观点
# - 自媒体观点
# - 官方发布观点

# 5. 影响力分析：
# - 新闻重要性评级
# - 市场影响力评估
# - 持续影响时间预测

# 请按照以下JSON格式返回分析结果：
# {{
#     "overall_sentiment": {{
#         "score": 0.0,  # 情感得分，范围-1到1
#         "label": "string",  # 情感标签：极度看好/看好/中性/看空/极度看空
#         "summary": "string",  # 整体分析总结，100字以内
#         "market_expectation": "string"  # 市场预期分析
#     }},
#     "time_analysis": {{
#         "trend": [
#             {{
#                 "date": "YYYY-MM-DD",
#                 "score": 0.0,
#                 "key_events": ["string"]
#             }}
#         ],
#         "trend_prediction": "string"  # 趋势预测
#     }},
#     "topic_analysis": {{
#         "company_operation": {{
#             "score": 0.0,
#             "summary": "string",
#             "key_points": ["string"]
#         }},
#         "financial_performance": {{
#             "score": 0.0,
#             "summary": "string",
#             "key_points": ["string"]
#         }},
#         "market_competition": {{
#             "score": 0.0,
#             "summary": "string",
#             "key_points": ["string"]
#         }},
#         "product_technology": {{
#             "score": 0.0,
#             "summary": "string",
#             "key_points": ["string"]
#         }},
#         "industry_policy": {{
#             "score": 0.0,
#             "summary": "string",
#             "key_points": ["string"]
#         }},
#         "capital_market": {{
#             "score": 0.0,
#             "summary": "string",
#             "key_points": ["string"]
#         }}
#     }},
#     "source_analysis": {{
#         "mainstream_media": {{
#             "score": 0.0,
#             "summary": "string"
#         }},
#         "industry_media": {{
#             "score": 0.0,
#             "summary": "string"
#         }},
#         "self_media": {{
#             "score": 0.0,
#             "summary": "string"
#         }},
#         "official_announcement": {{
#             "score": 0.0,
#             "summary": "string"
#         }}
#     }},
#     "impact_analysis": {{
#         "importance_level": "string",  # 高/中/低
#         "market_impact": {{
#             "score": 0.0,  # 影响力得分，范围0-1
#             "duration": "string",  # 预计持续时间
#             "key_factors": ["string"]
#         }}
#     }},
#     "risk_analysis": {{
#         "risk_level": "string",  # 高/中/低
#         "risk_factors": [
#             {{
#                 "factor": "string",
#                 "description": "string",
#                 "severity": "string"  # 高/中/低
#             }}
#         ]
#     }}
# }}

# 注意：
# 1. 所有得分均在相应范围内
# 2. 分析内容应简明扼要，突出重点
# 3. 确保返回格式严格符合上述JSON结构
# 4. 时间维度分析应考虑新闻发布时间的先后顺序
# 5. 主题分类应准确，一条新闻可能属于多个主题
# 6. 来源分析应考虑不同类型媒体的可信度
# 7. 影响力分析应基于新闻内容的重要性和市场敏感度'''
