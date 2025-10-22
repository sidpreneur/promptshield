# aegis/evaluators/base_evaluator.py
from abc import ABC, abstractmethod

class BaseEvaluator(ABC):
    """
    Abstract base class for all evaluator types.

    This class defines the essential methods that every evaluator agent
    must implement to judge the outcome of an attack.
    """

    @abstractmethod
    def evaluate(self, attack: object, response: str, system_prompt: str) -> dict:
        """
        Evaluates a model's response to a specific attack and returns a
        structured dictionary with the verdict.

        Args:
            attack: The attack object that was used.
            response: The target model's response to the attack.
            system_prompt: The system prompt that the target model was using.

        Returns:
            A dictionary containing the evaluation results, including compliance,
            classification, and reasoning.
        """
        pass