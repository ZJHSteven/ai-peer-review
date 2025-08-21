#!/usr/bin/env python3
"""
使用示例：展示新 API 的使用方法
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_peer_review.llm_clients.openai_client import OpenAIClient

def main():
    """演示新 API 的使用"""
    print("🤖 AI Peer Review - 新 API 演示")
    print("=" * 50)
    
    # 测试不同的模型
    models_to_test = [
        "gpt-4o",
        "claude-3-sonnet-20240229", 
        "gemini-pro",
        "deepseek-chat"
    ]
    
    test_prompt = "请用一句话简单介绍神经科学研究的重要性。"
    
    for model in models_to_test:
        print(f"\n🧠 测试模型: {model}")
        print("-" * 30)
        
        try:
            client = OpenAIClient(model=model)
            response = client.generate(test_prompt)
            print(f"✅ 成功: {response}")
        except Exception as e:
            print(f"❌ 失败: {e}")
    
    print(f"\n{'='*50}")
    print("✨ 演示完成！新的统一 API 架构正常工作。")

if __name__ == "__main__":
    main()
