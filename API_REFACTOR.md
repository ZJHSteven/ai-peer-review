# API 重构说明

## 重大更改

我们已经将所有 LLM 客户端从 SDK 模式改为直接 JSON 请求模式，现在所有模型都使用 OpenAI 兼容的 API 格式通过第三方中转站。

### 主要变化

1. **统一 API 格式**: 所有模型现在都使用 OpenAI 的 `/chat/completions` API 格式
2. **环境变量配置**: API 密钥和基础 URL 通过 `.env` 文件配置
3. **简化架构**: 所有客户端继承自统一的 `BaseLLMClient`
4. **动态模型支持**: 支持任何模型名称，不再限制为预定义模型

### 环境变量配置

在项目根目录的 `.env` 文件中配置：

```env
# OpenAI API Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://yunwu.ai/v1

# Alternative environment variable names for compatibility
API_KEY=your-api-key-here
BASE_URL=https://yunwu.ai/v1
```

### 使用示例

```python
from ai_peer_review.llm_clients.openai_client import OpenAIClient

# 创建客户端 - 支持任何模型名称
client = OpenAIClient(model="gpt-4o")
response = client.generate("你好，请介绍一下自己")

# 使用其他模型
claude_client = OpenAIClient(model="claude-3-sonnet-20240229")
gemini_client = OpenAIClient(model="gemini-pro")
deepseek_client = OpenAIClient(model="deepseek-chat")
```

### CLI 使用

```bash
# 使用任何支持的模型进行评审
ai-peer-review review paper.pdf --models gpt-4o claude-3-sonnet-20240229 gemini-pro

# 所有模型都会通过同一个 API 端点进行请求
```

### 架构优势

1. **灵活性**: 支持第三方中转站支持的任何模型
2. **一致性**: 所有模型使用相同的 API 接口
3. **可维护性**: 代码结构更简单，易于维护
4. **可扩展性**: 新增模型无需修改代码

### 注意事项

- `.env` 文件已添加到 `.gitignore`，确保 API 密钥不会泄露
- 原有的 SDK 依赖已不再使用，但保留在依赖列表中以保持兼容性
- 测试需要更新以反映新的架构
