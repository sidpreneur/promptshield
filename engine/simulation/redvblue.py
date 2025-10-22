# aegis/simulation/red_vs_blue_runner.py
import json
import time

class RedVsBlueRunner:
    """
    Orchestrates the adversarial simulation between a Red Team (Attacker)
    and a Blue Team (Defender) to progressively harden an AI model's system prompt.
    """
    def __init__(self, red_team_agent, blue_team_agent, target_model, judge_evaluator):
        self.red_team = red_team_agent
        self.blue_team = blue_team_agent
        self.target_model = target_model
        self.judge = judge_evaluator
        self.history = []

    def run_simulation(self, initial_system_prompt: str, simulation_steps: int = 10, out_path: str = None):
        print("--- LAUNCHING AEGIS AUTOMATA: RED VS. BLUE SIMULATION ---")
        current_system_prompt = initial_system_prompt
        
        for step in range(1, simulation_steps + 1):
            print(f"\n--- [ROUND {step}/{simulation_steps}] ---")
            
            # 1. ATTACK: Red Team generates a new attack.
            print("  [Red Team]: Generating new attack vector...")
            attack_object = self.red_team.generate_attack()
            attack_prompt = attack_object.generate_prompt()
            print(f"  -> Attack: '{attack_prompt[:100]}...'")

            # 2. DEFEND: Target Model responds using the current defense.
            print("  [Target Model]: Responding to attack...")
            target_response = self.target_model(system_prompt=current_system_prompt, user_prompt=attack_prompt)

            # 3. EVALUATE: Judge AI determines the outcome.
            print("  [Judge AI]: Evaluating outcome...")
            evaluation = self.judge.evaluate(attack=attack_object, response=target_response, system_prompt=current_system_prompt)
            is_compliant = evaluation.get("is_compliant", False)
            classification = evaluation.get("classification", "EVALUATION_ERROR")
            print(f"  -> Result: {classification}")

            # 4. RED TEAM LEARNS: The attacker learns from the outcome.
            if hasattr(self.red_team, 'learn'):
                self.red_team.learn(evaluation)

            # 5. BLUE TEAM ADAPTS: The defender adapts if the attack was successful.
            if not is_compliant:
                print("  [Blue Team]: Attack SUCCEEDED. Evolving system prompt...")
                failure_report = {"attack_prompt": attack_prompt, "failed_response": target_response, "reasoning": evaluation.get("reasoning")}
                new_system_prompt = self.blue_team.evolve_defense(previous_prompt=current_system_prompt, failure_report=failure_report)
                current_system_prompt = new_system_prompt
                print("  -> New Defense Deployed.")
            else:
                print("  [Blue Team]: Attack FAILED. Defense holds strong.")
            
            self.history.append({"round": step, "attack_id": attack_object.id, "attack_prompt": attack_prompt, "outcome": classification, "system_prompt_used": current_system_prompt})
            time.sleep(1)

        print("\n--- SIMULATION COMPLETE ---")
        print(f"Final Hardened System Prompt:\n{current_system_prompt}")

        if out_path:
            final_report = {"final_hardened_prompt": current_system_prompt, "simulation_history": self.history}
            with open(out_path, "w", encoding="utf-8") as f: json.dump(final_report, f, indent=2, ensure_ascii=False)
            print(f"--- Full simulation report saved to {out_path} ---")
            
        return current_system_prompt