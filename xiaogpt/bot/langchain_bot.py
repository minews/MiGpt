"""Unified LangChain bot supporting all model providers."""
from __future__ import annotations

from typing import Any, AsyncGenerator, List, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from rich import print

from xiaogpt.bot.base_bot import BaseBot
from xiaogpt.utils import split_sentences


class LangChainBot(BaseBot):
    """Unified bot that delegates to any LangChain chat model."""

    name = "LangChain"
    MAX_HISTORY = 5  # 保留最近 N 轮对话（不含 system message）

    def __init__(
        self,
        model,
        system_prompt: str = "",
        tools: Optional[List] = None,
    ) -> None:
        self.model = model.bind_tools(tools) if tools else model
        self.system_prompt = system_prompt
        self.history: List[BaseMessage] = []
        if system_prompt:
            self.history.append(SystemMessage(content=system_prompt))

    def _build_messages(self, query: str) -> List[BaseMessage]:
        messages = list(self.history)
        messages.append(HumanMessage(content=query))
        return messages

    def _trim_history(self) -> None:
        """保留 system message + 最近 MAX_HISTORY 轮对话。"""
        sys_msgs = [m for m in self.history if isinstance(m, SystemMessage)]
        conv_msgs = [m for m in self.history if not isinstance(m, SystemMessage)]
        self.history = sys_msgs + conv_msgs[-(self.MAX_HISTORY * 2) :]

    def has_history(self) -> bool:
        return any(not isinstance(m, SystemMessage) for m in self.history)

    def change_prompt(self, new_prompt: str) -> None:
        self.history = [m for m in self.history if not isinstance(m, SystemMessage)]
        if new_prompt:
            self.history.insert(0, SystemMessage(content=new_prompt))
        self.system_prompt = new_prompt

    async def ask(self, query: str, **options: Any) -> str:
        messages = self._build_messages(query)
        try:
            response = await self.model.ainvoke(messages)
        except Exception as e:
            print(str(e))
            return ""
        content = response.content
        self.history.append(HumanMessage(content=query))
        self.history.append(AIMessage(content=content))
        self._trim_history()
        print(content)
        return content

    async def ask_stream(self, query: str, **options: Any) -> AsyncGenerator[str, None]:
        messages = self._build_messages(query)
        try:
            astream = self.model.astream(messages)
        except Exception as e:
            print(str(e))
            return

        async def text_gen():
            async for chunk in astream:
                if chunk.content:
                    print(chunk.content, end="")
                    yield chunk.content

        full_content = ""
        try:
            async for sentence in split_sentences(text_gen()):
                full_content += sentence
                yield sentence
        finally:
            print()
            self.history.append(HumanMessage(content=query))
            self.history.append(AIMessage(content=full_content))
            self._trim_history()
