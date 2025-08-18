# Template Logic Updates for categorisation_write_up.py

## Summary of Changes

The `categorisation_write_up.py` file has been updated to support two distinct template modes based on command-line arguments:

### 1. Logic Overview Mode (only `-logic` provided)
- **Uses**: `section_introduction` template
- **Purpose**: Generate comprehensive overview of a logic layer
- **Content includes**:
  - Section header with logic name and subtitle
  - Long introduction to the logic
  - Enumerated list of categories under this logic

### 2. Category-Specific Mode (`-logic` and `-category` provided)
- **Uses**: `category_subsection` template  
- **Purpose**: Generate detailed write-up for a specific category
- **Content includes**:
  - Subsection header with category name
  - Category role description under the logic
  - PP analysis (introduction, function, benefits, reusability)
  - Human feeling response
  - Reuse guidance
  - LaTeX table of representative prompt patterns

## Key Changes Made

### 1. Modified `generate_writeup` method
- Made `category` parameter optional (can be `None`)
- Added logic to route to different prompt building methods based on presence of category
- Updated method signature and documentation

### 2. Replaced single prompt builder with two specialized methods
- **`_build_logic_writeup_prompt()`**: For logic overview mode
- **`_build_category_writeup_prompt()`**: For category-specific mode

### 3. Updated task execution logic
- Modified `execute_writeup_task()` to handle optional category
- Auto-generates appropriate default tasks based on mode

### 4. Enhanced documentation and help
- Updated argument help text to clarify optional nature of category
- Added examples showing both modes
- Enhanced template structure documentation

### 5. Updated examples in help text
```bash
# Logic overview (uses section_introduction template)
python categorisation_write_up.py -logic "Beyond"

# Category-specific write-up (uses category_subsection template)  
python categorisation_write_up.py -logic "Beyond" -category "prediction"
```

## Template Selection Logic

The system now automatically selects the appropriate template:

```python
if category:
    # Generate category-specific write-up using category_subsection template
    prompt = self._build_category_writeup_prompt(logic, category, task, context)
else:
    # Generate logic overview write-up using section_introduction template
    prompt = self._build_logic_writeup_prompt(logic, task, context)
```

## Benefits

1. **Flexible Usage**: Supports both high-level logic overviews and detailed category analysis
2. **Template Consistency**: Ensures appropriate template structure is used for each mode
3. **Backward Compatibility**: Existing category-specific functionality remains unchanged
4. **Clear Separation**: Distinct prompt building methods for cleaner code organization

## Usage Examples

### Generate Logic Overview
```bash
python categorisation_write_up.py -logic "Beyond"
```

### Generate Category-Specific Write-up
```bash
python categorisation_write_up.py -logic "Beyond" -category "prediction"
```

### With Custom Task
```bash
python categorisation_write_up.py -logic "Beyond" -task "Generate comprehensive overview focusing on innovation aspects"
```

The updated system now properly implements the template selection logic you requested, ensuring that the appropriate LaTeX template structure is used based on the command-line arguments provided.
