# Custom LLM implementation for revChat in Langchain
from typing import Any, Mapping, Optional
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManager,CallbackManagerForLLMRun
from langchain.callbacks.base import BaseCallbackHandler
# import typing

import revChatGPT
from revChatGPT.V1 import Chatbot
import tokens
import faulthandler

faulthandler.enable()

# Handler Class Currently working on it Callbacks not working, we can ignore it for now to create but we will have to solve this 
class MyHandler(BaseCallbackHandler):

    def on_llm_new_token(self, token: str):
        print(f"New token: {token}")

# Currently only Synchronous operations are being supported.
class CustomLLM(LLM):
    n: int
    chatbot:'Chatbot'
    config:'dict'
    response:'dict'
    callbacks:'list'

    # Added to prevent a pydantic error of __field_set__ attribute missing
    __fields_set__  = set()

    def __init__(self, config:dict, n = 10):
        
        """Initializes a ChatBot of V1 revChatGPT

       Args:
        config[dict] = 
        "access_token" - "<access_token>"
        "proxy" - "<proxy_url_string>",
        "model" - "<model_name>",
        "plugin" - "<plugin_id>", } More details on these are available at https://github.com/acheong08/ChatGPT#configuration
        "conversation_id" str | None, optional - Id of the conversation to continue on. Defaults to None.
        "parent_id" str | None, optional - Id of the previous response message to continue on. Defaults to None.
        "session_client" type, optional - description. Defaults to None.
       """
        self.config = config
        try: 
            self.chatbot = Chatbot(config = self.config)
        except Exception as e:
            print("Unexpected error ", e)


    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: str,
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
        for data in self.chatbot.ask(
            prompt
        ):
            self.response = data
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
    config={
  "access_token": f"{tokens.load_tokens('GPT_ACCESS_TOKEN')}",
  "conversation_id": '34e32a56-66f7-4955-bd40-526f78937ee8',
}
    prompt = input("Enter the Question: ")
    llm = CustomLLM(config, 10)
    llm._call(prompt)
    print("Answer: ",llm.response['message'])
    
handler = MyHandler()
run_manager = CallbackManagerForLLMRun(run_id='run1', handlers=[handler], inheritable_handlers=[]) 



        # return self.response