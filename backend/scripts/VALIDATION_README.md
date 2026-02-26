# Scenario Validation System

## Overview

This validation system ensures generated heist scenarios are **balanced, fun, and completely playable** with no dead ends, orphaned tasks, or extended player idle time.

## Single Source of Truth

**📖 `design/dependency_tree_design_guide.md`** is the authoritative specification for:
- File format requirements
- Task types and formats
- NPC, item, and location specifications
- Validation rules (25 rules spanning critical, important, and advisory levels)
- Anti-patterns to avoid

All validation tools reference this document as ground truth.

---

## Tools

### 1. `validate_scenario.py` - Core Validator

**Purpose**: Validates scenario markdown files against all design guide requirements.

**Usage**:
```bash
python validate_scenario.py <experience_file.md>
python validate_scenario.py backend/experiences/generated_museum_4players.md
```

**Checks** (25 validation rules):

**CRITICAL (Must Pass)**:
- ✅ Valid minigame IDs from roles.json
- ✅ Proper task ID format
- ✅ Required sections present
- ✅ Task count appropriate for player count
- ✅ Location count appropriate for player count (scales 4-15)
- ✅ No circular dependencies (handled by graph analyzer)
- ✅ All tasks reachable from start
- ✅ No orphaned tasks
- ✅ Valid NPC references
- ✅ Valid item references
- ✅ Consistent location names
- ✅ Valid outcome IDs

**IMPORTANT (Should Pass)**:
- ⚠️ Balanced role distribution (2-8 tasks per role)
- ⚠️ Task type balance (60-70% social interactions)
- ⚠️ Sufficient cross-role interaction (handoffs, info shares)
- ⚠️ Early game engagement (all roles start within 3 turns)
- ⚠️ No extended dead time (max 3 consecutive idle turns)
- ⚠️ Distributed workload across timeline

**ADVISORY (Nice to Have)**:
- 💭 Search task balance (6-10 recommended)
- 💭 Concurrent task availability
- 💭 Item unlock progression

**Output**:
```
================================================================================
SCENARIO VALIDATION REPORT: generated_museum_4players.md
================================================================================

✅ PASSED | Critical: 0 | Important: 2 | Advisory: 1

IMPORTANT ISSUES (2):
--------------------------------------------------------------------------------

[16] Too Many Social Interactions
  Social tasks: 72.0% (target: 60-70%)
  ...
```

---

### 2. `scenario_graph_analyzer.py` - Dependency Graph Analysis

**Purpose**: Analyzes task dependency graphs for structural issues.

**Usage**:
```python
from scenario_graph_analyzer import ScenarioGraphAnalyzer, Task

tasks = {
    "MM1": Task("MM1", [], "npc_llm"),
    "MM2": Task("MM2", [{"type": "task", "id": "MM1"}], "search"),
}

analyzer = ScenarioGraphAnalyzer(tasks)
result = analyzer.analyze_all()
analyzer.print_analysis(result)
```

