# PEIL Evaluation Criteria - Extended Reference

This document provides detailed guidance for each evaluation criterion.

## 1. Clarity and Coherence (30%)

### What to Look For

**Language Clarity**
- Are sentences easy to understand on first read?
- Is technical jargon defined or appropriate for the audience?
- Are pronouns unambiguous (what does "it" refer to)?

**Logical Flow**
- Do instructions follow a natural sequence?
- Are prerequisites mentioned before dependent steps?
- Is there a clear beginning, middle, and end?

**Structural Organization**
- Are sections clearly delineated?
- Do headings accurately describe content?
- Is formatting consistent (bullets, numbering)?

### Red Flags
- Run-on sentences
- Nested conditionals ("If X, unless Y, but when Z...")
- Undefined acronyms
- Contradictory instructions

### Example Feedback

**Good**: "The prompt uses clear section headers and numbered steps that follow a logical progression from context to execution."

**Needs Work**: "The instructions mix setup requirements with execution steps. Consider separating 'Prerequisites' from 'Steps to Follow'."

---

## 2. Completeness and Comprehensiveness (25%)

### PEIL Component Checklist

| Component | Present? | Quality |
|-----------|----------|---------|
| Role | □ | 1-5 |
| Clear Context | □ | 1-5 |
| Broken Down Questions | □ | 1-5 |
| Specific Instructions | □ | 1-5 |
| Conciseness Definition | □ | 1-5 |
| Prompting Technique | □ | 1-5 |
| Desired Output | □ | 1-5 |

### Coverage Assessment

**Task Coverage**
- Are all aspects of the task addressed?
- Are edge cases considered?
- Are error conditions handled?

**Audience Considerations**
- Is the expertise level appropriate?
- Are assumptions stated?
- Is necessary background provided?

### Red Flags
- Missing output format specification
- No error handling guidance
- Undefined scope boundaries
- Assumed knowledge without context

---

## 3. Relevance and Applicability (20%)

### Alignment Assessment

**Purpose Alignment**
- Does the prompt achieve its stated goal?
- Is every instruction necessary for the task?
- Are there irrelevant tangents?

**Practical Applicability**
- Can this prompt be used as-is?
- Are requirements realistic?
- Is the expected output achievable?

### Context Appropriateness

| Question | Yes | Partial | No |
|----------|-----|---------|-----|
| Appropriate for target LLM? | | | |
| Suitable complexity level? | | | |
| Realistic constraints? | | | |
| Domain-appropriate language? | | | |

### Red Flags
- Instructions that don't serve the goal
- Unrealistic expectations (e.g., "always be 100% accurate")
- Mismatched complexity (expert instructions for simple task)

---

## 4. Creativity and Originality (15%)

### Innovation Indicators

**Novel Approaches**
- Unique combination of techniques
- Creative constraint design
- Innovative output formats
- Original problem decomposition

**Effective Adaptations**
- Customized standard techniques
- Domain-specific modifications
- Creative examples

### Creativity Levels

| Level | Description | Example |
|-------|-------------|---------|
| 5 | Highly innovative | Novel technique combination for unique problem |
| 4 | Creative adaptation | Standard technique with clever modifications |
| 3 | Competent application | Appropriate technique, well-applied |
| 2 | Basic implementation | Generic application, no customization |
| 1 | Template copy | Unchanged template with filled blanks |

### Note on Creativity
Creativity should serve the goal. Novel approaches that reduce effectiveness should not score highly.

---

## 5. Technical Accuracy (10%)

### Accuracy Checklist

**Factual Correctness**
- [ ] Domain facts are accurate
- [ ] Technical terminology is correct
- [ ] Examples are valid

**Best Practices**
- [ ] Follows PEIL methodology correctly
- [ ] Appropriate technique for task type
- [ ] Proper prompt structure

**Implementation Details**
- [ ] Syntax is correct (Markdown, JSON, etc.)
- [ ] References are valid
- [ ] Instructions are executable

### Common Technical Errors

| Error Type | Example | Impact |
|------------|---------|--------|
| Wrong technique | Using CoT for simple lookup | Reduced efficiency |
| Invalid syntax | Malformed JSON example | Execution failure |
| Incorrect facts | Wrong API endpoint | Wrong results |
| Bad structure | Output format in middle of prompt | Confusion |

---

## Evaluation Workflow

### Phase 1: Quick Scan (1-2 minutes)
1. Identify the prompt's purpose
2. Check for PEIL components
3. Note obvious issues

### Phase 2: Detailed Analysis (5-10 minutes)
1. Score each criterion
2. Document specific examples
3. Identify patterns

### Phase 3: Synthesis (2-3 minutes)
1. Calculate overall score
2. Prioritize recommendations
3. Write summary

---

## Calibration Examples

### High-Scoring Prompt (85-95)
```
Clear role with specific expertise
Well-defined context and constraints
Appropriate technique selection
Detailed but not overwhelming
Specific output format with examples
```

### Medium-Scoring Prompt (60-75)
```
Generic role ("You are an assistant")
Some context, missing constraints
Technique mentioned but not integrated
Either too brief or too verbose
Output format specified but vague
```

### Low-Scoring Prompt (30-50)
```
No clear role
Minimal or no context
No technique or wrong technique
Confusing structure
No output specification
```

---

## Feedback Best Practices

### Be Specific
❌ "Needs more clarity"
✅ "The instruction 'process the data appropriately' is vague. Specify what 'appropriately' means: filtering nulls, normalizing values, etc."

### Be Actionable
❌ "The prompt is incomplete"
✅ "Add an error handling section that specifies what the model should do when input data is missing or malformed."

### Be Constructive
❌ "This technique choice is wrong"
✅ "Consider using Chain-of-Verification instead of basic CoT here, as the task requires high accuracy and the verification step would catch potential errors."

### Prioritize
Focus feedback on:
1. Issues that most impact effectiveness
2. Quick wins (easy fixes, big impact)
3. Patterns rather than one-off issues
