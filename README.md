# xiaogpt

[![PyPI](https://img.shields.io/pypi/v/xiaogpt?style=flat-square)](https://pypi.org/project/xiaogpt)
[![Docker Image Version (latest by date)](https://img.shields.io/docker/v/yihong0618/xiaogpt?color=%23086DCD&label=docker%20image)](https://hub.docker.com/r/yihong0618/xiaogpt)

<https://user-images.githubusercontent.com/15976103/226803357-72f87a41-a15b-409e-94f5-e2d262eecd53.mp4>

Play ChatGPT and other LLM with Xiaomi AI Speaker

![image](https://user-images.githubusercontent.com/15976103/220028375-c193a859-48a1-4270-95b6-ef540e54a621.png)
![image](https://user-images.githubusercontent.com/15976103/226802344-9c71f543-b73c-4a47-8703-4c200c434dec.png)

## 支持的 AI 类型

通过 [LangChain](https://python.langchain.com/) 统一接入，支持以下 provider：

| Provider | `model_provider` | 默认模型 | API Key 环境变量 |
|---|---|---|---|
| [OpenAI](https://platform.openai.com/) | `openai` | `gpt-4o-mini` | `OPENAI_API_KEY` |
| [Google Gemini](https://makersuite.google.com/app/apikey) | `google-genai` | `gemini-2.5-flash-lite` | `GEMINI_KEY` |
| [Groq (Llama3)](https://console.groq.com/docs/quickstart) | `groq` | `llama3-70b-8192` | `GROQ_API_KEY` |
| [Moonshot](https://platform.moonshot.cn/) | `openai` | `moonshot-v1-8k` | `MOONSHOT_API_KEY` |
| [ChatGLM](http://open.bigmodel.cn/) | `openai` | `glm-4` | `CHATGLM_KEY` |
| [通义千问](https://help.aliyun.com/zh/dashscope/) | `openai` | `qwen-turbo` | `DASHSCOPE_API_KEY` |
| [01万物](https://platform.lingyiwanwu.com/apikeys) | `openai` | `yi-34b-chat-0205` | `YI_API_KEY` |
| [豆包](https://console.volcengine.com/) | `openai` | `skylark-chat` | `volc_api_key` |
| [PPIO (DeepSeek)](https://api.ppinfra.com/) | `openai` | `deepseek/deepseek-v3.2` | `PPIO_API_KEY` |

> 任何 OpenAI 兼容的 API 服务都可以通过 `model_provider: openai` + `api_base` 接入。
> 旧版 `bot=chatgptapi` 等配置仍然兼容，会自动映射到对应的 provider。

## Python 版本支持

- **主分支**: Python >= 3.9
- **Python 3.8 分支**: `python38-support`（使用 LangChain 0.2.x）

### Python 3.8 用户安装

```bash
# 克隆 Python 3.8 专用分支
git clone -b python38-support https://github.com/minews/MiGpt.git xiaogpt
cd xiaogpt

# 安装依赖（使用 uv）
uv python pin 3.8
uv venv
uv sync --no-dev

# 运行
uv run python -m xiaogpt --config xiao_config.yaml
```

注意：Python 3.8 分支使用 LangChain 0.2.x，部分新功能（如 MCP 工具）需要 Python >= 3.10。

## 获取小米音响 DID

| 系统和 Shell   | Linux *sh                                      | Windows CMD 用户                        | Windows PowerShell 用户                         |
| ------------- | ---------------------------------------------- | -------------------------------------- | ---------------------------------------------- |
| 1、安装包     | `pip install miservice_fork`                   | `pip install miservice_fork`           | `pip install miservice_fork`                   |
| 2、设置变量   | `export MI_USER=xxx` <br> `export MI_PASS=xxx` | `set MI_USER=xxx`<br>`set MI_PASS=xxx` | `$env:MI_USER="xxx"` <br> `$env:MI_PASS="xxx"` |
| 3、取得 MI_DID | `micli list`                                   | `micli list`                           | `micli list`                                   |
| 4、设置 MI_DID | `export MI_DID=xxx`                            | `set MI_DID=xxx`                       | `$env:MI_DID="xxx"`                            |

- 注意不同 shell 对环境变量的处理是不同的，尤其是 powershell 赋值时，可能需要双引号来包括值。
- 如果获取 did 报错时，请更换一下无线网络，有很大概率解决问题。

## 一点原理

[不用 root 使用小爱同学和 ChatGPT 交互折腾记](https://github.com/yihong0618/gitblog/issues/258)

## 准备

1. LLM API Key（OpenAI / Gemini / Groq 等任一即可）
2. 小爱音响
3. 能正常联网的环境或 proxy
4. Python 3.8+（主分支需要 3.9+，Python 3.8 请使用 `python38-support` 分支）

## 使用

- `pip install -U --force-reinstall xiaogpt`
- 参考我 fork 的 [MiService](https://github.com/yihong0618/MiService) 项目 README 并在本地 terminal 跑 `micli list` 拿到你音响的 DID 成功 **别忘了设置 export MI_DID=xxx** 这个 MI_DID 用
- run `xiaogpt --hardware ${your_hardware} --model_provider openai --model_name gpt-4o-mini` hardware 你看小爱屁股上有型号，输入进来，如果在屁股上找不到或者型号不对，可以用 `micli mina` 找到型号
- 跑起来之后就可以问小爱同学问题了，”帮我”开头的问题，会发送一份给 LLM 然后小爱同学用 tts 回答
- 如果上面不可用，可以尝试用手机抓包，<https://userprofile.mina.mi.com/device_profile/v2/conversation> 找到 cookie 利用 `--cookie '${cookie}'` cookie 别忘了用单引号包裹
- 默认用目前 ubus, 如果你的设备不支持 ubus 可以使用 `--use_command` 来使用 command 来 tts
- 使用 `--mute_xiaoai` 选项，可以快速停掉小爱的回答
- 使用 `--account ${account} --password ${password}`
- 如果有能力可以自行替换唤醒词，也可以去掉唤醒词
- 如果你遇到了墙需要用 Cloudflare Workers 替换 api_base 请使用 `--api_base ${url}` 来替换。 **请注意，此处你输入的 api 应该是'`https://xxxx/v1`'的字样，域名需要用引号包裹**
- 可以跟小爱说 `开始持续对话` 自动进入持续对话状态，`结束持续对话` 结束持续对话状态。
- 可以使用 `--tts edge` 来获取更好的 tts 能力
- 可以使用 `--tts fish --fish_api_key <your-fish-key> --fish_voice_key <fish-voice>` 来获取 [fish-audio](https://fish.audio/) 能力 (如何获取 fish voice 见下)
- 可以使用 `--tts openai` 来获取 openai tts 能力
- 可以使用 `--tts azure --azure_tts_speech_key <your-speech-key>` 来获取 Azure TTS 能力

### 新配置方式（推荐）

通过 `--model_provider` 和 `--model_name` 直接指定模型：

```shell
# OpenAI
export OPENAI_API_KEY=${your_api_key}
xiaogpt --hardware LX06 --model_provider openai --model_name gpt-4o-mini --mute_xiaoai --stream

# Google Gemini
export GEMINI_KEY=${your_gemini_key}
xiaogpt --hardware LX06 --model_provider google-genai --model_name gemini-2.5-flash-lite --mute_xiaoai --stream

# Groq (Llama3)
export GROQ_API_KEY=${your_groq_key}
xiaogpt --hardware LX06 --model_provider groq --model_name llama3-70b-8192 --mute_xiaoai --stream

# Moonshot (OpenAI 兼容)
export MOONSHOT_API_KEY=${your_moonshot_key}
xiaogpt --hardware LX06 --model_provider openai --model_name moonshot-v1-8k --api_base https://api.moonshot.cn/v1 --mute_xiaoai --stream

# DeepSeek via PPIO
export PPIO_API_KEY=${your_ppio_key}
xiaogpt --hardware LX06 --model_provider openai --model_name deepseek/deepseek-v3.2 --api_base https://api.ppinfra.com/openai --mute_xiaoai --stream
```

### 兼容旧配置

旧的 `--use_chatgpt_api`、`--use_gemini` 等参数仍然有效，会自动映射到对应的 provider：

```shell
export OPENAI_API_KEY=${your_api_key}
xiaogpt --hardware LX06 --use_chatgpt_api
# or
xiaogpt --hardware LX06 --cookie ${cookie} --use_chatgpt_api
# 如果你想直接输入账号密码
xiaogpt --hardware LX06 --account ${your_xiaomi_account} --password ${your_password} --use_chatgpt_api
# 如果你想 mute 小米的回答
xiaogpt --hardware LX06  --mute_xiaoai --use_chatgpt_api
# 使用流式响应，获得更快的响应
xiaogpt --hardware LX06  --mute_xiaoai --stream
# 如果你想使用 google 的 gemini
xiaogpt --hardware LX06  --mute_xiaoai --use_gemini --gemini_key ${gemini_key}
# 如果你想使用阿里的通义千问
xiaogpt --hardware LX06  --mute_xiaoai --use_qwen --qwen_key ${qwen_key}
# 如果你想使用 kimi
xiaogpt --hardware LX06  --mute_xiaoai --use_moonshot_api --moonshot_api_key ${moonshot_api_key}
# 如果你想使用 llama3
xiaogpt --hardware LX06  --mute_xiaoai --use_llama --llama_api_key ${llama_api_key}
```

## config.yaml

如果想通过单一配置文件启动也是可以的，可以通过 `--config` 参数指定配置文件，config 文件必须是合法的 Yaml 或 JSON 格式
参数优先级

- cli args > default > config

```shell
python3 xiaogpt.py --config xiao_config.yaml
# or
xiaogpt --config xiao_config.yaml
```

配置文件示例（新方式）：

```yaml
hardware: LX06
account: ""
password: ""
stream: true
mute_xiaoai: true

# 直接指定 provider 和 model
model_provider: openai
model_name: gpt-4o-mini
# openai_key: ""  # 或设置环境变量 OPENAI_API_KEY
```

## MCP 工具（可选）

xiaogpt 支持通过 [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 为 LLM 添加工具能力。在配置文件中声明 `mcp_servers` 即可自动加载。

> 需要 Python >= 3.10

```yaml
mcp_servers:
  # 本地 stdio 类型的 MCP server
  - name: "weather"
    transport: "stdio"
    command: "python"
    args: ["-m", "weather_mcp_server"]

  # 远程 SSE 类型的 MCP server
  - name: "home_control"
    transport: "sse"
    url: "http://localhost:8080/sse"
```

## 配置项说明

### 模型配置（新方式，推荐）

| 参数 | 说明 | 默认值 |
|---|---|---|
| model_provider | LangChain 模型 provider | 由 `bot` 自动映射 |
| model_name | 模型名称 | 由 `bot` 自动映射 |
| api_base | 自定义 API 端点 URL |  |
| openai_key | API Key（所有 provider 通用） | 环境变量 `OPENAI_API_KEY` |

### MCP 工具配置

| 参数 | 说明 | 默认值 |
|---|---|---|
| mcp_servers | MCP Server 列表，见 [MCP 工具](#mcp-工具可选) | `[]` |

### 设备和通用配置

| 参数 | 说明 | 默认值 | 可选值 |
|---|---|---|---|
| hardware | 设备型号 |  |  |
| account | 小爱账户 |  |  |
| password | 小爱账户密码 |  |  |
| cookie | 小爱账户 cookie（如果用密码登录可以不填） |  |  |
| mi_did | 设备 did |  |  |
| use_command | 使用 MI command 与小爱交互 | `false` |  |
| mute_xiaoai | 快速停掉小爱自己的回答 | `true` |  |
| verbose | 是否打印详细日志 | `false` |  |
| tts | 使用的 TTS 类型 | `mi` | `edge`、`openai`、`azure`、`volc`、`baidu`、`google`、`minimax`、`fish` |
| tts_options | TTS 参数字典，参考 [tetos](https://github.com/frostming/tetos) | `{}` |  |
| prompt | 自定义 prompt | `请用300字以内回答` |  |
| keyword | 自定义请求词列表 | `["帮我", "请"]` |  |
| change_prompt_keyword | 更改提示词触发列表 | `["更改提示词"]` |  |
| start_conversation | 开始持续对话关键词 | `开始持续对话` |  |
| end_conversation | 结束持续对话关键词 | `结束持续对话` |  |
| stream | 使用流式响应 | `false` |  |
| proxy | HTTP 代理 URL | `""` |  |


## 注意

1. 请开启小爱同学的蓝牙
2. 如果要更改提示词和 PROMPT 在代码最上面自行更改
3. 目前已知 LX04、X10A 和 L05B L05C 可能需要使用 `--use_command`，否则可能会出现终端能输出 GPT 的回复但小爱同学不回答 GPT 的情况。这几个型号也只支持小爱原本的 tts.
4. 在 wsl 使用时，需要设置代理为 <http://wls 的 ip:port(vpn 的代理端口)>, 否则会出现连接超时的情况，详情 [报错：Error communicating with OpenAI](https://github.com/yihong0618/xiaogpt/issues/235)

## QA

1. 用破解么？不用
2. 你做这玩意也没用啊？确实。。。但是挺好玩的，有用对你来说没用，对我们来说不一定呀
3. 想把它变得更好？PR Issue always welcome.
4. 还有问题？提 Issue 哈哈
5. Exception: Error <https://api2.mina.mi.com/admin/v2/device_list?master=0&requestId=app_ios_xxx>: Login failed [@KJZH001](https://github.com/KJZH001)<br>
   这是由于小米风控导致，海外地区无法登录大陆的账户，请尝试 cookie 登录
   无法抓包的可以在本地部署完毕项目后再用户文件夹`C:\Users\用户名`下面找到.mi.token，然后扔到你无法登录的服务器去<br>
   若是 linux 则请放到当前用户的 home 文件夹，此时你可以重新执行先前的命令，不出意外即可正常登录（但 cookie 可能会过一段时间失效，需要重新获取）<br>
   详情请见 [https://github.com/yihong0618/xiaogpt/issues/332](https://github.com/yihong0618/xiaogpt/issues/332)

## 视频教程

<https://www.youtube.com/watch?v=K4YA8YwzOOA>

## Docker

### 常规用法

X86/ARM Docker Image: `yihong0618/xiaogpt`

```shell
docker run -e OPENAI_API_KEY=<your-openapi-key> yihong0618/xiaogpt <命令行参数>
```

如

```shell
docker run -e OPENAI_API_KEY=<your-openapi-key> yihong0618/xiaogpt --account=<your-xiaomi-account> --password=<your-xiaomi-password> --hardware=<your-xiaomi-hardware> --use_chatgpt_api
```

### 使用配置文件

xiaogpt 的配置文件可通过指定 volume /config，以及指定参数--config 来处理，如

```shell
docker run -v <your-config-dir>:/config yihong0618/xiaogpt --config=/config/config.yaml
```

### 网络使用 host 模型

```shell
docker run -v <your-config-dir>:/config --network=host yihong0618/xiaogpt --config=/config/config.yaml
```

### 本地编译 Docker Image

```shell
 docker build -t xiaogpt .
```

如果在安装依赖时构建失败或安装缓慢时，可以在构建 Docker 镜像时使用 `--build-arg` 参数来指定国内源地址：

```sh
docker build --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple -t xiaogpt .
```

如果需要在 Apple M1/M2上编译x86

```shell
 docker buildx build --platform=linux/amd64 -t xiaogpt-x86 .
```

### 第三方 TTS

我们目前支持是三种第三方 TTS：edge/openai/azure/volc/baidu/google

[edge-tts](https://github.com/rany2/edge-tts) 提供了类似微软 tts 的能力
[azure-tts](https://techcommunity.microsoft.com/t5/ai-azure-ai-services-blog/9-more-realistic-ai-voices-for-conversations-now-generally/ba-p/4099471) 提供了微软 azure tts 的能力
[openai-tts](https://platform.openai.com/docs/guides/text-to-speech) 提供了类似 openai tts 的能力
[fish-tts](https://fish.audio/) 提供了 fish tts 的能力

#### Usage

你可以通过参数 `tts`, 来启用它

```yaml
tts: edge
```

For edge 查看更多语言支持，从中选择一个

```shell
edge-tts --list-voices
```

#### 如果你想使用 [fish-tts](https://fish.audio/)

1. 注册 https://fish.audio/zh-CN/go-api/ 拿到 api key
2. 选择你想要的声音自建声音或者使用热门声音  https://fish.audio/zh-CN/text-to-speech/?modelId=e80ea225770f42f79d50aa98be3cedfc 其中 `e80ea225770f42f79d50aa98be3cedfc` 就声音的 key id
3. python3 xiaogpt.py --hardware LX06 --account xxxx --password xxxxx --use_chatgpt_api --mute_xiaoai --stream --tts fish --fish_api_key xxxxx --fish_voice_key xxxxx
4. 或者在 xiao_config.yaml 中配置

```yaml
tts: fish 
# TTS 参数字典，参考 https://github.com/frostming/tetos 获取可用参数
tts_options: {
    "api_key": "xxxxx",
    "voice": "xxxxxx"
}

``` 

#### 在容器中使用 edge-tts/azure-tts/openai-tts/volc/google/baidu/fish

由于 Edge TTS 启动了一个本地的 HTTP 服务，所以需要将容器的端口映射到宿主机上，并且指定本地机器的 hostname:

```shell
docker run -v <your-config-dir>:/config -p 9527:9527 -e XIAOGPT_HOSTNAME=<your ip> yihong0618/xiaogpt --config=/config/config.yaml
```

注意端口必须映射为与容器内一致，XIAOGPT_HOSTNAME 需要设置为宿主机的 IP 地址，否则小爱无法正常播放语音。

## 推荐的类似项目

- [XiaoBot](https://github.com/longbai/xiaobot) -> Go 语言版本的 Fork, 带支持不同平台的 UI
- [MiGPT](https://github.com/idootop/mi-gpt) -> Node.js 版，支持流式响应和长短期记忆

## 感谢

- [xiaomi](https://www.mi.com/)
- [LangChain](https://python.langchain.com/) 统一模型接入
- [Tetos](https://github.com/frostming/tetos) TTS 云服务支持
- @[Yonsm](https://github.com/Yonsm) 的 [MiService](https://github.com/Yonsm/MiService)
- @[pjq](https://github.com/pjq) 给了这个项目非常多的帮助
- @[frostming](https://github.com/frostming) 重构了一些代码，支持了`持续会话功能`

## 赞赏

谢谢就够了
