# Custom LLM implementation for revChat in Langchain
# TODO: Tryy running this application using our implementation of cCHatGPT. Sometimes the issue related to code challenge required is encountered. Has to deal with it

from typing import Any, Dict, Mapping, Optional, List, Sequence, Union
from uuid import UUID
import sys
from pathlib import Path
import faulthandler
faulthandler.enable()

sys.path.append(str(Path(__file__).parent.parent))
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManager,CallbackManagerForLLMRun
from langchain.callbacks.base import BaseCallbackHandler
from langchain import PromptTemplate
from langchain.schema import Document, LLMResult
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from OpenAI_chatGPT.openai import Role_type, OpenaiChat, Formatted_Response

import asyncio
# import typing
# import revChatGPT
# from revChatGPT.V1 import Chatbot
# from chatgpt import Chatbot, Role_type
import tokens


# # Handler Class Currently working on it Callbacks not working, we can ignore it for now to create but we will have to solve this 
# class MyHandler(BaseCallbackHandler):

#     def on_llm_new_token(self, token: str):
#         print(f"New token: {token}")

# Has to add all this just to please the langchain codebase.
class CustomCallbackForRetriever(CallbackManagerForRetrieverRun):

    """Callback manager for multiquery retriever"""

    def __init__(self, *, run_id: UUID = None, handlers: List[BaseCallbackHandler] = [], inheritable_handlers: List[BaseCallbackHandler] = [], parent_run_id: UUID | None = None, tags: List[str] | None = None, inheritable_tags: List[str] | None = None, metadata: Dict[str, Any] | None = None, inheritable_metadata: Dict[str, Any] | None = None) -> None:
        super().__init__(run_id=run_id, handlers=handlers, inheritable_handlers=inheritable_handlers, parent_run_id=parent_run_id, tags=tags, inheritable_tags=inheritable_tags, metadata=metadata, inheritable_metadata=inheritable_metadata)
    def on_retriever_end(self, documents: Sequence[Document], **kwargs: Any) -> None:
        # return super().on_retriever_end(documents, **kwargs)
        pass

    def on_retriever_error(self, error: Exception | KeyboardInterrupt, **kwargs: Any) -> None:
        # return super().on_retriever_error(error, **kwargs)
        pass


class MycustomHandler(CallbackManagerForLLMRun):

    """Callback manager for custom llm run"""
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        # return super().on_llm_new_token(token, **kwargs)
        pass
    def on_llm_error(self, error: Exception | KeyboardInterrupt, **kwargs: Any) -> None:
        return super().on_llm_error(error, **kwargs)
        pass
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        # return super().on_llm_end(response, **kwargs)
        pass

# Returns the response of the user
async def run_ChatGPT(chatbot, prompt:str, role: Role_type.USER.value, conversation_id: str = None ):
    return await chatbot.create_async(prompt=prompt, role = role, conversation_id=conversation_id)
    

# Currently only Synchronous operations are being supported.
class CustomLLM(LLM):
    n: int
    chatbot: 'OpenaiChat'
    config:'dict'
    response:'dict'
    callbacks:'list'
    verbose: 'bool'
    tags: List[str] | None
    access_token:'str'
    conversation_id : 'str'

    # Added to prevent a pydantic error of __field_set__ attribute missing
    __fields_set__  = set()

    def __init__(self, access_token: str, callbacks = None ,n = 10, verbose :bool = False, metadata : dict = None, cache:bool = False, tags: List[str] | None = None, conversation_id: str = None):
        
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
        "cache" "bool" used to store and retrieve previously generated responses.
       """
        
        # Added all of these to make it compatible to various features all across langchain 
        self.callbacks= callbacks or []
        self.verbose = verbose
        # self.config = config
        self.access_token = access_token
        self.metadata = metadata
        self.n = n
        self.cache = cache
        self.tags = tags
        try: 
            self.chatbot = OpenaiChat(self.access_token, )
        except Exception as e:
            print("Unexpected error ", e)


    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: str,
        role :str = 'user',
        conversation_id: str | None = None,
        parent_id: str = "",
        model: str = "",
        plugin_ids: list = [],
        auto_continue: bool = False,
        timeout: float = 360,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        callbacks: Optional[BaseCallbackHandler] = [],
        tags: List[str] = None,
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
        self.tags = tags
        print("Entered the call function")
        self.response=""
        # for data in self.chatbot.ask(
        #     prompt,
        #     conversation_id=conversation_id,
        #     role=Role_type.USER.value
        # ):
        #     self.response = data
        
        # Asynhronously runs the model 
        import os
        if os.name == 'nt':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        self.response = asyncio.run(run_ChatGPT(self.chatbot, role=role, prompt=prompt, conversation_id=conversation_id))
        
        self.callbacks = callbacks

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
    
    # def run(self, prompt:str, callbacks = []):
    #     self.callbacks = callbacks




if __name__ == "__main__":
#     config={
#   "access_token": f"{tokens.load_verified_token('GPT_ACCESS_TOKEN')}",
#   "conversation_id": 'c6f6fb09-6981-48c9-b4a8-2c77822fc691',
# }
    
    prompt = input("Enter the Question: ")
    llm = CustomLLM(access_token=tokens.load_verified_token('GPT_ACCESS_TOKEN'))
    llm._call(prompt,role=Role_type.USER.value, conversation_id='c6f6fb09-6981-48c9-b4a8-2c77822fc691')
    # print("Original headers = ", llm.chatbot.session._auth)   
    # print("Answer: ",llm.response['message'])
    print("Answer: ",llm.response.msg)
    
# handler = MyHandler()
# run_manager = CallbackManagerForLLMRun(run_id='run1', handlers=[handler], inheritable_handlers=[]) 



        # return self.response