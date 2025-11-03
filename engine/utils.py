import difflib

def generate_diff(prompt_a: str, prompt_b: str) -> str:
    """
    Generates a simple text-based diff between two system prompts.
    """
    diff = difflib.ndiff(prompt_a.splitlines(), prompt_b.splitlines())
    return "\n".join(line for line in diff if line.startswith("+ ") or line.startswith("- "))