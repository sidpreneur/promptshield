import datetime
import uuid

class ReportGenerator:
    """
    Takes the raw history from a simulation and generates a detailed,
    human-readable markdown report.
    """
    def generate_report(self, history, final_prompt, parameters, output_path):
        """
        Generates and saves the full markdown report.
        """
        report_id = f"promptshield-run-{uuid.uuid4().hex[:12]}"
        report_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_content = []

        # --- Header ---
        report_content.append(f"# **Prompt Shield: Post-Mortem Analysis Report**")
        report_content.append(f"* **Date:** {report_date}")
        report_content.append(f"* **Simulation ID:** `{report_id}`\n")
        report_content.append("---\n")

        # --- Executive Summary (Rule-based) ---
        successes = [r for r in history if r.get('outcome') == 'SUCCESS' or 'COMPLIANCE' in r.get('outcome')]
        num_successes = len(successes)
        total_rounds = len(history)
        report_content.append("## **1. Executive Summary** 📝")
        summary = (
            f"The simulation completed **{total_rounds}** rounds of adversarial testing. "
            f"The Red Team achieved **{num_successes}** successful breaches across multiple categories, "
            f"forcing the Blue Team to evolve the system prompt {num_successes} times. "
            "This report provides a detailed breakdown of each attack attempt, the model's response, and the resulting defensive evolutions."
        )
        report_content.append(summary + "\n")

        # --- Simulation Parameters ---
        report_content.append("## **2. Simulation Parameters** ⚙️")
        report_content.append(f"* **Target Model:** `{parameters.get('target', 'N/A')}`")
        report_content.append(f"* **Attacker Model:** `{parameters.get('attacker', 'N/A')}`")
        report_content.append(f"* **Judge Model:** `{parameters.get('judge', 'N/A')}`\n")
        report_content.append("---\n")

        # --- Detailed Round-by-Round Analysis ---
        report_content.append("## **3. Detailed Round-by-Round Analysis** 🔬")
        current_category = ""
        category_count = 0
        for round_data in history:
            category = round_data.get("category", "N/A")
            if category != current_category:
                category_count += 1
                report_content.append(f"\n### **3.{category_count}. Category: {category}**")
                current_category = category

            outcome = round_data.get('outcome', 'UNKNOWN')
            is_success = "SUCCESS" in str(outcome) or "COMPLIANCE" in str(outcome)

            report_content.append(f"\n#### **Round {round_data['round']} | Attempt {round_data.get('attempt', 'N/A')}**")
            report_content.append(f"* **Attack Prompt:** `{round_data['attack_prompt'][:200]}...`")
            report_content.append(f"* **Result:** `{outcome}` (**{'SUCCESS' if is_success else 'FAILURE'}**)")

            if is_success:
                report_content.append(f"* **Analysis:** The attack successfully bypassed the system's defenses. The `'{category}'` vector proved effective, forcing a defensive adaptation.")
            else:
                report_content.append(f"* **Analysis:** The system's defenses held strong against the `'{category}'` attack and successfully blocked the attempt.")

        report_content.append("\n---\n")

        # --- Final Hardened Prompt ---
        report_content.append("## **4. Final Hardened System Prompt** 🛡️")
        report_content.append("The following prompt is the result of all successful defensive evolutions throughout the simulation:")
        report_content.append("\n```")
        report_content.append(final_prompt)
        report_content.append("```\n")

        # --- Write to file ---
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_content))
        print(f"--- Detailed markdown report saved to {output_path} ---")