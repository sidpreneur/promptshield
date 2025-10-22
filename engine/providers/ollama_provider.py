# aegis/providers/ollama_provider.py
from openai import OpenAI
from .base_provider import BaseProvider

class OllamaProvider(BaseProvider):
    """A provider for local models served via Ollama's OpenAI-compatible API."""
    def __init__(self, model_name: str, api_key: str = "ollama", api_base_url: str = "http://localhost:11434/v1", temperature: float = 0.0):
        self.client = OpenAI(api_key=api_key, base_url=api_base_url)
        self.model_name = model_name
        self.temperature = temperature

    def __call__(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        request_params = {"model": self.model_name, "messages": messages, "temperature": self.temperature, "max_tokens": 500}

        if kwargs.get("is_json", False):
            request_params["response_format"] = {"type": "json_object"}
            
        try:
            response = self.client.chat.completions.create(**request_params)
            return response.choices[0].message.content
        except Exception as e:
            return f"API_ERROR: {str(e)}"