import datetime
import uuid
from collections import Counter
from engine.utils import generate_diff

class ReportGenerator:
    def _generate_insights(self, history: list) -> str:
        insights = []
        total_attacks = len(history)
        # This logic is now CORRECT. It reads the 'is_compliant' boolean.
        successes = [r for r in history if not r.get('is_compliant', True)]
        total_successes = len(successes)
        
        if total_attacks == 0:
            return "No attacks were run."
            
        insights.append(f"Overall success rate: {total_successes / total_attacks:.1%} ({total_successes} / {total_attacks} attacks succeeded).")
        
        category_attacks = Counter([r['category'] for r in history])
        category_successes = Counter([r['category'] for r in successes])
        
        insights.append("\n**Vulnerability by Category:**")
        for category, count in category_attacks.items():
            success_count = category_successes.get(category, 0)
            rate = 0.0 if count == 0 else success_count / count
            insights.append(f"- **{category}:** {rate:.1%} success rate ({success_count} / {count} succeeded)")
            
        return "\n".join(insights)

    def _generate_prompt_diff(self, initial_prompt: str, final_prompt: str) -> str:
        if initial_prompt == final_prompt:
            return "No changes were made to the system prompt."
        
        diff = generate_diff(initial_prompt, final_prompt)
        if not diff:
            return "No textual changes detected (only whitespace differences)."
        return f"```diff\n{diff}\n```"

    def generate_report(self, history, initial_prompt, final_prompt, parameters, output_path):
        report_id = f"promptshield-run-{uuid.uuid4().hex[:12]}"
        report_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_content = []

        report_content.append(f"# **Prompt Shield: Post-Mortem Analysis Report**")
        report_content.append(f"* **Date:** {report_date}")
        report_content.append(f"* **Simulation ID:** `{report_id}`\n")
        report_content.append("---\n")

        report_content.append("## **1. Simulation Parameters** ⚙️")
        report_content.append(f"* **Target Model:** `{parameters.get('target', 'N/A')}`")
        report_content.append(f"* **Attacker Model:** `{parameters.get('attacker', 'N/A')}`")
        # This line is now FIXED. It correctly prints "Judge Model".
        report_content.append(f"* **Judge Model:** `{parameters.get('judge', 'N/A')}`\n")
        report_content.append("---\n")

        report_content.append("## **2. Executive Summary & Key Insights** 📝")
        report_content.append(self._generate_insights(history))
        report_content.append("\n---\n")

        report_content.append("## **3. Prompt Evolution (Diff)** 🛡️")
        report_content.append(self._generate_prompt_diff(initial_prompt, final_prompt))
        report_content.append("\n---\n")

        report_content.append("## **4. Detailed Round-by-Round Log** 🔬")
        current_category = ""
        for round_data in history:
            category = round_data.get("category", "N/A")
            if category != current_category:
                report_content.append(f"\n### **Category: {category}**")
                current_category = category

            outcome = round_data.get('outcome', 'UNKNOWN')
            # This logic is now CORRECT. It reads the 'is_compliant' boolean.
            is_success = not round_data.get('is_compliant', True)

            report_content.append(f"\n#### **Round {round_data['round']} | Attempt {round_data.get('attempt', 'N/A')}**")
            report_content.append(f"* **Attack Prompt:** `{round_data['attack_prompt'][:200]}...`")
            report_content.append(f"* **Result:** `{outcome}` (**{'SUCCESS' if is_success else 'FAILURE'}**)")

            if "failed_prompt_generation" in round_data:
                report_content.append(f"* **Analysis:** Attack succeeded, but Blue Team's new defense failed validation and was discarded.")
            elif is_success:
                report_content.append(f"* **Analysis:** Attack successfully bypassed defenses. Blue Team defense was validated and deployed.")
            else:
                report_content.append(f"* **Analysis:** System defenses held strong and blocked the attack.")

        report_content.append("\n---\n")

        report_content.append("## **5. Final Hardened System Prompt (Full Text)**")
        report_content.append("\n```")
        report_content.append(final_prompt)
        report_content.append("```\n")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_content))
        print(f"--- Detailed markdown report saved to {output_path} ---")