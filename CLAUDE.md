# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

xiaogpt 是一个通过 LangChain 将各种 LLM 接入小米 AI 音箱（小爱同学）的开源项目。它轮询小爱音箱的对话 API，将语音查询转发给 LLM，再通过 TTS 将回复播放到音箱上。

通过 LangChain 的 `init_chat_model()` 统一接入所有模型 provider（OpenAI、Google Gemini、Groq、以及所有 OpenAI 兼容 API 如 Moonshot、智谱、通义千问、豆包、Yi、PPIO 等），并支持通过 MCP 工具扩展。

## Commands

```shell
# 安装依赖（使用 uv）
uv sync --no-dev --frozen

# 运行（新方式，直接指定 provider 和 model）
xiaogpt --hardware LX06 --model_provider openai --model_name gpt-4o-mini

# 运行（兼容旧方式）
xiaogpt --hardware LX06 --use_chatgpt_api

# 运行（模块方式）
python -m xiaogpt

# 运行（本地开发脚本，含硬编码 DID）
python xiaogpt.py --config xiao_config.yaml

# 代码格式化（唯一的 dev 依赖是 black）
black .

# Docker 构建与运行
docker build -t xiaogpt .
docker run -e OPENAI_API_KEY=<key> xiaogpt --hardware LX06 --model_provider openai --model_name gpt-4o-mini
```

本项目没有测试套件、lint 配置和类型检查配置。

## Architecture

### 核心流程

```
[小爱音箱] --轮询API--> [MiGPT 编排器] --查询--> [LangChainBot] --流式响应--> [TTS] --播放--> [音箱]
```

### 关键模块

- **`xiaogpt/xiaogpt.py` — `MiGPT` 类**：核心编排器。登录小米账号、轮询对话 API（`poll_latest_ask`）、关键词过滤（`need_ask_gpt`）、调度 Bot 和 TTS。`chatbot` 在 `init_all_data()` 中通过 `await get_bot(config)` 异步初始化，`tts` 通过 `@functools.cached_property` 延迟初始化。主循环 `run_forever()` 与后台轮询任务通过 `asyncio.Event` 协调。

- **`xiaogpt/bot/` — Bot 子系统**：统一的 `LangChainBot` 类，通过 LangChain 的 `init_chat_model()` 支持所有模型 provider。`BaseBot`（ABC）定义接口（`ask()`、`ask_stream()`）。`get_bot(config)` 是 async 工厂函数，根据 `config.model_provider` / `config.model_name` 创建 bot 实例。对话历史用 LangChain 的 `BaseMessage` 类型管理（SystemMessage + 最近 5 轮 HumanMessage/AIMessage）。支持通过 `config.mcp_servers` 加载 MCP 工具。

- **`xiaogpt/tts/` — TTS 子系统**：`TTS`（ABC）定义 `synthesize()` 接口。三种实现：`MiTTS`（小米原生）、`TetosFileTTS`（生成 MP3 文件通过本地 HTTP 服务播放）、`TetosLiveTTS`（实时流式播放）。

- **`xiaogpt/config.py` — `Config` 数据类**：配置优先级：CLI 参数 > 默认值 > 配置文件（YAML/JSON）。核心字段 `model_provider`、`model_name`、`mcp_servers`。保留 legacy `bot` 字段，在 `__post_init__` 中自动映射到新字段。`HARDWARE_COMMAND_DICT` 映射音箱型号到 TTS/唤醒命令对。

- **`xiaogpt/cli.py`**：argparse CLI 定义和 `main()` 入口。

### 模型 Provider 配置

所有模型通过 `model_provider` + `model_name` 配置，兼容旧的 `bot=` 字段：

| Legacy `bot=` | `model_provider` | `model_name` 默认值 | `api_key` 环境变量 |
|---|---|---|---|
| `chatgptapi` | `openai` | `gpt-4o-mini` | `OPENAI_API_KEY` |
| `moonshot` | `openai` | `moonshot-v1-8k` | `MOONSHOT_API_KEY` |
| `yi` | `openai` | `yi-34b-chat-0205` | `YI_API_KEY` |
| `llama` | `groq` | `llama3-70b-8192` | `GROQ_API_KEY` |
| `ppio` | `openai` | `deepseek/deepseek-v3.2` | `PPIO_API_KEY` |
| `glm` | `openai` | `glm-4` | `CHATGLM_KEY` |
| `gemini` | `google-genai` | `gemini-2.5-flash-lite` | `GEMINI_KEY` |
| `qwen` | `openai` | `qwen-turbo` | `DASHSCOPE_API_KEY` |
| `doubao` | `openai` | `skylark-chat` | `volc_api_key` |

### 新增模型 Provider

无需新增代码。只需在配置中指定 `model_provider` 和 `model_name`：

```yaml
model_provider: openai          # 或 google-genai, groq, 或任何 LangChain 支持的 provider
model_name: your-model-name
api_base: https://custom-api.example.com/v1  # 可选，用于 OpenAI 兼容 API
```

如需 LangChain 尚未内置的 provider，安装对应的 `langchain-xxx` 包即可。

### MCP 工具扩展

在配置文件中声明 `mcp_servers` 即可自动加载 MCP 工具（需要 Python >= 3.10）：

```yaml
mcp_servers:
  - name: "weather"
    transport: "stdio"
    command: "python"
    args: ["-m", "weather_mcp_server"]
```

参考示例：`examples/mcp_config.yaml`

## Build System

- 构建后端：`hatchling` + `hatch-vcs`（版本从 git tag 派生）
- 依赖管理：`uv`（已从 PDM 迁移）
- 包索引：使用阿里云镜像 `https://mirrors.aliyun.com/pypi/simple/`
- Python 版本要求：`>=3.9, <3.13`
- 核心依赖：`langchain`、`langchain-openai`、`langchain-google-genai`、`langchain-groq`、`langchain-mcp-adapters`

## Key Conventions

- 全异步架构，基于 `asyncio`，Bot 和 TTS 的核心方法都是 async
- `get_bot()` 是 async 函数（因为 MCP 工具加载需要 await）
- 流式响应使用 `asyncio.Queue` 的生产者-消费者模式
- `xiaogpt/utils.py` 中的 `split_sentences()` 是流式文本在句子边界分割的异步生成器
- System Prompt 通过 LangChain 的 `SystemMessage` 在 Bot 初始化时设置
- 环境变量 `MI_USER`、`MI_PASS`、`MI_DID` 用于小米账号认证
- 根目录 `xiaogpt.py` 是本地开发便捷脚本，含硬编码值，不应提交敏感信息
