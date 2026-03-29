"""Q5: System prompt evolution in extractTextFromPDF.py across all major versions."""
import subprocess
import re

# Key commits that changed the system prompt
versions = [
    ("303c56b", "2023-08-28", "V1: Initial (GPT-3.5, per-page)"),
    ("9eeb28f", "2023-08-30", "V2: Added reflection + JSON structure"),
    ("d315965", "2023-09-24", "V3: Prompt clarified"),
    ("a564e21", "2023-08-29", "V2b: GPT-3.5-Turbo-16k engine"),
    ("4459ef1", "2024-01-28", "V4: GPT-4 Turbo rewrite"),
    ("c32eb54", "2024-07-13", "V5: Few-shot + GPT-4o"),
    ("53ee56f", "2024-07-14", "V6: Few-shot toggleable"),
    ("95a4c24", "2024-12-15", "V7: Added CoT (Let's think step-by-step)"),
    ("cc2fe09", "2024-12-29", "V8: Non-JSON return handling"),
    ("d89a1b8", "2025-05-25", "V9: GPT-4.1 nano"),
    ("dd85f7c", "2025-08-08", "V10: GPT-5"),
]

for commit, date, label in versions:
    print(f"\n{'='*80}")
    print(f"=== {label} ({date}, {commit}) ===")
    print(f"{'='*80}")
    try:
        result = subprocess.run(
            ["git", "show", f"{commit}:extractTextFromPDF.py"],
            capture_output=True, text=True, cwd=r"C:\dev\PromptEngineering", encoding='utf-8'
        )
        content = result.stdout
        
        # Extract the model/engine being used
        for line in content.split('\n'):
            if 'engine=' in line or 'model=' in line.strip()[:6]:
                print(f"  MODEL: {line.strip()}")
            if 'pages_per_set' in line and '=' in line:
                print(f"  {line.strip()}")

        # Extract system prompt section
        if 'system_prompt' in content:
            # Find system_prompt dict
            start = content.find('system_prompt = {')
            if start == -1:
                start = content.find("system_prompt = '''")
                if start == -1:
                    start = content.find("prompts = '''")
            if start >= 0:
                # Get a reasonable chunk
                chunk = content[start:start+600]
                print(f"\n  PROMPT (first 600 chars):")
                for line in chunk.split('\n')[:20]:
                    print(f"    {line}")
        elif "prompts = '''" in content:
            start = content.find("prompts = '''")
            chunk = content[start:start+500]
            print(f"\n  PROMPT:")
            for line in chunk.split('\n')[:15]:
                print(f"    {line}")
    except Exception as e:
        print(f"  Error: {e}")
