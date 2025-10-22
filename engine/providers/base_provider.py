# aegis/providers/base_provider.py
from abc import ABC, abstractmethod

class BaseProvider(ABC):
    """Abstract base class for all LLM provider types."""
    @abstractmethod
    def __call__(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """Executes a prompt and returns the model's response as a string."""
        pass