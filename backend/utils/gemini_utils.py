import re
import json
import asyncio
from google import genai
from typing import Dict, Optional


def extract_json_from_markdown(text: str) -> str:
    """从Markdown格式的响应中提取JSON内容"""
    json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    return text


async def generate_content_with_retry(
    client: genai.Client,
    model: str,
    contents: str,
    max_retries: int = 3
) -> Dict:
    """带重试机制的内容生成函数

    Args:
        client: Gemini API客户端
        model: 模型名称
        contents: 提示词内容
        max_retries: 最大重试次数

    Returns:
        Dict: 解析后的JSON响应

    Raises:
        Exception: 当所有重试都失败时抛出异常
    """
    last_error = None
    for attempt in range(max_retries):
        try:
            # 发送请求
            response = client.models.generate_content(
                model=model,
                contents=contents
            )

            # 提取JSON内容
            json_text = extract_json_from_markdown(response.text)

            # 解析JSON
            try:
                return json.loads(json_text)
            except json.JSONDecodeError as e:
                raise Exception(f"JSON解析失败: {e}\n原始响应: {response.text}")

        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                # 使用指数退避策略
                await asyncio.sleep(2 ** attempt)
                continue
            raise Exception(f"Gemini API调用失败: {str(last_error)}")


class GeminiClient:
    """Gemini API客户端封装"""

    def __init__(self, api_key: str, model: str):
        """初始化Gemini客户端

        Args:
            api_key: API密钥
            model: 模型名称
        """
        self.client = genai.Client(api_key=api_key)
        self.model = model

    async def analyze_sentiment(self, prompt: str) -> Dict:
        """分析情感

        Args:
            prompt: 提示词

        Returns:
            Dict: 情感分析结果
        """
        return await generate_content_with_retry(
            client=self.client,
            model=self.model,
            contents=prompt
        )
