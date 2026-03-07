from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Any, Iterable, Literal, Optional, Union

import yaml

from xiaogpt.utils import validate_proxy

LATEST_ASK_API = "https://userprofile.mina.mi.com/device_profile/v2/conversation?source=dialogu&hardware={hardware}&timestamp={timestamp}&limit=2"
COOKIE_TEMPLATE = "deviceId={device_id}; serviceToken={service_token}; userId={user_id}"
WAKEUP_KEYWORD = "小爱同学"

HARDWARE_COMMAND_DICT = {
    # hardware: (tts_command, wakeup_command)
    "LX06": ("5-1", "5-5"),
    "L05B": ("5-3", "5-4"),
    "S12": ("5-1", "5-5"),  # 第一代小爱，型号 MDZ-25-DA
    "S12A": ("5-1", "5-5"),
    "LX01": ("5-1", "5-5"),
    "L06A": ("5-1", "5-5"),
    "LX04": ("5-1", "5-4"),
    "L05C": ("5-3", "5-4"),
    "L17A": ("7-3", "7-4"),
    "X08E": ("7-3", "7-4"),
    "LX05A": ("5-1", "5-5"),  # 小爱红外版
    "LX5A": ("5-1", "5-5"),  # 小爱红外版
    "L07A": ("5-1", "5-5"),  # Redmi 小爱音箱 Play(l7a)
    "L15A": ("7-3", "7-4"),
    "X6A": ("7-3", "7-4"),  # 小米智能家庭屏 6
    "X10A": ("7-3", "7-4"),  # 小米智能家庭屏 10
    # add more here
}

DEFAULT_COMMAND = ("5-1", "5-5")

KEY_WORD = ("帮我", "请")
CHANGE_PROMPT_KEY_WORD = ("更改提示词",)
PROMPT = "以下请用 300 字以内回答，请只回答文字不要带链接"
# simulate_xiaoai_question
MI_ASK_SIMULATE_DATA = {
    "code": 0,
    "message": "Success",
    "data": '{"bitSet":[0,1,1],"records":[{"bitSet":[0,1,1,1,1],"answers":[{"bitSet":[0,1,1,1],"type":"TTS","tts":{"bitSet":[0,1],"text":"Fake Answer"}}],"time":1677851434593,"query":"Fake Question","requestId":"fada34f8fa0c3f408ee6761ec7391d85"}],"nextEndTime":1677849207387}',
}


@dataclass
class Config:
    hardware: str = "LX06"
    account: str = os.getenv("MI_USER", "")
    password: str = os.getenv("MI_PASS", "")
    openai_key: str = os.getenv("OPENAI_API_KEY", "")
    proxy: Optional[str] = None
    mi_did: str = os.getenv("MI_DID", "")
    keyword: Iterable[str] = KEY_WORD
    change_prompt_keyword: Iterable[str] = CHANGE_PROMPT_KEY_WORD
    prompt: str = PROMPT
    mute_xiaoai: bool = True
    bot: str = "chatgptapi"
    cookie: str = ""
    api_base: Optional[str] = None
    use_command: bool = False
    verbose: int = 0
    start_conversation: str = "开始持续对话"
    end_conversation: str = "结束持续对话"
    stream: bool = False
    tts: Literal[
        "mi", "edge", "azure", "openai", "baidu", "google", "volc", "minimax", "fish"
    ] = "mi"
    tts_options: dict[str, Any] = field(default_factory=dict)
    model_provider: str = ""
    model_name: str = ""
    mcp_servers: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Legacy bot 配置自动映射到 model_provider/model_name
        if not self.model_provider and self.bot:
            legacy_map = {
                "chatgptapi": ("openai", "gpt-4o-mini", self.openai_key, self.api_base),
                "moonshot": ("openai", "moonshot-v1-8k", os.getenv("MOONSHOT_API_KEY", ""), "https://api.moonshot.cn/v1"),
                "yi": ("openai", "yi-34b-chat-0205", os.getenv("YI_API_KEY", ""), "https://api.lingyiwanwu.com/v1"),
                "llama": ("groq", "llama3-70b-8192", os.getenv("GROQ_API_KEY", ""), None),
                "ppio": ("openai", "deepseek/deepseek-v3.2", os.getenv("PPIO_API_KEY", ""), "https://api.ppinfra.com/openai"),
                "glm": ("openai", "glm-4", os.getenv("CHATGLM_KEY", ""), "https://open.bigmodel.cn/api/paas/v4"),
                "gemini": ("google-genai", os.getenv("GEMINI_MODEL", "") or "gemini-2.5-flash-lite", os.getenv("GEMINI_KEY", ""), None),
                "qwen": ("openai", "qwen-turbo", os.getenv("DASHSCOPE_API_KEY", ""), "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                "doubao": ("openai", "skylark-chat", os.getenv("volc_api_key", ""), None),
                "langchain": ("openai", "gpt-4o-mini", self.openai_key, self.api_base),
            }
            if self.bot in legacy_map:
                provider, model, key, base = legacy_map[self.bot]
                self.model_provider = provider
                self.model_name = model
                if key:
                    self.openai_key = key
                if base and not self.api_base:
                    self.api_base = base
        if self.proxy:
            validate_proxy(self.proxy)

    @property
    def tts_command(self) -> str:
        return HARDWARE_COMMAND_DICT.get(self.hardware, DEFAULT_COMMAND)[0]

    @property
    def wakeup_command(self) -> str:
        return HARDWARE_COMMAND_DICT.get(self.hardware, DEFAULT_COMMAND)[1]

    @classmethod
    def from_options(cls, options: argparse.Namespace) -> Config:
        config_path = options.config
        if not config_path and os.path.exists("xiao_config.yaml"):
            config_path = "xiao_config.yaml"
        if not config_path:
            raise FileNotFoundError(
                "未找到配置文件。请通过 --config 指定，或在当前目录放置 xiao_config.yaml"
            )
        config = cls.read_from_file(config_path)
        return cls(**config)

    @classmethod
    def read_from_file(cls, config_path: str) -> dict:
        result = {}
        with open(config_path, "rb") as f:
            if config_path.endswith(".json"):
                config = json.load(f)
            else:
                config = yaml.safe_load(f)
            for key, value in config.items():
                if value is None:
                    continue
                if key == "keyword":
                    if not isinstance(value, list):
                        value = [value]
                    value = [kw for kw in value if kw]
                # Legacy boolean flags → bot name
                elif key == "use_chatgpt_api":
                    key, value = "bot", "chatgptapi"
                elif key == "use_glm":
                    key, value = "bot", "glm"
                elif key == "use_gemini":
                    key, value = "bot", "gemini"
                elif key == "use_qwen":
                    key, value = "bot", "qwen"
                elif key == "use_doubao":
                    key, value = "bot", "doubao"
                elif key == "use_moonshot":
                    key, value = "bot", "moonshot"
                elif key == "use_yi":
                    key, value = "bot", "yi"
                elif key == "use_llama":
                    key, value = "bot", "llama"
                elif key == "use_langchain":
                    key, value = "bot", "langchain"
                elif key == "use_ppio":
                    key, value = "bot", "ppio"
                elif key == "enable_edge_tts":
                    key, value = "tts", "edge"
                if key in cls.__dataclass_fields__:
                    result[key] = value
        return result