**Detects**:
- 🔄 **Circular dependencies** (Task A → B → A)
- 🏝️ **Orphaned tasks** (unreachable from start)
- 🚫 **Dead-end tasks** (don't unlock anything)
- 🎯 **Critical path** (longest path through graph)
- ⚡ **Parallel opportunities** (tasks that can be done simultaneously)

**Output**:
```
================================================================================
DEPENDENCY GRAPH ANALYSIS
================================================================================

📊 Overview:
  Total tasks: 6
  Start tasks: 3
  Critical path length: 4

🔄 CYCLES DETECTED (1):
  1. MM3 → SC2 → MM3
  ⚠️  These circular dependencies make tasks impossible to complete!

✅ No orphaned tasks
```

---

### 3. `scenario_playability_simulator.py` - Gameplay Simulation

**Purpose**: Simulates actual gameplay to validate player experience.

**Usage**:
```python
from scenario_playability_simulator import PlayabilitySimulator, Task

tasks = { ... }
roles = ["mastermind", "safe_cracker", "hacker"]

sim = PlayabilitySimulator(tasks, roles)
result = sim.simulate(strategy="round_robin")
sim.print_report(result)
```

**Simulates**:
- Turn-by-turn task completion
- Player availability and idle time
- Workload distribution across timeline
- Concurrent task opportunities

**Validates**:
- Rule 19: Early game engagement (all roles active in first 3 turns)
- Rule 20: No extended dead time (max 3 consecutive idle turns)
- Rule 21: Distributed workload (not all tasks at end)
- Rule 22: Concurrent availability (≥50% players have tasks)

**Output**:
```
================================================================================
PLAYABILITY SIMULATION REPORT
================================================================================

✅ PLAYABLE
Total turns: 15

📊 Per-Role Summary:
Role                 Tasks      Max Idle     Timeline
--------------------------------------------------------------------------------
mastermind           5          2            1, 3, 7, 10, 14
safe_cracker         4          3            2, 6, 11, 15
hacker               4          2            4, 8, 9, 13

⚠️  WARNINGS (1):
1. Rule 20: safe_cracker had 4 consecutive idle turns (max 3 recommended)
```

---

### 4. `scenario_auto_fixer.py` - Fix Suggestions

**Purpose**: Generates automatic fix suggestions for detected issues.

**Usage**:
```python
from scenario_auto_fixer import AutoFixer

fixer = AutoFixer(tasks, graph_analysis, playability_result)
suggestions = fixer.generate_fixes()
suggestions.print_suggestions()
```

**Suggests Fixes For**:
- 🔄 Circular dependencies (which prerequisite to remove)
- 🏝️ Orphaned tasks (connect to main flow or make start task)
- 🚫 Dead-end tasks (add dependencies or mark optional)
- ⏰ Late-starting roles (remove prerequisites for early engagement)
- 💤 Extended idle time (add parallel tasks)
- 📊 Uneven workload (redistribute prerequisites across timeline)

**Output**:
```
================================================================================
AUTO-FIX SUGGESTIONS
================================================================================

🚨 CRITICAL FIXES (1):
--------------------------------------------------------------------------------

1. Circular dependency detected: MM3 → SC2 → MM3
   💡 Remove prerequisite: Task MM3 should NOT depend on SC2

⚠️  IMPORTANT: These are SUGGESTIONS only. Human review required.
```

---

### 5. `test_scenario_generation.py` - Test Harness

**Purpose**: Bulk test scenario generation and validation.

**Usage**:
```bash
# Generate and validate 10 random scenarios
python test_scenario_generation.py --count 10

# Test specific scenarios
python test_scenario_generation.py --count 5 --scenarios museum_gala_vault train_robbery

# Custom output directory
python test_scenario_generation.py --count 10 --output /path/to/output
```

**Process**:
1. Generates random scenario configurations (scenario + player count + roles)
2. Calls `generate_experience.py` for each
3. Validates each with full validation suite
4. Reports pass/fail statistics and common issues

**Output**:
```
================================================================================
TEST SUITE SUMMARY
================================================================================

Total scenarios tested: 10
✅ Passed: 7 (70%)
❌ Failed: 3 (30%)

❌ Failed Scenarios:
--------------------------------------------------------------------------------

  museum_gala_vault (6 players)
    Roles: mastermind, hacker, safe_cracker, driver, lookout, fence
    Issues: 2
      • Location Count Out of Range
      • Invalid Item References

📊 Most Common Issues:
--------------------------------------------------------------------------------
  4x: Task Count Out of Range
  3x: Location Count Out of Range
  2x: Too Many Social Interactions
```

---

## Integration

### In `generate_experience.py`

Add `--validate` flag to automatically validate after generation:

```bash
python generate_experience.py \
  --scenario museum_gala_vault \
  --roles mastermind hacker safe_cracker \
  --validate
```

If validation fails, the script exits with error code 1.

---

## Workflow

### 1. Generate a Scenario

```bash
python generate_experience.py \
  --scenario museum_gala_vault \
  --roles mastermind safe_cracker hacker fence \
  --output backend/experiences/my_heist.md \
  --validate
```

### 2. Review Validation Report

Check for critical issues that must be fixed.

### 3. Deep Analysis (If Needed)

```bash
# Detailed dependency graph analysis
python scenario_graph_analyzer.py backend/experiences/my_heist.md

# Playability simulation
python scenario_playability_simulator.py backend/experiences/my_heist.md

# Get fix suggestions
python scenario_auto_fixer.py backend/experiences/my_heist.md
```

### 4. Fix Issues

Manually edit the scenario file based on suggestions.

### 5. Re-validate

```bash
python validate_scenario.py backend/experiences/my_heist.md
```

Repeat until all critical issues are resolved.

---

## Thresholds & Tuning

All validation thresholds are defined in `design/dependency_tree_design_guide.md`:

- **Task counts**: 30-40 tasks (3-7 players), 40-50 tasks (8-12 players)
- **Location counts**: 12-18 locations
- **Role balance**: 2-8 tasks per role
- **Social interaction**: 60-70% of tasks
- **Handoffs**: ≥3 recommended
- **Info shares**: ≥2 recommended
- **Search tasks**: 6-10 recommended
- **Max idle time**: 3 consecutive turns
- **Early engagement**: All roles within first 3 turns
- **Workload distribution**: No role should have >50% tasks in final 25%

To adjust thresholds, update the design guide and corresponding validation rule implementations.

---

## Architecture

```
design/dependency_tree_design_guide.md  ← Single source of truth
    ↓
validate_scenario.py  ← Validates all structural rules
    ├─→ scenario_graph_analyzer.py  ← Checks dependency graph
    ├─→ scenario_playability_simulator.py  ← Simulates gameplay
    └─→ scenario_auto_fixer.py  ← Suggests fixes
        ↓
test_scenario_generation.py  ← Bulk testing harness
        ↓
generate_experience.py  ← Integrated validation (--validate flag)
```

---

## Future Enhancements

Potential improvements:
- **Auto-apply fixes**: Automatically modify scenario files (with backup)
- **Difficulty scoring**: Calculate scenario difficulty based on metrics
- **Player count scaling**: Validate scenarios scale properly with player counts
- **Narrative coherence**: Validate story flow and NPC interactions
- **Web UI**: Visual validator with interactive fix suggestions
- **CI/CD integration**: Automated validation on all scenario commits

---

## Troubleshooting

### "Validation found critical issues"

1. Run validator to see detailed report
2. Use auto-fixer to get suggestions
3. Manually fix critical issues (circular deps, invalid references, etc.)
4. Re-run validator until passed

### "All tasks are orphaned"

Likely a circular dependency involving all tasks, or no start tasks defined. Use graph analyzer to detect cycles.

### "Validation error: Module not found"

Ensure you're running from `backend/scripts/` directory, or add it to PYTHONPATH:
```bash
cd backend/scripts
python validate_scenario.py ../experiences/my_heist.md
```

### "Generation succeeded but validation fails"

This is expected! The LLM may generate syntactically correct but structurally flawed scenarios. Use the validation report to identify and fix issues.

---

## Summary

This validation system ensures **every scenario is playable, balanced, and fun** by:
1. ✅ Enforcing structural correctness (valid IDs, references, formats)
2. 🔄 Detecting dependency issues (cycles, orphans, dead ends)
3. ⏱️ Simulating gameplay to catch pacing problems
4. 🤖 Suggesting automatic fixes for common issues
5. 📊 Bulk testing for quality assurance

**Result**: High-quality scenarios with no dead ends, good player engagement, and balanced workload distribution!
