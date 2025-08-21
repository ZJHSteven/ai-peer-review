# 《学位与研究生教育》期刊AI审稿系统使用指南

## 目录
1. [系统概述](#系统概述)
2. [定制特色](#定制特色)
3. [快速开始](#快速开始)
4. [详细使用](#详细使用)
5. [配置说明](#配置说明)
6. [输出解读](#输出解读)
7. [常见问题](#常见问题)

## 系统概述

本AI审稿系统专门为《学位与研究生教育》期刊定制开发，基于该期刊的投稿须知、审稿标准和栏目特色，提供专业的智能同行评审服务。

### 核心功能
- **多模型协同审稿**：支持GPT-4、Claude、DeepSeek、Gemini等多个大语言模型
- **专业评审标准**：严格按照期刊审稿五维度标准评估
- **智能栏目匹配**：自动识别论文最适合的期刊栏目
- **元评审生成**：综合多个模型意见，生成专业元评审报告
- **问题汇总表**：结构化输出审稿关注问题

## 定制特色

### 1. 期刊专业定位
- 服务于学位制度建设和研究生教育事业
- 覆盖工作指导、理论研究、经验介绍、信息传播
- 适配期刊11个主要栏目的特定要求

### 2. 五维度审稿标准
| 维度 | 权重 | 评估要点 |
|------|------|----------|
| 选题价值与期刊契合度 | 25% | 问题重要性、期刊匹配度、栏目适配性 |
| 学术质量与创新性 | 25% | 理论创新、实践价值、方法新颖性 |
| 学术规范性 | 20% | 学术道德、引用规范、数据真实性 |
| 写作质量与形式规范 | 15% | 文风简洁、格式规范、篇幅适中 |
| 研究方法与论证质量 | 15% | 方法科学、论证严密、结论可靠 |

### 3. 严格格式要求
- 篇幅控制：10000汉字以内
- 摘要要求：300-500字，包含目的、方法、结果、结论
- 关键词：3-5个准确关键词
- 参考文献：符合GB/T7714-2015国家标准

## 快速开始

### 环境准备
```bash
# 1. 确保Python环境已配置
python --version  # 需要Python 3.8+

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置API密钥（根据使用的模型）
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
# 或在.env文件中配置
```

### 简单使用
```bash
# 使用基础配置审稿
python degree_education_review.py your_paper.pdf

# 指定输出目录
python degree_education_review.py your_paper.pdf my_review_output
```

### Python代码使用
```python
from ai_peer_review.review import process_paper, generate_meta_review

# 基础审稿
reviews = process_paper(
    pdf_path="paper.pdf",
    models=["gpt-4o", "claude-3-sonnet"],
    config_file="configs/degree_education_journal.json"
)

# 生成元评审
meta_review, mapping = generate_meta_review(
    reviews=reviews,
    config_file="configs/degree_education_journal.json"
)
```

## 详细使用

### 配置文件选择
系统提供两个配置文件：

1. **基础配置** (`degree_education_journal.json`)
   - 适合一般审稿需求
   - 包含核心提示词和标准

2. **详细配置** (`degree_education_journal_detailed.json`)
   - 包含详细的栏目信息
   - 提供评分标准和权重
   - 适合精细化审稿需求

### 模型选择建议
```python
# 推荐模型组合
models = [
    "gpt-4o",           # OpenAI最新模型，理解力强
    "claude-3-sonnet",  # Anthropic模型，分析深入
    "deepseek-chat",    # DeepSeek模型，中文优化
    "gemini-pro"        # Google模型，多角度分析
]
```

### 批量审稿
```python
import glob
from pathlib import Path

# 批量处理多个论文
pdf_files = glob.glob("papers/*.pdf")
for pdf_file in pdf_files:
    output_dir = f"reviews/{Path(pdf_file).stem}"
    review_paper_for_degree_education_journal(pdf_file, output_dir)
```

## 配置说明

### 提示词定制
配置文件中的三个核心提示词：

1. **system**: 设定AI的专家身份和背景
2. **review**: 详细的审稿指导和评估标准
3. **metareview**: 元评审生成的指导原则

### 栏目适配
系统自动识别论文适合的栏目：
- 专题研究：重大理论实践问题
- 学术探索：前沿理论探讨
- 导师论坛：培养经验心得
- 研究生培养：培养模式机制
- 研究生教学：课程教学改革
- 研究生管理：管理制度创新
- 研究生德育：思政教育方法
- 招生与就业：政策机制研究
- 评估与质量保障：质量体系建设
- 学科建设与发展：建设发展战略
- 比较与借鉴：国际经验分析

## 输出解读

### 独立评审报告
每个模型生成的独立评审包含：
```
一、论文概述
二、栏目适配性分析
三、各维度详细评析
四、主要优点和创新之处
五、存在问题和改进建议
六、审稿结论
```

### 元评审报告
综合所有模型意见的元评审包含：
```
1. 评审意见综合分析
2. 期刊标准符合度评估
3. 主要问题优先级排序
4. 修改指导建议
5. 编辑决策建议
```

### 关注问题汇总表 (CSV)
结构化的问题清单，包含：
- 问题描述
- 问题类别
- 严重程度
- 各模型识别情况

## 常见问题

### Q1: 如何选择合适的模型？
**A:** 建议使用4个不同的模型以获得多角度评审。GPT-4o适合综合分析，Claude适合深度思考，DeepSeek对中文友好，Gemini提供独特视角。

### Q2: 审稿结果如何理解？
**A:** 系统提供四级审稿建议：
- **接受发表**：无重大问题，符合期刊标准
- **修改后接受**：有一般问题，修改后可发表
- **修改后重审**：有重要问题，需大幅修改
- **拒稿**：有重大问题或不符合期刊定位

### Q3: 可以自定义评审标准吗？
**A:** 可以。修改配置文件中的`prompts`部分，调整评审维度和权重。

### Q4: 系统支持哪些文件格式？
**A:** 目前支持PDF格式的论文文件。确保PDF文档清晰、文字可提取。

### Q5: 如何处理API限制？
**A:** 
- 设置合理的请求间隔
- 监控API使用量
- 考虑使用多个API key轮替

### Q6: 审稿结果的可靠性如何？
**A:** AI审稿作为辅助工具，可以提供全面的形式检查和初步评估，但最终决策应结合人工专家判断。

## 技术支持

如遇到技术问题，请检查：
1. Python环境和依赖包是否正确安装
2. API密钥是否正确配置
3. PDF文件是否可正常读取
4. 网络连接是否稳定

更多技术问题请参考项目文档或提交issue。
