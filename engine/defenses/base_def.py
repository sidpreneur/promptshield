# aegis/defenses/base_defense.py
from abc import ABC, abstractmethod

class BaseDefense(ABC):
    """
    Abstract base class for all defense mechanisms.

    This class defines the essential methods that every defense agent
    must implement to protect the target model.
    """
    
    @abstractmethod
    def evolve_defense(self, previous_prompt: str, failure_report: dict) -> str:
        """
        Analyzes a successful attack and generates an improved system prompt.

        Args:
            previous_prompt: The system prompt that failed to block the attack.
            failure_report: A dictionary containing details about the successful attack.

        Returns:
            A new, hardened system prompt designed to be more resilient.
        """
        pass