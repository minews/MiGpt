from __future__ import annotations

from langchain.chat_models import init_chat_model
from rich import print

from xiaogpt.bot.base_bot import BaseBot
from xiaogpt.bot.langchain_bot import LangChainBot
from xiaogpt.config import Config


async def get_bot(config: Config) -> BaseBot:
    """Create a unified LangChainBot from config."""
    if not config.model_provider:
        raise ValueError(
            "model_provider is required. Set it directly or use a legacy bot name "
            f"(one of: chatgptapi, moonshot, yi, llama, ppio, glm, gemini, qwen, doubao)"
        )

    # 构建 init_chat_model 参数
    kwargs = {
        "model": config.model_name,
        "model_provider": config.model_provider,
    }
    # api_key: 优先使用 openai_key（legacy 映射会将各 provider key 放到这里）
    if config.openai_key:
        kwargs["api_key"] = config.openai_key
    if config.api_base:
        kwargs["base_url"] = config.api_base

    model = init_chat_model(**kwargs)

    # MCP 工具加载（可选）
    tools = None
    if config.mcp_servers:
        try:
            from langchain_mcp_adapters.client import MultiServerMCPClient

            client = MultiServerMCPClient(config.mcp_servers)
            tools = await client.get_tools()
            print(f"已加载 {len(tools)} 个 MCP 工具")
        except Exception as e:
            print(f"MCP 工具加载失败: {e}")

    return LangChainBot(
        model=model,
        system_prompt=config.prompt,
        tools=tools,
    )


__all__ = [
    "BaseBot",
    "LangChainBot",
    "get_bot",
]
