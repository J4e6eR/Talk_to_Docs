# OpenAI Chatgpt working
# TODO: Clean up the code, handle new conversations and finally push this updated code to gpt4free or create our own repo 

from __future__ import annotations

from curl_cffi.requests import AsyncSession
import uuid
import json
from enum import Enum
import faulthandler
from .base_provider import AsyncProvider, get_cookies, format_prompt
from .typings import AsyncGenerator
from typing import Optional

faulthandler.enable()

BASE_URL = 'https://chat.openai.com/backend-api/conversation'


class Role_type(Enum):
    """
    Decides the role of the chatbot
    """

    SYSTEM = 'system'
    ASSISTANT = 'assistant'
    USER = 'user'

class Formatted_Response():
    """
    Takes care of formatting the response received from the assistant i.e. ChatGPT
    Holds information about 
    1. message_id       : refrenced with msg_id
    2. parent_id        : refrenced with parent_id
    3. conversation_id  : refrenced with conversation_id
    4. Message          : refrenced with msg
    """
    def __init__(
        self,
        response: dict,
    ) -> None:
        self.msg_id          = response['message']['id']
        self.parent_id       = response['message']['metadata']['parent_id']
        self.conversation_id = response['conversation_id']
        self.msg             = response["message"]["content"]["parts"][0]


class OpenaiChat(AsyncProvider):
    """
    Main class which handles conversation with the specified model
    """

    url                   = "https://chat.openai.com"
    needs_auth            = True
    working               = True
    supports_gpt_35_turbo = True
    _access_token         = None
    proxies               = None
    headers               = None


    def __init__(self, access_token: str) -> None:
        # super().__init__()
        self._access_token = access_token
        self._access_token = access_token
        self.proxies = None
        self.headers = {
            "Accept": "text/event-stream",
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        }
        self.cookies = None
        self.conversation_mapping = {}

    # @classmethod
    async def get_msg_history(self, convo_id: str, encoding: str | None = None) -> list:
        """
        Get message history
        :param id: UUID of conversation
        :param encoding: String
        """
        # print("headers in msg history =", self.headers)
        msg_url = f"{BASE_URL}/{convo_id}"
        async with AsyncSession(proxies=self.proxies, headers=self.headers, impersonate="chrome107") as session:
            response = await session.get(msg_url)
            response.raise_for_status()
            return response.json()

    # @classmethod
    async def create_async(
        self,
        prompt: list[str],
        model: Optional [str] = None,
        proxy: str = None,
        access_token: str = None,
        cookies: dict = None,
        role: Role_type = Role_type.USER.value,
        conversation_id: str = None,
        disable_history: bool = False,
        **kwargs: dict
    ) -> Formatted_Response:
        
        self.prompt = prompt
        
        if proxy:
            if "://" not in proxy:
                proxy = f"http://{proxy}"
            self.proxies = {
                "http": proxy,
                "https": proxy
            }

        # if not access_token:
        #     access_token = await cls.get_access_token(cookies, cls.proxies)
        
        if type(self.prompt) is str:
            self.prompt = [prompt]

        # Get the list of all messages in a current converation
        history = await self.get_msg_history(conversation_id)

        # The thing which is of concern here is that the currentnode of the previous conversation would be set as the parent node to get the message registered
        self.conversation_mapping[conversation_id] = history["current_node"] 

        async with AsyncSession(proxies=self.proxies, headers=self.headers, cookies = self.cookies, impersonate="chrome107") as session:
            messages = [
                {
                    "id": str(uuid.uuid4()),
                    "author": {"role": role},
                    "content": {"content_type": "text", "parts": self.prompt},
                    "metadata": {}
                },
            ]
            data = {
                "action": "next",
                "messages": messages,
                "conversation_id": conversation_id or None,
                "parent_message_id": self.conversation_mapping[conversation_id] or str(uuid.uuid4()),
                "model": model or "text-davinci-002-render-sha",
                "history_and_training_disabled": disable_history,
            }

            response = await session.post(BASE_URL, json=data)
            # print("Response =", response.text)
            response.raise_for_status()
            last_message = None
            
            for line in response.content.decode().splitlines():
                if line.startswith("data: "):
                    line = line[6:]
                    if line != "[DONE]":
                        line = json.loads(line)
                        if "message" in line:
                            # last_message = line["message"]["content"]["parts"][0]
                            last_message = line
            return Formatted_Response(last_message)

    # @classmethod
    async def get_access_token(self, cookies: dict = None, proxies: dict = None):
        if not self._access_token:
            cookies = cookies if cookies else get_cookies("chat.openai.com")
            async with AsyncSession(proxies=proxies, cookies=cookies, impersonate="chrome107") as session:
                response = await session.get("https://chat.openai.com/api/auth/session")
                response.raise_for_status()
                self._access_token = response.json()["accessToken"]
        return self._access_token
    
    

    # @classmethod
    # @property
    # def params(cls):
    #     params = [
    #         ("model", "str"),
    #         ("messages", "list[dict[str, str]]"),
    #         ("stream", "bool"),
    #         ("proxy", "str"),
    #         ("access_token", "str"),
    #         ("cookies", "dict[str, str]")
    #     ]
    #     param = ", ".join([": ".join(p) for p in params])
    #     return f"g4f.provider.{cls.__name__} supports: ({param})"