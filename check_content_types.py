import json

def check_content_types():
    with open('prompt-pattern-dictionary/public/data/patterns.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Check for any examples with non-string content
    issues_found = 0
    for i, pattern in enumerate(data):
        for j, example in enumerate(pattern.get('examples', [])):
            if 'content' in example:
                if not isinstance(example['content'], str):
                    print(f'Pattern {i} ({pattern["patternName"]}), Example {j}: content is {type(example["content"])}: {example["content"]}')
                    issues_found += 1
                elif example['content'] is None:
                    print(f'Pattern {i} ({pattern["patternName"]}), Example {j}: content is null')
                    issues_found += 1
            else:
                print(f'Pattern {i} ({pattern["patternName"]}), Example {j}: missing content field')
                issues_found += 1

    print(f'Check complete. Found {issues_found} issues.')

if __name__ == "__main__":
    check_content_types()
