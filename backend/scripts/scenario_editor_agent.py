"""
Scenario Editor Agent

LLM-powered agent that makes surgical edits to scenario files based on validation issues.
Uses Gemini to understand context and make intelligent, minimal fixes.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import google.generativeai as genai

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import GEMINI_API_KEY, GEMINI_EXPERIENCE_MODEL
from validate_scenario import ValidationIssue, ValidationLevel

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)


@dataclass
class EditResult:
    """Result of an edit operation"""
    success: bool
    issue_fixed: str
    changes_made: str
    error: Optional[str] = None


class ScenarioEditorAgent:
    """
    LLM-powered agent that makes surgical edits to scenario files.
    
    Takes validation issues and the scenario file, makes minimal targeted fixes.
    """
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or GEMINI_EXPERIENCE_MODEL
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": 0.3,  # Lower temperature for precise edits
                "response_mime_type": "text/plain"
            }
        )
        self._role_minigames: Dict[str, List[str]] = self._load_role_minigames()
        logger.info(f"Scenario Editor Agent initialized with {self.model_name}")
    
    def fix_issues(
        self,
        scenario_file: Path,
        issues: List[ValidationIssue],
        max_issues: int = 5
    ) -> List[EditResult]:
        """
        Fix multiple validation issues
        
        Args:
            scenario_file: Path to scenario markdown file
            issues: List of validation issues to fix
            max_issues: Maximum number of issues to fix in one pass
        
        Returns:
            List of edit results
        """
        # Read current scenario
        scenario_content = scenario_file.read_text()
        
        # Sort issues by priority (CRITICAL first)
        sorted_issues = sorted(
            issues,
            key=lambda i: (i.level != ValidationLevel.CRITICAL, i.rule_number)
        )
        
        results = []
        
        # Fix top N issues
        for issue in sorted_issues[:max_issues]:
            logger.info(f"Attempting to fix: [{issue.rule_number}] {issue.title}")
            
            result = self._fix_single_issue(scenario_file, scenario_content, issue)
            results.append(result)
            
            if result.success:
                # Reload content for next fix
                scenario_content = scenario_file.read_text()
                logger.info(f"✓ Fixed: {issue.title}")
            else:
                logger.warning(f"✗ Could not fix: {issue.title} - {result.error}")
        
        return results
    
    def _fix_single_issue(
        self,
        scenario_file: Path,
        scenario_content: str,
        issue: ValidationIssue
    ) -> EditResult:
        """
        Fix a single validation issue using LLM
        
        Returns:
            EditResult with success status and details
        """
        try:
            # Build prompt for the fix
            prompt = self._build_fix_prompt(scenario_content, issue)
            
            # Get fixed version from LLM
            response = self.model.generate_content(prompt)
            fixed_content = response.text.strip()
            
            # Remove markdown code fences if present
            if fixed_content.startswith("```"):
                lines = fixed_content.split("\n")
                # Remove first line (```markdown or similar)
                if lines[0].startswith("```"):
                    lines = lines[1:]
                # Remove last line (```)
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                fixed_content = "\n".join(lines)
            
            # Save the fixed version
            scenario_file.write_text(fixed_content)
            
            return EditResult(
                success=True,
                issue_fixed=f"[{issue.rule_number}] {issue.title}",
                changes_made=f"Applied fix for: {issue.title}"
            )
            
        except Exception as e:
            logger.error(f"Error fixing issue: {e}")
            return EditResult(
                success=False,
                issue_fixed=f"[{issue.rule_number}] {issue.title}",
                changes_made="",
                error=str(e)
            )
    
    # Complete NPC block from the handcrafted museum_gala_vault.md reference —
    # shown to the LLM when fixing NPC quality issues (Rules 36-39).
    _NPC_REFERENCE_BLOCK = """\
REFERENCE — Complete NPC block (museum_gala_vault.md gold standard):

### Security Guard - Marcus Romano
- **ID**: `security_guard`
- **Role**: Museum Security Guard
- **Location**: Grand Hall
- **Age**: 45
- **Gender**: male
- **Ethnicity**: White
- **Clothing**: Navy security uniform with badge and radio
- **Expression**: bored
- **Attitude**: lonely, chatty
- **Details**: Holding clipboard, wearing glasses
- **Personality**: Bored and lonely on the night shift. Loves sports and misses the excitement of his old job. Gets chatty when someone shows interest in his stories. Genuinely believes nothing interesting ever happens at the museum.
- **Relationships**: Works under Dr. Elena Vasquez's department — respects her but finds the gala crowd stuffy. Friendly with the other guards but prefers working alone.
- **Story Context**: Has been stationed at the vault exhibit all week; his patrol schedule is the key intel the Mastermind needs.
- **Information Known**:
  - `vault_location` HIGH: The Eye of Orion jewels are in the new vault in the basement, east wing
  - `patrol_schedule` MEDIUM: He leaves the vault area around 9 PM for his break
- **Actions Available**:
  - `leave_post` HIGH: Can be convinced to leave his post early for a smoke break — he's bored and would welcome an excuse
