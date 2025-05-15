# AI Peer Review

This package facilitates AI-based peer review of academic papers, particularly in neuroscience. It uses multiple large language models (LLMs) to generate independent reviews of a paper, and then creates a meta-review summarizing the key points.

## Features

- Submit papers for review by multiple LLMs
- Generate individual peer reviews from various models
- Create a meta-review analyzing common themes and unique insights
- Generate a concerns table identifying which model found each concern
- Store results in markdown, CSV, and JSON formats

## Supported Models

- GPT-4o (via OpenAI API)
- GPT-4o-mini (via OpenAI API)
- Claude 3.7 Sonnet (via Anthropic API)
- Google Gemini 2.5 Pro (via Google AI API)
- DeepSeek R1 (via Together API)
- Llama 4 Maverick (via Together API)

## Installation

```bash
# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Usage

### API Keys

You can set API keys in two ways:

#### Using the CLI config command

```bash
# Set API keys (recommended)
ai-peer-review config openai "your-openai-key"
ai-peer-review config anthropic "your-anthropic-key"
ai-peer-review config google "your-google-key"
ai-peer-review config together "your-together-ai-key"  # Used for DeepSeek R1 and Llama 4 Maverick
```

Keys are stored in `~/.ai-peer-review/config.json`.

#### Using environment variables

Alternatively, you can set environment variables either by exporting them or by using a `.env` file:

**Option 1: Export variables in your shell:**

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"
export TOGETHER_API_KEY="your-together-ai-key"  # Used for DeepSeek R1 and Llama 4 Maverick
```

**Option 2: Create a .env file:**

Copy the `.env.example` file to `.env` and fill in your API keys:

```bash
cp .env.example .env
# Edit the .env file with your API keys
```

You can place the `.env` file in:
- The current working directory
- Your home directory at `~/.ai-peer-review/.env`

### Command Line Interface

Review a paper with all available models:

```bash
ai-peer-review review path/to/paper.pdf
```

Specify specific models to use:

```bash
ai-peer-review review path/to/paper.pdf --models "gpt4-o1,claude-3.7-sonnet"
```

Specify output directory:

```bash
ai-peer-review review path/to/paper.pdf --output-dir ./my_reviews
```

Skip meta-review generation:

```bash
ai-peer-review review path/to/paper.pdf --no-meta-review
```

## Outputs

The tool generates the following outputs in the specified directory (default: `./papers/[paper-name]`):

- `review_[model-name].md` - Individual reviews from each LLM
- `meta_review.md` - Summary and analysis of all reviews
- `concerns_table.csv` - CSV file with concerns identified by each model
- `results.json` - Structured data containing all reviews, meta-review, and reviewer-to-model mapping