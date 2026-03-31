"""Examine the PEIL prompts that caused the worst scores to identify structural issues."""
import json
from pathlib import Path

RESULTS_DIR = Path("evaluation/results")

# The 5 patterns where PEIL scored worst vs naive
problem_patterns = [
    "at_calculation_math_word_problems",      # -2.56
    "across_comparison_attendance",            # -2.38
    "at_assessment_opinion_verification",      # -2.25
    "beyond_logical_reasoning_premise_question", # -2.12
    "beyond_hypothesise_theory_of_mind",       # -1.38
]

# Also examine the 3 best PEIL patterns for contrast
good_patterns = [
    "in_refactoring_template_filling",         # +0.69
    "at_assessment_expert_rating",             # +0.50
    "out_output_customisation_knapsack_code",  # +0.38
]

for label, patterns in [("PROBLEM PATTERNS (PEIL scored worse)", problem_patterns), 
                         ("STRONG PATTERNS (PEIL scored better)", good_patterns)]:
    print("=" * 90)
    print(label)
    print("=" * 90)
    
    for pattern_name in patterns:
        pattern_dir = RESULTS_DIR / pattern_name / "gpt-4.1"
        
        # Load naive and PEIL labelled run_1
        naive_file = pattern_dir / "run_1_naive.json"
        peil_file = pattern_dir / "run_1_peil_labelled.json"
        
        if not naive_file.exists() or not peil_file.exists():
            print(f"\n--- {pattern_name}: FILES MISSING ---")
            continue
        
        naive_data = json.loads(naive_file.read_text(encoding="utf-8"))
        peil_data = json.loads(peil_file.read_text(encoding="utf-8"))
        
        print(f"\n{'─' * 90}")
        print(f"PATTERN: {pattern_name}")
        print(f"{'─' * 90}")
        
        print(f"\n  NAIVE PROMPT ({len(naive_data['prompt'])} chars):")
        print(f"  {naive_data['prompt'][:300]}")
        
        print(f"\n  NAIVE OUTPUT ({len(naive_data['output'])} chars):")
        print(f"  {naive_data['output'][:300]}")
        
        print(f"\n  PEIL LABELLED PROMPT ({len(peil_data['prompt'])} chars):")
        print(f"  {peil_data['prompt'][:500]}")
        
        print(f"\n  PEIL LABELLED OUTPUT ({len(peil_data['output'])} chars):")
        print(f"  {peil_data['output'][:300]}")
        
        # Check if task material appears in PEIL prompt
        task_mat = naive_data["pattern"].get("task_material", "")
        if task_mat:
            in_naive = task_mat[:50] in naive_data["prompt"]
            in_peil = task_mat[:50] in peil_data["prompt"]
            print(f"\n  TASK MATERIAL present in naive prompt: {in_naive}")
            print(f"  TASK MATERIAL present in PEIL prompt:  {in_peil}")
        else:
            print(f"\n  TASK MATERIAL: (empty)")
        
        print()
