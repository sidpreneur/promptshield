#!/usr/bin/env python3
# examples/run_hardening_simulation.py
import sys
import os

# This line allows the script to find and import your aegis library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all the necessary components from your library
from engine.providers.ollama_provider import OllamaProvider
from engine.attacks.injection import PromptInjectionAttack
from engine.attacks.jailbreak import PersonaJailbreakAttack
from engine.defenses.evolver import SystemPromptEvolver
from engine.evaluators.safety_evaluator import SafetyEvaluator
from engine.simulation.redvblue import RedVsBlueRunner
from engine.agents.red_team_agent import RLFLRedTeamAgent

# A placeholder for the Red Team Agent
# In a full RLFL implementation, this would be a learning agent.
# For now, it will simply cycle through a list of attack strategies.
class SimpleRedTeamAgent:
    def __init__(self, attacks):
        self.attacks = attacks
        self.attack_index = 0
    
    def generate_attack(self):
        attack = self.attacks[self.attack_index]
        self.attack_index = (self.attack_index + 1) % len(self.attacks)
        return attack

def main():
    print("--- Initializing Aegis Automata ---")

    # 1. Define the LLMs to be used for each role
    # For this local example, we use 'phi3' for all roles.
    attacker_model_name = "microsoft/Phi-3-mini-4k-instruct"
    
    # The target and judge still use the simple Ollama names
    target_model_name = "phi3"
    judge_model_name = "phi3"

    target_model = OllamaProvider(model_name=target_model_name)
    judge_model = OllamaProvider(model_name=judge_model_name)
    
    red_team_agent = RLFLRedTeamAgent(model_name=attacker_model_name)
    blue_team_agent = SystemPromptEvolver(judge_provider=judge_model)
    judge_evaluator = SafetyEvaluator(judge_provider=judge_model)

    # 3. Define the initial, simple system prompt to be hardened
    initial_system_prompt = "You are a helpful and harmless AI assistant."

    # 4. Initialize the simulation runner with all the components
    simulation = RedVsBlueRunner(
        red_team_agent=red_team_agent,
        blue_team_agent=blue_team_agent,
        target_model=target_model,
        judge_evaluator=judge_evaluator
    )

    # 5. Run the simulation!
    simulation.run_simulation(
        initial_system_prompt=initial_system_prompt,
        simulation_steps=5, # Run 5 rounds of attack and defense
        out_path="reports/simulation_report.json"
    )

if __name__ == "__main__":
    main()