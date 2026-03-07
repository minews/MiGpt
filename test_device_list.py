import asyncio
import json
import yaml
import aiohttp

from xiaogpt.miservice.miaccount import MiAccount
from xiaogpt.miservice.minaservice import MiNAService


async def main():
    with open("xiao_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    cookie = config.get("cookie", "")
    account = config.get("account", "")
    password = config.get("password", "")

    if not cookie:
        print("xiao_config.yaml 中未配置 cookie")
        return

    async with aiohttp.ClientSession() as session:
        mi_account = MiAccount(
            session=session,
            username=account,
            password=password,
            cookie=cookie,
        )
        mina_service = MiNAService(mi_account)

        print("正在获取设备列表...")
        devices = await mina_service.device_list()

        if devices is None:
            print("请求失败，返回 None")
        elif not devices:
            print("设备列表为空")
        else:
            print(f"共找到 {len(devices)} 台设备：")
            arr = []
            for device in devices:
                arr.append({"name": device["name"], "mi_did": device["miotDID"],"hardware":device["hardware"]})

            print(json.dumps(arr, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
