import os
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


class Config:
    """配置管理类"""

    # Gemini API配置
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

    # 新闻爬取配置
    MAX_NEWS_PER_STOCK = 20  # 每个股票最多爬取的新闻数量
    NEWS_CACHE_DAYS = 1  # 新闻缓存天数

    # 情感分析配置
    SENTIMENT_PROMPT = '''你是一位专业的股票分析师，请对以下新闻进行多维度分析，并以JSON格式返回分析结果。

新闻内容：
{news_content}

请从以下维度进行分析：
1. 整体市场情绪
2. 基本面分析（公司经营、财务状况等）
3. 技术面分析（股价走势、成交量等）
4. 行业分析（行业地位、竞争态势等）
5. 风险因素分析

请按照以下JSON格式返回分析结果：
{{
    "overall_sentiment": {{
        "score": 0.0,  # 情感得分，范围-1到1
        "label": "string",  # 情感标签：极度看好/看好/中性/看空/极度看空
        "summary": "string"  # 整体分析总结，100字以内
    }},
    "dimension_analysis": {{
        "fundamental": {{
            "score": 0.0,  # 基本面得分
            "analysis": "string"  # 基本面分析，100字以内
        }},
        "technical": {{
            "score": 0.0,  # 技术面得分
            "analysis": "string"  # 技术面分析，100字以内
        }},
        "industry": {{
            "score": 0.0,  # 行业得分
            "analysis": "string"  # 行业分析，100字以内
        }}
    }},
    "risk_analysis": {{
        "risk_level": "string",  # 风险等级：高/中/低
        "risk_factors": [  # 主要风险因素列表
            {{
                "factor": "string",  # 风险因素
                "description": "string"  # 风险描述
            }}
        ]
    }}
}}

注意：
1. 所有得分均在-1到1之间
2. 分析内容应简明扼要，突出重点
3. 确保返回格式严格符合上述JSON结构'''