- **Cover Story Options**:
  - `new_guard`: "New security guard, just transferred here — first night on the job" -- (treats you as a peer, shares tips)
  - `caterer`: "Catering staff working the gala event tonight" -- (friendly to service workers but guarded about security)
  - `tourist`: "Enthusiastic tourist who thinks this is a wax museum" -- (bewildered by this person, not sharing anything)
"""

    def _load_role_minigames(self) -> Dict[str, List[str]]:
        """Load per-role valid minigame IDs from shared_data/roles.json."""
        try:
            roles_path = Path(__file__).parent.parent.parent / "shared_data" / "roles.json"
            with open(roles_path) as f:
                data = json.load(f)
            return {
                role["role_id"]: [mg["id"] for mg in role.get("minigames", [])]
                for role in data.get("roles", [])
            }
        except Exception as e:
            logger.warning(f"[editor] Could not load roles.json for minigame reference: {e}")
            return {}

    def _format_minigame_reference(self) -> str:
        """Format a per-role minigame ID reference table for injection into the prompt."""
        if not self._role_minigames:
            return ""
        lines = ["VALID MINIGAME IDs BY ROLE (ONLY use IDs from this table):"]
        for role_id, mgs in sorted(self._role_minigames.items()):
            if mgs:
                lines.append(f"  - {role_id}: {', '.join(mgs)}")
        lines.append("NEVER use a minigame ID not listed above for the task's assigned role.")
        return "\n".join(lines)

    def _get_fix_instructions(self, issue: ValidationIssue) -> str:
        """Return targeted fix instructions for each rule the editor handles."""
        rule = issue.rule_number

        # --- Structural rules ---
        if rule == 16:
            minigame_ref = self._format_minigame_reference()
            return (
                "Replace some `npc_llm` tasks with `minigame` tasks to bring social interactions below 60%.\n"
                "CRITICAL: Only use minigame IDs from the per-role table below — NEVER invent IDs.\n"
                "For each task you change:\n"
                "  - Change `*Type:*` from `npc_llm` to `minigame`\n"
                "  - Replace `*NPC:*` and `*Target Outcomes:*` lines with `*Minigame:* `valid_id_here``\n"
                "  - Keep all prerequisite lines exactly as-is — do NOT reorder or remove any Task/Outcome prereqs.\n"
                f"\n{minigame_ref}"
            )
        if rule == 17:
            return (
                "Add new handoff and/or info_share tasks until Rule 17 minimums are met (≥3 handoff, ≥2 info_share).\n"
                "DO NOT modify or remove any existing tasks or their prerequisites.\n"
                "Add NEW tasks using these exact formats:\n\n"
                "HANDOFF TASK FORMAT:\n"
                "#### [ROLE_CODE][N] - Hand off [item] to [target_role]\n"
                "- *Type:* handoff\n"
                "- *Assigned Role:* `role_id`\n"
                "- *Location:* `location_id`\n"
                "- *Handoff Item:* `item_id`\n"
                "- *Handoff To Role:* `target_role_id`\n"
                "- *Prerequisites:* Task `PREV_TASK_ID`\n\n"
                "INFO_SHARE TASK FORMAT:\n"
                "#### [ROLE_CODE][N] - Share intelligence with the team\n"
                "- *Type:* info_share\n"
                "- *Assigned Role:* `role_id`\n"
                "- *Location:* `location_id`\n"
                "- *Info Description:* Brief note on what is shared\n"
                "- *Prerequisites:* Task `PREV_TASK_ID`, Outcome `real_npc_outcome_id`\n"
                "  (The Outcome prereq MUST reference an existing NPC information_known or actions_available ID)\n"
            )
        if rule == 28:
            return (
                "Fix dead-end tasks by chaining them into the task sequence — DO NOT remove or reorder any tasks.\n"
                "For each dead-end task ID listed in the issue details:\n"
                "  1. Find the NEXT task in that role's sequence (the task with the next letter/number).\n"
                "  2. Add `Task `DEAD_END_TASK_ID`` to the prerequisites of that next task.\n"
                "  3. If the dead-end task is the last task for a role, add it as a prereq to the role's escape task.\n"
                "  DO NOT change the dead-end task itself — only edit the task that comes AFTER it.\n"
            )

        # --- NPC quality rules ---
        if rule == 36:
            return (
                "Fill in the MISSING NPC fields identified above to match the reference block.\n"
                "Write grounded, specific content for THIS scenario's setting — no generic placeholders.\n"
                "- personality: 2-3 sentences about their emotional state, job, and quirks right now.\n"
                "- relationships: 1-2 sentences cross-referencing OTHER NPCs in this scenario by name.\n"
                "- information_known: At least 1 entry as: `snake_case_id` HIGH|MEDIUM|LOW: specific real fact.\n"
                "- cover_options: At least 1 entry as: `cover_id`: \"Player cover identity\" -- (NPC reaction note)."
            )
        if rule == 37:
            return (
                "Add at least one `actions_available` entry to the NPC identified above.\n"
                "Format: `snake_case_action_id` HIGH|MEDIUM|LOW: What the NPC does when convinced — be specific.\n"
                "The action_id MUST either match a task's `Target Outcomes` or be referenceable as `Outcome action_id`.\n"
                "Example: `leave_post` HIGH: Can be convinced to leave his post early for a smoke break"
            )
        if rule == 38:
            return (
                "Add cover story options to each NPC that has fewer than 3.\n"
                "Each entry must have: `cover_id`: \"One sentence player cover identity\" -- (NPC behavioral reaction note)\n"
                "Make the identities diverse: one plausible professional, one semi-plausible civilian, one implausible/funny.\n"
                "The NPC reaction note should describe concretely how the NPC behaves differently for that cover."
            )
        if rule == 39:
            return (
                "Ensure at least ONE outcome flows cross-role: Role A learns it from an NPC, Role B needs it.\n"
                "Pattern 1 — Direct prerequisite: add 'Outcome `outcome_id`' to one of Role B's task prerequisites.\n"
                "Pattern 2 — Via info_share: add an info_share task for Role A that has the NPC task as prerequisite,\n"
                "  then add 'Outcome `outcome_id`' as a prerequisite on Role B's dependent task.\n"
                "Use an existing NPC outcome ID — do NOT invent new ones that don't exist in NPC definitions."
            )
        return ""

    def _build_fix_prompt(self, scenario_content: str, issue: ValidationIssue) -> str:
        """Build prompt for fixing a specific issue"""

        # Format issue details
        details_str = "\n".join([f"  - {d}" for d in issue.details]) if issue.details else "  (No specific details)"

        # Rules that benefit from the NPC reference block
        npc_rules = {36, 37, 38, 39}
        # Rules that get targeted fix instructions
        guided_rules = {16, 17, 28} | npc_rules

        npc_reference_section = ""
        if issue.rule_number in npc_rules:
            npc_reference_section = f"\n{self._NPC_REFERENCE_BLOCK}\n"

        extra_instructions = ""
        if issue.rule_number in guided_rules:
            fix_guide = self._get_fix_instructions(issue)
            if fix_guide:
                label = "NPC-SPECIFIC FIX GUIDANCE" if issue.rule_number in npc_rules else "FIX GUIDANCE"
                extra_instructions = f"\n{label}:\n{fix_guide}\n"

        prompt = f"""You are a scenario file editor. Your job is to make MINIMAL, SURGICAL edits to fix specific validation issues.
{npc_reference_section}
VALIDATION ISSUE TO FIX:
Rule #{issue.rule_number}: {issue.title}
Level: {issue.level}

