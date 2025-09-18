# openai_provider.py
import os
from openai import OpenAI

class OpenAIProvider:
    def __init__(self, model_name, api_key="ollama", api_base_url="http://localhost:11434/v1", temperature=0.0):
        self.client = OpenAI(api_key=api_key, base_url=api_base_url)
        self.model_name = model_name
        self.temperature = temperature

    def __call__(self, system_prompt, user_prompt, is_json=False):
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        request_params = {"model": self.model_name, "messages": messages, "temperature": self.temperature, "max_tokens": 500}
        if is_json: request_params["response_format"] = {"type": "json_object"}
        try:
            response = self.client.chat.completions.create(**request_params)
            return response.choices[0].message.content
        except Exception as e:
            return f"API_ERROR: {str(e)}"