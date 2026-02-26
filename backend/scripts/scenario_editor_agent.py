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
    
    def _build_fix_prompt(self, scenario_content: str, issue: ValidationIssue) -> str:
        """Build prompt for fixing a specific issue"""
        
        # Format issue details
        details_str = "\n".join([f"  - {d}" for d in issue.details]) if issue.details else "  (No specific details)"
        
        prompt = f"""You are a scenario file editor. Your job is to make MINIMAL, SURGICAL edits to fix specific validation issues.

VALIDATION ISSUE TO FIX:
Rule #{issue.rule_number}: {issue.title}
Level: {issue.level}

Details:
{details_str}

Fix Suggestion: {issue.fix_suggestion or 'Use your judgment'}

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
