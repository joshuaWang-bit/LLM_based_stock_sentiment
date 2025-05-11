import os
import re
import json
import asyncio
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def extract_json_from_markdown(text: str) -> str:
    """从Markdown格式的响应中提取JSON内容"""
    json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    return text

class DeepSeekClient:
    """DeepSeek API客户端封装"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1", model: str = "deepseek-chat"):
        """
        Args:
            api_key: DeepSeek API密钥
            model: 模型名称（默认deepseek-chat）
        """
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,  # DeepSeek API端点
            max_retries=3,  # 使用LangChain内置重试机制
        )
        self.parser = JsonOutputParser()

    async def analyze_sentiment(self, prompt: str) -> Dict:
        """情感分析（带JSON格式输出）"""
        # 构建带格式要求的提示词
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a professional stock analyst."),
            ("human", "{input}"),
        ])
        chain = prompt_template | self.llm | self.parser
        
        try:
            # 异步调用
            result = await chain.ainvoke({"input": prompt})
            return result
        except json.JSONDecodeError as e:
            # 处理格式错误的情况
            raw_response = str(e)
            json_text = extract_json_from_markdown(raw_response)
            return json.loads(json_text)

# 使用示例
async def main():
    client = DeepSeekClient(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        model="deepseek-chat"
    )
    
    analysis = await client.analyze_sentiment(
        "这款产品的用户体验非常出色，但价格有点昂贵。"
    )
    print(analysis)

if __name__ == "__main__":
    asyncio.run(main())