# Scenario Editor Agent

## Overview

The **Scenario Editor Agent** is an LLM-powered tool that makes surgical, intelligent edits to scenario files based on validation issues. It replaces the previous crude auto-fixer with an AI-powered editor that understands context and makes minimal, targeted fixes.

## Architecture

```
┌─────────────────┐
│ generate_       │
│ experience.py   │──┐
└─────────────────┘  │
                     │
         ┌───────────▼──────────┐
         │ Validation Loop      │
         │ (max 3 attempts)     │
         └───────────┬──────────┘
                     │
         ┌───────────▼──────────┐
         │ validate_scenario.py │
         │ Returns issues       │
         └───────────┬──────────┘
                     │
              Issues Found?
                     │
         ┌───────────▼──────────┐
         │ scenario_editor_     │
         │ agent.py             │
         │ (LLM fixes)          │
         └───────────┬──────────┘
                     │
         ┌───────────▼──────────┐
         │ Re-validate          │
         │ (loop continues)     │
         └──────────────────────┘
```

## Key Features

### 1. Intelligent Fixes
- Uses Gemini 2.5 Flash with temperature 0.3 for precise edits
- Understands the full context of the scenario file
- Makes minimal, surgical changes to fix specific issues
- Preserves all other content exactly as-is

### 2. Priority-Based Fixing
- Fixes CRITICAL issues first
- Sorts by validation rule number for consistent ordering
- Processes top 5 issues per pass (configurable)

### 3. Validation Integration
- Seamlessly integrated into `generate_experience.py --validate`
- Automatically triggers on validation failures
- Re-validates after each fix attempt
- Exits gracefully after 3 attempts if issues persist

## ID-Only Reference Enforcement

The system now **strictly enforces** ID-only references:

### Task Location Format
```markdown
✅ CORRECT:
- *Location:* `safe_house`
- *Location:* `bank_lobby`

❌ WRONG:
- *Location:* Safe House
- *Location:* Bank Lobby
```

### Task NPC Format
```markdown
✅ CORRECT:
- *NPC:* `lobby_guard_brenda` (Guard Name)

❌ WRONG:
- *NPC:* lobby_guard_brenda
- *NPC:* Brenda Jenkins
```

### Prerequisites Format
```markdown
✅ CORRECT:
- Task `MM1`
- Outcome `guard_distracted`
- Item `keycard`

❌ WRONG:
- Task MM1
- Outcome guard_distracted
```

## Usage

### Via Generation Script (Recommended)
```bash
python backend/scripts/generate_experience.py \
  --scenario museum_gala_vault \
  --roles mastermind grifter \
  --output "output/test.md" \
  --validate
```

The `--validate` flag automatically:
1. Validates the generated scenario
2. Calls Editor Agent if issues found
3. Re-validates after fixes
4. Repeats up to 3 times

### Standalone Testing
```bash
python backend/scripts/scenario_editor_agent.py scenario_file.md --max-issues 5
```

## Implementation Details

### ScenarioEditorAgent Class
```python
class ScenarioEditorAgent:
    def fix_issues(
        self,
        scenario_file: Path,
        issues: List[ValidationIssue],
        max_issues: int = 5
    ) -> List[EditResult]
```

**Key Methods:**
- `fix_issues()`: Fixes multiple validation issues
- `_fix_single_issue()`: Fixes one issue using LLM
- `_build_fix_prompt()`: Constructs detailed prompt for LLM

### EditResult Dataclass
```python
@dataclass
class EditResult:
    success: bool
    issue_fixed: str
    changes_made: str
    error: Optional[str] = None
```

## Prompt Engineering

The Editor Agent uses a carefully crafted prompt that includes:

1. **Issue Details**: Rule number, level, title, description
2. **Current Scenario**: Full file contents for context
3. **Fix Instructions**: ID-only reference rules, format requirements
4. **Output Format**: Return complete fixed file without commentary

### Critical Prompt Rules
- Use temperature 0.3 for consistent, precise edits
- Explicitly forbid markdown code fences in output
- Enforce ID-only reference format
- Request minimal, surgical changes only

## Validation Loop in generate_experience.py

