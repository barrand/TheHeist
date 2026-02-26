# Scenario Generation & Validation Workflow

Complete guide for generating, validating, and fixing scenarios.

---

## 🎯 Quick Start

```bash
cd backend/scripts

# 1. Generate a scenario (improved prompts now include validation requirements)
python3 generate_experience.py \
  --scenario museum_gala_vault \
  --roles mastermind safe_cracker hacker \
  --output output/test_scenarios/my_heist.md

# 2. Auto-fix validation issues
python3 auto_fix_scenarios.py output/test_scenarios/my_heist.md

# 3. Validate manually if needed
python3 validate_scenario.py output/test_scenarios/my_heist.md

# 4. Move to production when passing
mv output/test_scenarios/my_heist.md ../experiences/
```

---

## 📁 Directory Structure

```
backend/
├── scripts/
│   ├── output/               # ✅ NOT in git (temporary files)
│   │   └── test_scenarios/   # Generated scenarios before validation
│   ├── generate_experience.py
│   ├── validate_scenario.py
│   ├── auto_fix_scenarios.py
│   └── analyze_test_scenarios.py
└── experiences/              # ✅ IN git (production scenarios)
    ├── generated_museum_gala_vault_2players.md
    └── ...
```

**Workflow**:
1. Generate → `backend/scripts/output/test_scenarios/` (temporary, not in git)
2. Validate & Fix → still in `output/test_scenarios/`
3. Approve → move to `backend/experiences/` (production, in git)

---

## 🔄 Complete Workflow

### Step 1: Generate Scenarios

**Single scenario:**
```bash
python3 generate_experience.py \
  --scenario casino_vault_night \
  --roles mastermind hacker safe_cracker fence \
  --output output/test_scenarios/casino_4players.md
```

**Batch generation (10 random scenarios):**
```bash
# Generate manually with different configs
for i in {1..10}; do
  # Pick random scenario and roles
  python3 generate_experience.py \
    --scenario museum_gala_vault \
    --roles mastermind safe_cracker \
    --output output/test_scenarios/test_${i}.md &
done
wait
```

### Step 2: Auto-Fix All Scenarios

```bash
# Fix all scenarios in the test directory
python3 auto_fix_scenarios.py output/test_scenarios/*.md

# With rollback on failure
python3 auto_fix_scenarios.py output/test_scenarios/*.md --rollback-on-fail

# Limit attempts
python3 auto_fix_scenarios.py output/test_scenarios/*.md --max-attempts 5
```

**What auto-fix can do:**
- ✅ Add missing locations to meet count requirements
- ✅ Add missing tasks to meet count requirements
- ✅ Fix inconsistent location names
- ✅ Remove invalid item references
- ✅ Add handoff tasks for cross-role interaction

**What it can't auto-fix:**
- ❌ Invalid NPC references (needs manual NPC creation)
- ❌ Invalid outcome IDs (needs manual NPC outcome updates)
- ❌ Complex dependency issues

### Step 3: Analyze Results

```bash
# Get detailed report on all test scenarios
python3 analyze_test_scenarios.py
```

**Output**:
- Validation status for each scenario
- List of all issues found
- Common issue patterns
- Player count distribution

### Step 4: Manual Fixes (if needed)

For scenarios that didn't fully auto-fix:

1. **View the validation report:**
   ```bash
   python3 validate_scenario.py output/test_scenarios/my_heist.md
   ```

2. **Open scenario in editor:**
   ```bash
   # The files are in backend/scripts/output/test_scenarios/
   code output/test_scenarios/my_heist.md
   ```

3. **Fix remaining issues manually:**
   - Add missing NPCs if tasks reference non-existent NPCs
   - Add outcome IDs to NPCs if tasks require missing outcomes
   - Adjust task prerequisites if dependencies are broken

4. **Re-validate:**
   ```bash
   python3 validate_scenario.py output/test_scenarios/my_heist.md
   ```

### Step 5: Approve & Deploy

Once a scenario passes validation:

```bash
# Move to production experiences directory
mv output/test_scenarios/my_heist.md ../experiences/generated_my_heist_4players.md

# Commit to git
git add ../experiences/generated_my_heist_4players.md
git commit -m "Add validated my_heist scenario for 4 players"
```

---

## 🔧 Advanced Tools

### Deep Analysis

```bash
# Dependency graph analysis
python3 -c "
from scenario_graph_analyzer import ScenarioGraphAnalyzer, Task
from validate_scenario import ScenarioValidator

validator = ScenarioValidator('output/test_scenarios/my_heist.md')
validator.parse_file()

# Convert to graph analyzer format
tasks = {tid: Task(tid, t.prerequisites, t.type) 
         for tid, t in validator.tasks.items()}

from scenario_graph_analyzer import ScenarioGraphAnalyzer
analyzer = ScenarioGraphAnalyzer(tasks)
result = analyzer.analyze_all()
analyzer.print_analysis(result)
"

# Playability simulation
python3 -c "
from scenario_playability_simulator import PlayabilitySimulator, Task
from validate_scenario import ScenarioValidator

validator = ScenarioValidator('output/test_scenarios/my_heist.md')
validator.parse_file()

tasks = {tid: Task(tid, t.role, t.prerequisites, t.type)
         for tid, t in validator.tasks.items()}

sim = PlayabilitySimulator(tasks, validator.roles)
result = sim.simulate()
sim.print_report(result)
"
```

