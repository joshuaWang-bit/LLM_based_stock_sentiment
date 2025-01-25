import os
import json
import asyncio
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# 加载环境变量
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# 配置API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')


def extract_json_from_markdown(text):
    """从Markdown格式的响应中提取JSON内容"""
    # 移除Markdown代码块标记
    json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        return json_match.group(1)
    return text


def generate_content_with_retry(client, model, contents, max_retries=3):
    """带重试机制的内容生成函数"""
    for attempt in range(max_retries):
        try:
            print(f"\n尝试调用 API (第{attempt + 1}次)...")
            print(f"请求内容: {contents[:500]}..." if len(
                str(contents)) > 500 else f"请求内容: {contents}")

            response = client.models.generate_content(
                model=model,
                contents=contents
            )
            return response

        except Exception as e:
            print(f"第{attempt + 1}次调用失败: {str(e)}")
            if attempt == max_retries - 1:  # 最后一次尝试
                raise
            print(f"等待 {2 ** attempt}秒后重试...")
            asyncio.sleep(2 ** attempt)  # 指数退避


async def test_gemini_api():
    """测试Gemini API的连接和响应"""
    try:
        print("开始测试Gemini API...")
        print(f"使用模型: {GEMINI_MODEL}")

        # 初始化 Gemini 客户端
        client = genai.Client(api_key=GEMINI_API_KEY)

        # 简单的测试提示词
        test_prompt = """请用JSON格式返回以下内容：
        {
            "message": "Hello, World!",
            "status": "success"
        }"""

        print("\n发送测试请求...")

        # 发送请求
        response = generate_content_with_retry(
            client=client,
            model=GEMINI_MODEL,
            contents=test_prompt
        )

        print("\n收到响应:")
        print(response.text)

        # 提取JSON内容
        json_text = extract_json_from_markdown(response.text)
        print("\n提取的JSON内容:")
        print(json_text)

        # 尝试解析JSON
        try:
            json_result = json.loads(json_text)
            print("\nJSON解析成功!")
            print(json.dumps(json_result, ensure_ascii=False, indent=2))
        except json.JSONDecodeError as e:
            print(f"\nJSON解析失败: {e}")
            print("原始响应内容:")
            print(response.text)

    except Exception as e:
        print(f"\n测试过程中出错: {e}")
        if hasattr(e, 'response'):
            print("\n错误响应详情:")
            print(e.response)
        print("\n错误类型:", type(e))
        print("错误详情:", str(e))


async def main():
    """主函数"""
    print("Gemini API 连接测试\n" + "="*50)
    print(
        f"API Key: {GEMINI_API_KEY[:5]}..." if GEMINI_API_KEY else "API Key未设置!")

    await test_gemini_api()

if __name__ == "__main__":
    asyncio.run(main())
