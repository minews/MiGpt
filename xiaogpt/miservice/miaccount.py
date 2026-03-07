import base64
import hashlib
import json
import logging
import os
import random
import string
from urllib import parse
from aiohttp import ClientSession

_LOGGER = logging.getLogger(__package__)

# 固定的 User-Agent 列表，随机选择一个
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]

def get_random_ua():
    """获取随机 User-Agent"""
    return random.choice(USER_AGENTS)


def get_random(length):
    return "".join(random.sample(string.ascii_letters + string.digits, length))


class MiTokenStore:
    def __init__(self, token_path):
        self.token_path = token_path

    def load_token(self):
        if os.path.isfile(self.token_path):
            try:
                with open(self.token_path) as f:
                    return json.load(f)
            except Exception:
                _LOGGER.exception("Exception on load token from %s", self.token_path)
        return None

    def save_token(self, token=None):
        if token:
            try:
                with open(self.token_path, "w") as f:
                    json.dump(token, f, indent=2)
            except Exception:
                _LOGGER.exception("Exception on save token to %s", self.token_path)
        elif os.path.isfile(self.token_path):
            os.remove(self.token_path)


class MiAccount:
    def __init__(self, session: ClientSession, username, password, token_store=None, cookie=""):
        self.session = session
        self.username = username
        self.password = password
        self.token_store = (
            MiTokenStore(token_store) if isinstance(token_store, str) else token_store
        )
        self.token = token_store is not None and self.token_store.load_token()
        self.cookie = cookie
        self.now_ua = get_random_ua()  # 初始化随机 User-Agent

    async def login(self, sid):

        if not self.token:
            self.token = {"deviceId": get_random(16).upper()}
        try:
            resp = await self._safeServiceLogin(f"serviceLogin?sid={sid}&_json=true")
            if resp["code"] != 0:
                data = {
                    "_json": "true",
                    "qs": resp["qs"],
                    "sid": resp["sid"],
                    "_sign": resp["_sign"],
                    "callback": resp["callback"],
                    "user": self.username,
                    "hash": hashlib.md5(self.password.encode()).hexdigest().upper(),
                }
                resp = await self._safeServiceLogin("serviceLoginAuth2", data)
                if resp["code"] == 0:
                    if resp.get("notificationUrl"):
                        raise Exception(
                            "小米账号触发安全验证，请在浏览器中打开以下链接完成验证后重试："
                            f"{resp['notificationUrl']}"
                        )

            self.token["userId"] = resp["userId"]
            self.token["passToken"] = resp["passToken"]
            serviceToken = await self._securityTokenService(
                resp["location"], resp["nonce"], resp["ssecurity"]
            )
            self.token[sid] = (resp["ssecurity"], serviceToken)
            if self.token_store:
                self.token_store.save_token(self.token)
            return True

        except Exception as e:
            self.token = None
            if self.token_store:
                self.token_store.save_token()
            _LOGGER.exception("Exception on login %s: %s", self.username, e)
            raise

    async def _serviceLogin(self, uri, data=None):
        self.now_ua = get_random_ua()
        headers = {"User-Agent": self.now_ua}
        cookies = {"sdkVersion": "3.9", "deviceId": self.token["deviceId"]}
        if "passToken" in self.token:
            cookies["userId"] = self.token["userId"]
            cookies["passToken"] = self.token["passToken"]
        else:
            cookies["passToken"] = ""
        url = "https://account.xiaomi.com/pass/" + uri
        async with self.session.request(
            "GET" if data is None else "POST",
            url,
            data=data,
            cookies=cookies,
            headers=headers,
            ssl=False,
        ) as r:
            raw = await r.read()
        resp = json.loads(raw[11:])
        _LOGGER.debug("%s: %s", uri, resp)
        return resp
    
    async def getLoginInfoFromWeb(self, cookies: str):
        url = 'https://account.xiaomi.com/pass/serviceLogin?sid=xiaomiio&_json=true'
        headers = {
            'User-Agent': 'APP/com.xiaomi.mihome APPV/6.0.103 iosPassportSDK/3.9.0 iOS/14.4 miHSTS',
        }
        cookie_dict = {}
        for item in cookies.split(";"):
            item = item.strip()
            if "=" in item:
                k, v = item.split("=", 1)
                cookie_dict[k.strip()] = v.strip()
        async with self.session.get(url,
            cookies=cookie_dict,
            headers=headers,
            ssl = False
        ) as r:
            raw = await r.read()
            resp = json.loads(raw[11:])
            resp['deviceId'] = cookie_dict.get('deviceId', '')
            resp['passToken'] = cookie_dict.get('passToken', '')
            return resp

    # 风控版登录（模拟 iOS 客户端，绕过 Web 端风控）
    async def _safeServiceLogin(self, uri, data=None):
        headers = {
            'User-Agent': 'APP/com.xiaomi.mihome APPV/6.0.103 iosPassportSDK/3.9.0 iOS/14.4 miHSTS'
        }
        resp = await self.getLoginInfoFromWeb(self.cookie)
        deviceId = resp['deviceId']
        userId = resp['userId']
        passToken = resp['passToken']
        cookies = {
            'sdkVersion': '3.9',
            'deviceId': deviceId,
            'userId': userId,
            'passToken': passToken,
        }
        url = 'https://account.xiaomi.com/pass/' + uri
        async with self.session.get(url,
            data=data,
            cookies=cookies,
            headers=headers,
            ssl = False
        ) as r:
            raw = await r.read()
            resp = json.loads(raw[11:])
            return resp

    async def _securityTokenService(self, location, nonce, ssecurity):
        nsec = "nonce=" + str(nonce) + "&" + ssecurity
        clientSign = base64.b64encode(hashlib.sha1(nsec.encode()).digest()).decode()
        async with self.session.get(
            location + "&clientSign=" + parse.quote(clientSign)
        ) as r:
            serviceToken = r.cookies["serviceToken"].value
            if not serviceToken:
                raise Exception(await r.text())
        return serviceToken

    async def mi_request(self, sid, url, data, headers, relogin=True):
        headers["User-Agent"] = self.now_ua
        if (self.token and sid in self.token) or await self.login(sid):  # Ensure login
            cookies = {
                "userId": self.token["userId"],
                "serviceToken": self.token[sid][1],
            }
            content = data(self.token, cookies) if callable(data) else data
            method = "GET" if data is None else "POST"
            _LOGGER.info("%s %s", url, content)
            async with self.session.request(
                method, url, data=content, cookies=cookies, headers=headers
            ) as r:
                status = r.status
                if status == 200:
                    resp = await r.json(content_type=None)
                    code = resp["code"]
                    if code == 0:
                        return resp
                    if "auth" in resp.get("message", "").lower():
                        status = 401
                else:
                    resp = await r.text()
            if status == 401 and relogin:
                _LOGGER.warn("Auth error on request %s %s, relogin...", url, resp)
                self.token = None  # Auth error, reset login
                return await self.mi_request(sid, url, data, headers, False)
        else:
            resp = "Login failed"
        raise Exception(f"Error {url}: {resp}")
