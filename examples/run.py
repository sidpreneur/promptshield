import sys
import os
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.providers.ollama_provider import OllamaProvider
from engine.defenses.evolver import SystemPromptEvolver
from engine.evaluators.safety_evaluator import SafetyEvaluator
from engine.simulation.redvblue import RedVsBlueRunner
from engine.agents.red_team_agent import EscalationAgent

def main():
    print("--- Initializing Prompt Shield ---")

    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    cfg_sim = config['simulation']
    cfg_models = config['models']
    cfg_attacks = config['static_attacks']
    
    target_model = OllamaProvider(model_name=cfg_models['target'])
    attacker_model = OllamaProvider(model_name=cfg_models['attacker'])
    
    judge_model = OllamaProvider(model_name=cfg_models['judge'])
    
    print(f"Target: {cfg_models['target']} | Attacker: {cfg_models['attacker']} | Judge: {cfg_models['judge']}")

    red_team_agent = EscalationAgent(
        attacker_provider=attacker_model,
        static_attacks=cfg_attacks
    )
    
    blue_team_agent = SystemPromptEvolver(
        provider=attacker_model
    )
    
    judge_evaluator = SafetyEvaluator(
        judge_provider=judge_model
    )

    initial_system_prompt = cfg_sim['initial_system_prompt']
    attack_categories = list(cfg_attacks.keys())
    
    print(f"Running simulation with categories: {attack_categories}")

    simulation = RedVsBlueRunner(
        red_team_agent=red_team_agent,
        blue_team_agent=blue_team_agent,
        target_model=target_model,
        judge_evaluator=judge_evaluator
    )

    simulation.run_simulation(
        initial_system_prompt=initial_system_prompt,
        attack_categories=attack_categories,
        attempts_per_category=cfg_sim['attempts_per_category'],
        out_path=cfg_sim['reports']['json_path'],
        md_report_path=cfg_sim['reports']['markdown_path']
    )

if __name__ == "__main__":
    main()