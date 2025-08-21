#!/usr/bin/env python3
"""
测试脚本：验证新的API接口是否工作正常
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_peer_review.llm_clients.openai_client import OpenAIClient

def test_api_connection():
    """测试API连接"""
    try:
        # 测试不同的模型
        test_models = ["gpt-4o", "claude-3-sonnet-20240229", "gemini-pro"]
        
        for model in test_models:
            print(f"\n测试模型: {model}")
            try:
                client = OpenAIClient(model=model)
                response = client.generate("请用一句话介绍自己。")
                print(f"✅ 成功 - 响应: {response[:100]}...")
            except Exception as e:
                print(f"❌ 失败 - {e}")
                
    except Exception as e:
        print(f"整体测试失败: {e}")

if __name__ == "__main__":
    test_api_connection()
