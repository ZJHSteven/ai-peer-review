#!/usr/bin/env python3
"""
调试脚本：测试不同模型名称的API请求
用于验证 yunwu.ai 代理是否有模型映射问题
"""

import os
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_model_request(model_name: str):
    """测试特定模型的API请求"""
    api_key = os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("BASE_URL") or os.getenv("OPENAI_BASE_URL", "https://yunwu.ai/v1")
    
    if not base_url.endswith("/chat/completions"):
        if base_url.endswith("/"):
            base_url += "chat/completions"
        else:
            base_url += "/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": "你是一个测试助手。"},
            {"role": "user", "content": "请简单回答：你正在使用的模型名称是什么？"}
        ],
        "temperature": 0.1,
        "max_tokens": 100
    }
    
    print(f"\n=== 测试模型: {model_name} ===")
    print(f"请求URL: {base_url}")
    print(f"请求数据中的模型名称: {model_name}")
    
    try:
        response = requests.post(base_url, headers=headers, json=data, timeout=30)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and result["choices"]:
                content = result["choices"][0]["message"]["content"]
                print(f"API响应内容: {content}")
                
                # 如果API返回了使用的模型信息，打印出来
                if "model" in result:
                    print(f"API响应中的模型字段: {result['model']}")
            else:
                print(f"响应格式异常: {result}")
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"请求异常: {e}")

def main():
    """主函数：测试多个模型"""
    test_models = [
        "gpt-5-2025-08-07",    # 你期望的模型
        "gpt-4o",              # 你在日志中看到的模型
        "o3-2025-04-16",       # 另一个测试模型
        "claude-3-7-sonnet-20250219-thinking",  # 非OpenAI模型
    ]
    
    print("开始测试模型映射问题...")
    print("=" * 50)
    
    for model in test_models:
        test_model_request(model)
    
    print("\n" + "=" * 50)
    print("测试完成。请检查以上结果，看是否存在模型映射问题。")
    print("如果请求的模型和实际使用的模型不一致，说明 yunwu.ai 存在模型映射。")

if __name__ == "__main__":
    main()