### Fix Suggestions (Without Applying)

```bash
# Get fix suggestions without modifying files
python3 -c "
from scenario_auto_fixer import AutoFixer
from validate_scenario import ScenarioValidator

validator = ScenarioValidator('output/test_scenarios/my_heist.md')
report = validator.validate_all()

fixer = AutoFixer(validator.tasks)
suggestions = fixer.generate_fixes()
suggestions.print_suggestions()
"
```

---

## 📊 Validation Rules Summary

### CRITICAL (Must Pass) - 13 Rules
1. Valid minigame IDs
2. Proper task ID format
3. Required sections present
4. Task count appropriate for player count
5. Location count appropriate for player count
6. No circular dependencies
7. All tasks reachable from start
8. No orphaned tasks
9. Critical path exists
10. Valid NPC references
11. Valid item references
12. Consistent location names
13. Valid outcome IDs

### IMPORTANT (Should Pass) - 8 Rules
14. Balanced role distribution (2-8 tasks per role)
15. Required roles featured (≥3 tasks)
16. Task type balance (60-70% social)
17. Sufficient cross-role interaction (≥3 handoffs, ≥2 info shares)
18. No isolated roles
19. Early game engagement (all roles within 3 turns)
20. No extended dead time (max 3 idle turns)
21. Distributed workload

### ADVISORY (Nice to Have) - 4 Rules
22. Concurrent task availability
23. Scenario coherence
24. Search task balance (6-10)
25. Item unlock progression

---

## 🎮 Testing New Prompts

After updating `generate_experience.py` with validation requirements:

```bash
# Generate a few test scenarios
python3 generate_experience.py --scenario museum_gala_vault --roles mastermind safe_cracker --output output/test_scenarios/test1.md
python3 generate_experience.py --scenario casino_vault_night --roles mastermind hacker safe_cracker fence --output output/test_scenarios/test2.md
python3 generate_experience.py --scenario train_robbery_car --roles mastermind muscle cat_burglar --output output/test_scenarios/test3.md

# Auto-fix them
python3 auto_fix_scenarios.py output/test_scenarios/test*.md

# Analyze results
python3 analyze_test_scenarios.py

# Check pass rate improvement
# Before prompt updates: 0/10 passed (0%)
# After prompt updates: ? (goal: >70%)
```

---

## 🐛 Troubleshooting

### "Location Count Out of Range"
**Auto-fix**: Adds placeholder locations automatically.
**Manual fix**: Add more location definitions in the `## Locations` section.

### "Invalid NPC References"
**Manual fix only**: Add the missing NPC definition or correct the NPC ID in the task.

### "Inconsistent Location Names"
**Auto-fix**: Standardizes location references to match defined names.
**Manual fix**: Ensure `*Location:*` in tasks exactly matches `- **Name**:` in Locations.

### "Invalid Outcome IDs"
**Manual fix only**: Add the outcome ID to the target NPC's `Information Known` or `Actions Available` section.

### "Too Few Social Interactions"
**Auto-fix**: Adds handoff tasks.
**Manual fix**: Convert some minigame tasks to NPC interactions or searches.

### "Insufficient Cross-Role Interaction"
**Auto-fix**: Adds handoff tasks.
**Manual fix**: Add more 🤝 HANDOFF and 🗣️ INFO tasks between roles.

---

## 📈 Success Metrics

**Target Pass Rates:**
- **Critical issues**: 0 (100% pass)
- **Important issues**: ≤2 per scenario
- **Advisory issues**: ≤3 per scenario

**Current Status** (after recent improvements):
- Location count validation: Fixed (now scales with player count)
- Prompt updates: Added validation requirements
- Auto-fixer: Implemented fix-validate-retry loop

**Next milestone**: 70%+ pass rate on random scenario generation

---

## 💡 Tips

1. **Always auto-fix first** - It handles 80% of common issues automatically
2. **Use analysis tool** - See patterns across multiple scenarios
3. **Check validation early** - Don't wait until scenario is "complete"
4. **Iterate on prompts** - Track which issues persist and update generation prompts
5. **Keep test scenarios separate** - Don't commit to git until validated and approved

---

## 🎯 Goal

**End state**: Generate 10 random scenarios → 8-10 pass validation automatically → manual review for quality → deploy to production

**Current state**: 0/10 pass → needs auto-fix + manual review → deploy

**Progress**: Auto-fix now handles most structural issues. Remaining issues require prompt improvements.
