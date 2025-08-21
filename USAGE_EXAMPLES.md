# AI Peer Review 使用示例

## 不同专家数量的评审

### 场景1：4个不同专家
```bash
ai-peer-review review paper.pdf --models "gpt-4o,claude-3-sonnet,deepseek-chat,gemini-pro"
```

### 场景2：2个专家（最少配置）
```bash
ai-peer-review review paper.pdf --models "gpt-4o,claude-3-sonnet"
```

### 场景3：6个相同专家（全用 Gemini 2.5 Pro）
```bash
ai-peer-review review paper.pdf --models "gemini-2.5-pro,gemini-2.5-pro,gemini-2.5-pro,gemini-2.5-pro,gemini-2.5-pro,gemini-2.5-pro"
```

### 场景4：8个专家的大规模评审
```bash
ai-peer-review review paper.pdf --models "gpt-4o,claude-3-sonnet,gemini-2.5-pro,deepseek-chat,qwen-plus,llama-3,mistral-large,gpt-4-turbo"
```

## 元评审模型配置

当前元评审使用 `gpt-4o`，在 `src/ai_peer_review/review.py` 第177行：

```python
meta_reviewer = OpenAIClient(model="gpt-4o")  # 可以修改为任何模型
```

## 评审工作流程

1. **个人评审阶段**：每个指定的模型独立生成评审
2. **匿名化**：评审者被分配 NATO 代码（alfa, bravo, charlie...）
3. **元评审阶段**：使用指定的元评审模型整合所有评审
4. **输出**：
   - 各个模型的单独评审文件
   - 元评审文件
   - 关注点比较表（CSV格式）

## 灵活性特点

✅ **专家数量**：无限制（1个到任意多个）
✅ **模型选择**：支持任何第三方中转站支持的模型
✅ **重复模型**：可以使用相同模型多次
✅ **元评审模型**：可以自定义任何模型
✅ **配置灵活**：通过环境变量轻松配置API