Details:
{details_str}

Fix Suggestion: {issue.fix_suggestion or 'Use your judgment'}
{extra_instructions}
CURRENT SCENARIO FILE:
---
{scenario_content}
---

INSTRUCTIONS:
1. Read and understand the validation issue
2. Make ONLY the changes necessary to fix this specific issue
3. Preserve ALL other content exactly as-is
4. Follow these ID reference rules:
   - Tasks MUST use location IDs in backticks: *Location:* `bank_lobby`
   - Tasks MUST use NPC IDs in backticks: *NPC:* `lobby_guard_brenda`
   - Prerequisites MUST use IDs: Task `MM1`, Item `keycard`, Outcome `guard_info`
5. Maintain the exact markdown format and structure
6. Do NOT add commentary or explanations
7. Return ONLY the complete fixed scenario file

OUTPUT:
Return the ENTIRE fixed scenario file with your changes applied."""

        return prompt


def main():
    """Test the editor agent"""
    import argparse
    from validate_scenario import ScenarioValidator
    
    parser = argparse.ArgumentParser(description="Edit scenario files using LLM")
    parser.add_argument("scenario_file", type=str, help="Path to scenario file")
    parser.add_argument("--max-issues", type=int, default=5, help="Max issues to fix")
    
    args = parser.parse_args()
    
    scenario_file = Path(args.scenario_file)
    
    if not scenario_file.exists():
        print(f"Error: File not found: {scenario_file}")
        return 1
    
    # Validate to get issues
    print(f"Validating {scenario_file.name}...")
    validator = ScenarioValidator(scenario_file)
    report = validator.validate_all()
    
    if report.passed:
        print("✅ No issues to fix!")
        return 0
    
    # Get critical issues
    critical_issues = [i for i in report.issues if i.level == ValidationLevel.CRITICAL]
    
    if not critical_issues:
        print("No critical issues found")
        return 0
    
    print(f"\nFound {len(critical_issues)} critical issues")
    print(f"Attempting to fix top {args.max_issues}...\n")
    
    # Create editor and fix
    editor = ScenarioEditorAgent()
    results = editor.fix_issues(scenario_file, critical_issues, max_issues=args.max_issues)
    
    # Report results
    print("\n" + "="*80)
    print("EDIT RESULTS")
    print("="*80)
    
    success_count = sum(1 for r in results if r.success)
    print(f"\nFixed: {success_count}/{len(results)} issues")
    
    for result in results:
        status = "✓" if result.success else "✗"
        print(f"{status} {result.issue_fixed}")
        if result.error:
            print(f"  Error: {result.error}")
    
    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