```python
max_attempts = 3
attempt = 0
editor = ScenarioEditorAgent()

while attempt < max_attempts:
    attempt += 1
    
    # Run validation
    validator = ScenarioValidator(Path(output_path))
    report = validator.validate_all()
    
    if report.passed:
        print("✅ VALIDATION PASSED!")
        break
    
    # Get critical issues
    critical_issues = [i for i in report.issues if i.level == ValidationLevel.CRITICAL]
    
    # Use Editor Agent to fix
    results = editor.fix_issues(Path(output_path), critical_issues, max_issues=5)
    
    success_count = sum(1 for r in results if r.success)
    print(f"Fixed {success_count}/{len(results)} issues")
```

## Parser Updates

The validator parser was updated to handle ID-only references:

### Location Extraction
```python
# Strip backticks from location references
location_match = re.search(r'- \*Location:\*\s+(.+)', task_text)
if location_match:
    location = location_match.group(1).strip()
    # Strip backticks (ID-only format: `bank_lobby`)
    if location.startswith('`') and location.endswith('`'):
        location = location[1:-1]
```

### Location Definition Parsing
Supports two formats:

**Format 1**: Traditional
```markdown
### Location Name
- **ID**: `loc_id`
```

**Format 2**: Nested (LLM-generated)
```markdown
### Category Header
- **Location Name**
  - **ID**: `loc_id`
  - **Name**: Location Name
```

## Test Results

### Successful Generation Example
```
🎮 Generating heist experience...
   Scenario: museum_gala_vault
   Roles: mastermind, grifter

✅ Generated 4214 words

--- Validation Attempt 1/3 ---
❌ VALIDATION FAILED
   Critical: 2
   Important: 2
   
   Critical Issues:
     • [5] Location Count Out of Range
     • [11] Invalid Item References

🤖 Scenario Editor Agent fixing issues...
   Fixed 2/2 issues

--- Validation Attempt 2/3 ---
✅ VALIDATION PASSED!
   Advisory: 0
```

## Files Modified

### New Files
- `backend/scripts/scenario_editor_agent.py` - Main editor agent

### Modified Files
- `backend/scripts/generate_experience.py` - Integrated editor into validation loop
- `backend/scripts/validate_scenario.py` - Updated parser for ID-only references
- `design/dependency_tree_design_guide.md` - Updated with ID-only rules

### Deprecated Files
- `backend/scripts/auto_fix_scenarios.py` - Replaced by Editor Agent

## Future Improvements

### Potential Enhancements
1. **Iterative Refinement**: Allow editor to make multiple passes on same issue
2. **Issue-Specific Prompts**: Customize prompt per validation rule
3. **Diff Preview**: Show before/after comparison
4. **Batch Mode**: Process multiple scenarios in parallel
5. **Learning Mode**: Track common issues and improve prompts

### Known Limitations
1. LLM may occasionally fail on complex structural issues
2. Large files (>10K lines) may hit context limits
3. Some issues may require manual intervention
4. Cannot fix issues requiring external data (missing NPCs, etc.)

## Cost Considerations

### Per-Scenario Cost
- **Generation**: ~$0.01 (Gemini 2.5 Flash)
- **Validation Loop**: ~$0.005 per attempt
- **Editor Agent**: ~$0.01 per fix attempt
- **Total**: ~$0.03-$0.05 per scenario

### Optimization Tips
- Set `max_issues=3` to reduce API calls
- Use `max_attempts=2` if acceptable
- Monitor token usage in logs

## Monitoring

### Success Metrics
- Fix success rate: # successful fixes / # attempts
- Validation pass rate: # scenarios passing / # generated
- Average attempts to pass: sum(attempts) / # scenarios

### Logging
The Editor Agent logs:
- Issue being fixed
- LLM response length
- Success/failure status
- Error messages if any

## Summary

The Scenario Editor Agent represents a significant upgrade to the validation system:

✅ **Intelligent**: Uses LLM understanding vs pattern matching  
✅ **Precise**: Makes surgical edits, preserves context  
✅ **Integrated**: Seamless validation loop  
✅ **Enforced**: ID-only references strictly required  
✅ **Tested**: Successfully validates generated scenarios  

This system dramatically improves scenario generation quality and reduces manual intervention.
