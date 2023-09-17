# Custom LLM implementation for revChat in Langchain
# TODO: Have to add conversation id while asking questions rather than in config file
# TODO: Has to build custom chat model which eases the interaction with langchain chains and agents

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from OpenAI_chatGPT.openai import Role_type, OpenaiChat, Formatted_Response
import asyncio

from typing import Any, Mapping, Optional
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManager,CallbackManagerForLLMRun
from langchain.callbacks.base import BaseCallbackHandler
# import typing]

import tokens
import faulthandler

faulthandler.enable()

# Returns the response of the user
async def run_ChatGPT(chatbot, prompt:str, role: Role_type.USER.value, conversation_id: str = None ):
    return await chatbot.create_async(prompt=prompt, role = role, conversation_id=conversation_id)
    
# Handler Class Currently working on it Callbacks not working, we can ignore it for now to create but we will have to solve this 
class MyHandler(BaseCallbackHandler):

    def on_llm_new_token(self, token: str):
        print(f"New token: {token}")

# Currently only Synchronous operations are being supported.
class CustomLLM(LLM):
    n: int
    chatbot:'OpenaiChat'
    config:'dict'
    response:'dict'
    callbacks:'list'
    access_token: 'str'

    # Added to prevent a pydantic error of __field_set__ attribute missing
    __fields_set__  = set()

    def __init__(self, access_token: str, n = 10):
        
        """Initializes a ChatBot of V1 revChatGPT

       Args:
        "access_token" - "<access_token>"
        "proxy" - "<proxy_url_string>",
        "model" - "<model_name>",
        "plugin" - "<plugin_id>", } More details on these are available at https://github.com/acheong08/ChatGPT#configuration
        "conversation_id" str | None, optional - Id of the conversation to continue on. Defaults to None.
        "parent_id" str | None, optional - Id of the previous response message to continue on. Defaults to None.
        "session_client" type, optional - description. Defaults to None.
       """
        self.access_token = access_token
        try: 
            self.chatbot = OpenaiChat(access_token=self.access_token)
        except Exception as e:
            print("Unexpected error ", e)


    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: str,
        role : str,
        conversation_id: str | None = None,
        parent_id: str = "",
        model: str = "",
        plugin_ids: list = [],
        auto_continue: bool = False,
        timeout: float = 360,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs, 
    ):
        """Ask a question to the chatbot
        Args:
            prompt (str): The question
            conversation_id (str, optional): UUID for the conversation to continue on. Defaults to None.
            parent_id (str, optional): UUID for the message to continue on. Defaults to "".
            model (str, optional): The model to use. Defaults to "".
            auto_continue (bool, optional): Whether to continue the conversation automatically. Defaults to False.
            timeout (float, optional): Timeout for getting the full response, unit is second. Defaults to 360.
            """
        
        # Response holds entire data, it's mostly a dictionary containing some valuable information
        print("Entered the call function")
        self.response=""
        
        # Asynhronously runs the model 
        import os
        if os.name == 'nt':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        try:
            self.response = asyncio.run(run_ChatGPT(self.chatbot, role=role, prompt=prompt, conversation_id=conversation_id))
        except Exception as e:
            print("Error or exception =", e)

        if run_manager:
            res = run_manager.on_llm_new_token(self.response)
            print("Response while using callbacks =", res)
            # self.callbacks = []
            

    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"n": self.n}

    # A way to get responses
    def get_results(self):
        return self.response
    




if __name__ == "__main__":
#     config={
#   "access_token": f"{tokens.load_tokens('GPT_ACCESS_TOKEN')}",
#   "conversation_id": '34e32a56-66f7-4955-bd40-526f78937ee8',
# }


    prompt = input("Enter the Question: ")
    llm = CustomLLM(access_token=tokens.load_verified_token('GPT_ACCESS_TOKEN'))
    llm._call(prompt,role=Role_type.USER.value, conversation_id='c6f6fb09-6981-48c9-b4a8-2c77822fc691')

    print("Answer: ",llm.response.msg)
    
handler = MyHandler()
run_manager = CallbackManagerForLLMRun(run_id='run1', handlers=[handler], inheritable_handlers=[]) 



        # return self.response