# aegis/attacks/base_attack.py
from abc import ABC, abstractmethod

class BaseAttack(ABC):
    """
    Abstract base class for all attack types.

    This class defines the essential properties and methods that every
    attack strategy must implement.
    """
    id: str = "base.attack"
    category: str = "general"
    
    @abstractmethod
    def generate_prompt(self, **kwargs) -> str:
        """
        Generates the malicious prompt for the attack.
        
        This method can accept keyword arguments to make prompts more dynamic.
        """
        pass