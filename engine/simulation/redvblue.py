import json
import time
from engine.attacks.base import BaseAttack
from reports.reportGen import ReportGenerator

class SimpleAttackWrapper(BaseAttack):
    def __init__(self, prompt: str, category: str):
        self._prompt = prompt
        self.id: str = "dynamic.generated"
        self.category: str = category
    def generate_prompt(self, **kwargs) -> str:
        return self._prompt

class RedVsBlueRunner:
    def __init__(self, red_team_agent, blue_team_agent, target_model, judge_evaluator):
        self.red_team = red_team_agent
        self.blue_team = blue_team_agent
        self.target_model = target_model
        self.judge = judge_evaluator
        self.history = []

    def run_simulation(self, initial_system_prompt: str, attack_categories: list, attempts_per_category: int = 3, out_path: str = None, md_report_path: str = None):
        print("--- LAUNCHING PROMPT SHIELD: PERSISTENT RED VS. BLUE SIMULATION ---")
        current_system_prompt = initial_system_prompt
        overall_step = 0
        
        for category in attack_categories:
            print(f"\n--- [ATTACKING CATEGORY: {category}] ---")
            
            for attempt in range(1, attempts_per_category + 1):
                overall_step += 1
                print(f"\n--- [Round {overall_step}] | Category: {category} | Attempt: {attempt}/{attempts_per_category} ---")
           
                print(f"  [Red Team]: Generating '{category}' attack vector...")
                attack_generated = self.red_team.generate_attack(category=category)

                attack_object = SimpleAttackWrapper(attack_generated, category=category)
                attack_prompt = attack_object.generate_prompt()
                print(f"  -> Attack: '{attack_prompt[:100]}...'")
          
                print("  [Target Model]: Responding to attack...")
                target_response = self.target_model(system_prompt=current_system_prompt, user_prompt=attack_prompt)
         
                print("  [Judge AI]: Evaluating outcome...")
                evaluation = self.judge.evaluate(attack=attack_object, response=target_response, system_prompt=current_system_prompt)
                is_compliant = evaluation.get("is_compliant", False)
                classification = evaluation.get("classification", "EVALUATION_ERROR")
                reasoning = evaluation.get("reasoning", "No reasoning provided.")
                
                print(f"  -> Result: {classification}")
                print(f"  -> Judge's Reasoning: {reasoning}") 

                if hasattr(self.red_team, 'learn'):
                    self.red_team.learn(category, attack_prompt, evaluation)

                # This log_entry now correctly includes the 'is_compliant' boolean
                log_entry = {
                    "round": overall_step, "category": category, "attempt": attempt, "attack_id": attack_object.id, 
                    "attack_prompt": attack_prompt, "outcome": classification, "is_compliant": is_compliant,
                    "system_prompt_used": current_system_prompt
                }

                if not is_compliant:
                    print(f"  [Blue Team]: Attack SUCCEEDED on attempt {attempt}. Evolving system prompt...")
                    failure_report = {"attack_prompt": attack_prompt, "failed_response": target_response, "reasoning": reasoning}
                    new_system_prompt = self.blue_team.evolve_defense(previous_prompt=current_system_prompt, failure_report=failure_report)
                    
                    print("  [Blue Team]: Validating new defense against the same attack...")
                    validation_response = self.target_model(system_prompt=new_system_prompt, user_prompt=attack_prompt)
                    validation_eval = self.judge.evaluate(attack=attack_object, response=validation_response, system_prompt=new_system_prompt)
                    
                    if validation_eval.get("is_compliant"):
                        print("  -> Validation SUCCESS. Defense holds. Deploying new prompt.")
                        current_system_prompt = new_system_prompt
                        log_entry["new_prompt_generated"] = new_system_prompt
                        self.history.append(log_entry)
                        time.sleep(1)
                        break 
                    else:
                        print("  -> Validation FAILED. New defense is ineffective. Retaining old prompt and retrying.")
                        log_entry["outcome"] = "DEFENSE_VALIDATION_FAILED"
                        log_entry["failed_prompt_generation"] = new_system_prompt
                        self.history.append(log_entry)
                        time.sleep(1)
                else:
                    print("  [Blue Team]: Attack FAILED. Defense holds strong. Trying again.")
                    self.history.append(log_entry)
                    time.sleep(1)

        print("\n--- SIMULATION COMPLETE ---")
        print(f"Final Hardened System Prompt:\n{current_system_prompt}")

        if out_path:
            final_report = {"final_hardened_prompt": current_system_prompt, "simulation_history": self.history}
            with open(out_path, "w", encoding="utf-8") as f: json.dump(final_report, f, indent=2, ensure_ascii=False)
            print(f"--- Full simulation JSON report saved to {out_path} ---")
            
        if md_report_path:
            try:
                # This block is now fixed to handle a SINGLE judge, not a panel.
                simulation_params = {
                    'target': self.target_model.model_name,
                    'attacker': self.red_team.attacker_provider.model_name,
                    'judge': self.judge.judge_provider.model_name
                }
                report_generator = ReportGenerator()
                report_generator.generate_report(self.history, initial_system_prompt, current_system_prompt, simulation_params, md_report_path)
            except AttributeError as e:
                print(f"[ERROR] Could not generate markdown report. A model provider is missing a 'model_name' attribute. Details: {e}")
            
        return current_system_prompt