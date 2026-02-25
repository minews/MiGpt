from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, TypeVar

from xiaogpt.config import Config

T = TypeVar("T", bound="BaseBot")


class BaseBot(ABC):
    name: str

    @abstractmethod
    async def ask(self, query: str, **options: Any) -> str:
        pass

    @abstractmethod
    async def ask_stream(self, query: str, **options: Any) -> AsyncGenerator[str, None]:
        pass

    @abstractmethod
    def has_history(self) -> bool:
        pass

    @abstractmethod
    def change_prompt(self, new_prompt: str) -> None:
        pass
