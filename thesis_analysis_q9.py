"""Q9: Paper processing timeline - papers per month analysis."""
import subprocess
import re
from collections import Counter, OrderedDict

result = subprocess.run(
    ["git", "log", "--all", "--oneline", "--format=%ad %s", "--date=format:%Y-%m"],
    capture_output=True, text=True, cwd=r"C:\dev\PromptEngineering", encoding='utf-8'
)

lines = result.stdout.strip().split('\n')

# Count papers added per month
paper_months = Counter()
paper_events = []

for line in lines:
    if not line.strip():
        continue
    parts = line.split(' ', 1)
    if len(parts) < 2:
        continue
    month = parts[0]
    msg = parts[1]
    
    # Match paper additions
    paper_match = re.search(r'(?:paper|Paper|ID|id)[\s:]*(\d+)', msg, re.IGNORECASE)
    if paper_match and ('added' in msg.lower() or 'paper id' in msg.lower() or 'paper id' in msg.lower()):
        paper_id = paper_match.group(1)
        paper_months[month] += 1
        paper_events.append((month, paper_id, msg.strip()))

# Also count "Added section" commits (early pattern additions)
section_months = Counter()
for line in lines:
    if not line.strip():
        continue
    parts = line.split(' ', 1)
    if len(parts) < 2:
        continue
    month = parts[0]
    msg = parts[1]
    if 'added section' in msg.lower():
        section_months[month] += 1

print("=== Q9: Paper Processing Timeline ===")
print("\nPapers added per month:")
for month in sorted(paper_months.keys()):
    bar = "#" * paper_months[month]
    print(f"  {month}: {paper_months[month]:3d} papers {bar}")

total = sum(paper_months.values())
print(f"\nTotal paper commits: {total}")

print("\nSection additions per month (early pattern work):")
for month in sorted(section_months.keys()):
    bar = "#" * section_months[month]
    print(f"  {month}: {section_months[month]:3d} sections {bar}")

# Also count ALL commits per month
all_months = Counter()
for line in lines:
    if not line.strip():
        continue
    parts = line.split(' ', 1)
    if len(parts) >= 1:
        all_months[parts[0]] += 1

print("\nTotal commits per month (overall project activity):")
for month in sorted(all_months.keys()):
    bar = "#" * (all_months[month] // 2)
    print(f"  {month}: {all_months[month]:3d} commits {bar}")

# Model timeline
print("\n=== Model Evolution Timeline ===")
model_changes = [
    ("2023-08", "gpt-35-00", "GPT-3.5 (standard)"),
    ("2023-08", "gpt-35-Turbo-16k", "GPT-3.5 Turbo 16K"),
    ("2024-01", "GPT-4 Turbo", "GPT-4 Turbo (128K context)"),
    ("2024-07", "GPT-4o", "GPT-4o"),
    ("2025-04", "GPT-4.1 / 4.5-preview / DeepSeek-R1 / Grok-3", "Multi-model"),
    ("2025-05", "GPT-4.1-nano", "GPT-4.1 nano"),
    ("2025-08", "GPT-5", "GPT-5"),
    ("2025-12", "GPT-5.1 / GPT-5.2", "GPT-5.1 & GPT-5.2"),
]
for date, model, desc in model_changes:
    print(f"  {date}: {desc} ({model})")
