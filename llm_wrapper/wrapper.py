import time
import requests
import openai
import dotenv
import os
import pdb
from langchain.vectorstores.weaviate import Weaviate
import weaviate
from prompts.system_prompt import SYSTEM_PROMPT

class LLMWrapper:
    """Wrapper class for the LLM API."""
    def __init__(self, max_tokens=1000, model="gpt-3.5-turbo", max_try=2, temprature=0):
        self.max_tokens = max_tokens
        self.model = model
        self.temperature = temprature
        self.max_try = max_try
        self.history = False

    def _send_request(self, user_prompt="", vectorstore=None):
        for _ in range(self.max_try):
            try:
                if self.history:
                    batch_size = 5
                    GENERAL_CHAT_PROMPT = self.history.append({"role": "user", "content": f"{user_prompt}"}) 
                    print(GENERAL_CHAT_PROMPT, "printing general chat prompt")
                    response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=GENERAL_CHAT_PROMPT,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        stream=True,
                    )
                    return response 
                else:
                    CHAT_PROMPT = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]
                    print(CHAT_PROMPT, "printing chat prompt")
                    response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=CHAT_PROMPT,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        stream=True,
                    )
                    return response

            except openai.error.RateLimitError as e:
                self._handle_rate_limit()
                return self._send_request(CHAT_PROMPT, vectorstore)
            
            except openai.error.InvalidRequestError as e:
                if len(prompt) > self.max_tokens:
                    print("Prompt too long. Truncating...")
                    prompt = prompt[:self.max_tokens]
                    return self._send_request(prompt, vectorstore)
                print("Invalid request:", e)
                return {'error': 'invalid_request'}
            
            except Exception as e:
                print("Unhandled exception:", e)
                return {'error': 'unknown'}

    def _handle_rate_limit(self):
        print("Rate limit exceeded. Waiting before retrying...")
        time.sleep(60) 

    def generate_response(self, user_input):
        conversation = user_input
        response = self._send_request(conversation)
        return response

    def reset_history(self):
        self.history = False

if __name__ == "__main__":
    dotenv.load_dotenv()
    openai.api_key = os.getenv("OPENAI_APIKEY")
    API_TOKEN = os.getenv("HUGGINGFACE_APIKEY")

    wrapper = LLMWrapper()
    vectrstore = weaviate.Client("http://localhost:8080",
            additional_headers={
                "X-HuggingFace-Api-Key": API_TOKEN
    })

    index = 0
    while True:
        user_input = input("\nUser: ")    
        response = wrapper.generate_response(user_input)

        response_msg = ""
        for r in response:
            if r["choices"][0]["delta"] == {}:
                break
            msg = r["choices"][0]["delta"]["content"]
            response_msg += msg
            print(msg, end="", flush=True)
        wrapper.history = True
        vectrstore.data_object.create({
            "conversation": str({"User": user_input,
                                 "AI": response_msg}), 
            "chatIndex": index
            }, "Chat")
        index += 1