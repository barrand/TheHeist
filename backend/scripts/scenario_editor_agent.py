"""
Scenario Editor Agent

LLM-powered agent that makes surgical edits to scenario files based on validation issues.
Uses Gemini to understand context and make intelligent, minimal fixes.
"""

import json
import logging
import sys
from pathlib import Path
from typing import List, Optional
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

    def _get_npc_fix_instructions(self, issue: ValidationIssue) -> str:
        """Return targeted fix instructions for NPC quality rules (36-39)."""
        rule = issue.rule_number
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

        # Include NPC reference block and targeted instructions for quality rules
        npc_rules = {36, 37, 38, 39}
        npc_reference_section = ""
        extra_instructions = ""
        if issue.rule_number in npc_rules:
            npc_reference_section = f"\n{self._NPC_REFERENCE_BLOCK}\n"
            extra_instructions = f"\nNPC-SPECIFIC FIX GUIDANCE:\n{self._get_npc_fix_instructions(issue)}\n"
        
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
