#!/usr/bin/env python3
"""
Auto-Fix Scenarios

Automatically applies fixes to scenario files and re-validates.
Creates a fix-validate-retry loop until scenarios pass or max attempts reached.

Usage:
    python auto_fix_scenarios.py <scenario_file.md>
    python auto_fix_scenarios.py output/test_scenarios/*.md --max-attempts 3
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Dict, Set
from validate_scenario import ScenarioValidator, ValidationLevel


class ScenarioAutoFixer:
    """Automatically fixes common scenario validation issues"""
    
    def __init__(self, filepath: Path, max_attempts: int = 3):
        self.filepath = filepath
        self.max_attempts = max_attempts
        self.content = filepath.read_text()
        self.original_content = self.content
        self.attempt = 0
        self.fixes_applied = []
    
    def run_fix_loop(self) -> bool:
        """Run fix-validate loop until passing or max attempts"""
        print(f"\n{'='*80}")
        print(f"AUTO-FIXING: {self.filepath.name}")
        print(f"{'='*80}\n")
        
        while self.attempt < self.max_attempts:
            self.attempt += 1
            print(f"\n--- Attempt {self.attempt}/{self.max_attempts} ---\n")
            
            # Validate
            validator = ScenarioValidator(self.filepath)
            report = validator.validate_all()
            
            critical_issues = [i for i in report.issues if i.level == ValidationLevel.CRITICAL]
            
            if not critical_issues:
                print(f"✅ SUCCESS! Scenario passes validation after {self.attempt} attempt(s)")
                if self.fixes_applied:
                    print(f"\nFixes applied:")
                    for fix in self.fixes_applied:
                        print(f"  • {fix}")
                return True
            
            print(f"Found {len(critical_issues)} critical issues:")
            for issue in critical_issues[:5]:  # Show first 5
                print(f"  🚨 [{issue.rule_number}] {issue.title}")
            
            # Try to fix issues
            fixed_any = False
            
            for issue in critical_issues:
                if issue.rule_number == 5:  # Location count
                    if self._fix_location_count(issue):
                        fixed_any = True
                elif issue.rule_number == 4:  # Task count
                    if self._fix_task_count(issue):
                        fixed_any = True
                elif issue.rule_number == 12:  # Inconsistent location names
                    if self._fix_location_names(issue):
                        fixed_any = True
                elif issue.rule_number == 11:  # Invalid item references
                    if self._fix_item_references(issue):
                        fixed_any = True
                elif issue.rule_number == 17:  # Insufficient interaction
                    if self._fix_insufficient_interaction(issue):
                        fixed_any = True
            
            if not fixed_any:
                print(f"\n❌ Unable to auto-fix remaining issues. Manual intervention required.")
                return False
            
            # Save changes
            self.filepath.write_text(self.content)
            print(f"\n💾 Saved changes to {self.filepath.name}")
        
        print(f"\n❌ Max attempts ({self.max_attempts}) reached. Scenario still has critical issues.")
        return False
    
    def _fix_location_count(self, issue) -> bool:
        """Add placeholder locations if count is too low"""
        # Extract expected range from message
        match = re.search(r'expected (\d+)-(\d+) locations, found (\d+)', issue.message)
        if not match:
            return False
        
        min_locs, max_locs, current = int(match.group(1)), int(match.group(2)), int(match.group(3))
        
        if current >= min_locs:
            return False  # Already in range
        
        needed = min_locs - current
        print(f"  🔧 Adding {needed} placeholder location(s)...")
        
        # Find the Locations section
        locations_match = re.search(r'(## Locations\n.*?)(?=\n## |\Z)', self.content, re.DOTALL)
        if not locations_match:
            return False
        
        # Add locations at the end of the section
        location_templates = [
            ("Surveillance Point", "surveillance_point", "Remote observation post", "High vantage point"),
            ("Side Alley", "side_alley", "Narrow alley for discreet entry", "Dark narrow passage"),
            ("Back Entrance", "back_entrance", "Alternative entry point", "Unmarked service door"),
            ("Parking Lot", "parking_lot", "Vehicle staging area", "Dimly lit parking area"),
            ("Rooftop", "rooftop", "Elevated access point", "Flat rooftop with ventilation"),
        ]
        
        new_locations = []
        for i in range(needed):
            if i < len(location_templates):
                name, loc_id, desc, visual = location_templates[i]
                new_locations.append(f"\n### {name}\n- **ID**: `{loc_id}`\n- **Name**: {name}\n- **Description**: {desc}\n- **Visual**: {visual}\n")
        
        # Insert before next section
        insert_pos = locations_match.end()
        self.content = self.content[:insert_pos] + ''.join(new_locations) + self.content[insert_pos:]
        
        self.fixes_applied.append(f"Added {needed} location(s)")
        return True
    
    def _fix_task_count(self, issue) -> bool:
        """Add placeholder tasks if count is too low"""
        match = re.search(r'expected (\d+)-(\d+) tasks, found (\d+)', issue.message)
        if not match:
            return False
        
        min_tasks, max_tasks, current = int(match.group(1)), int(match.group(2)), int(match.group(3))
        
        if current >= min_tasks:
            return False
        
        needed = min_tasks - current
        print(f"  🔧 Adding {needed} placeholder task(s)...")
        
        # Find a role section to add tasks to
        role_sections = re.finditer(r'### (\w+)\n\n\*\*Tasks:\*\*', self.content)
        first_role = None
        for match in role_sections:
            first_role = match.group(1)
            break
        
        if not first_role:
            return False
        
        # Map role names to proper codes
        role_codes = {
            'mastermind': 'MM', 'hacker': 'H', 'safe_cracker': 'SC', 'driver': 'D',
            'insider': 'I', 'grifter': 'G', 'muscle': 'M', 'lookout': 'L',
            'fence': 'F', 'cat_burglar': 'CB', 'cleaner': 'CL', 'pickpocket': 'PP'
        }
        role_code = role_codes.get(first_role.lower().replace(' ', '_'), first_role[:2].upper())
        
        # Find existing task numbers for this role
        existing_tasks = re.findall(rf'\*\*{role_code}(\d+)\.\s+', self.content)
        next_num = max([int(n) for n in existing_tasks], default=0) + 1
        
        # Find where to insert (after the role's Tasks: line)
        role_section = re.search(rf'### {first_role}\n\n\*\*Tasks:\*\*\n(.*?)(?=\n### |\Z)', self.content, re.DOTALL)
        if not role_section:
            return False
        
        new_tasks = []
        for i in range(min(needed, 5)):  # Add up to 5 tasks
            task_num = next_num + i
            new_tasks.append(f"\n{len(existing_tasks) + i + 1}. **{role_code}{task_num}. 🔍 SEARCH** - Search for Additional Intel\n   - *Description:* Search the area for useful information or items.\n   - *Location:* Any\n   - *Prerequisites:* None\n")
        
        insert_pos = role_section.end()
        self.content = self.content[:insert_pos] + ''.join(new_tasks) + self.content[insert_pos:]
        
        self.fixes_applied.append(f"Added {len(new_tasks)} placeholder task(s) to {first_role}")
        return True
    
    def _fix_location_names(self, issue) -> bool:
        """Fix inconsistent location names by standardizing them"""
        if not issue.details:
            return False
        
        print(f"  🔧 Fixing {len(issue.details)} inconsistent location name(s)...")
        
        # Extract all defined location names
        location_names = set()
        for match in re.finditer(r'- \*\*Name\*\*: (.+)', self.content):
            location_names.add(match.group(1).strip())
        
        # Try to fix each inconsistent reference
        fixed_count = 0
        for detail in issue.details:
            # Extract task ID and wrong location
            match = re.search(r'(\w+): unknown location \'([^\']+)\'', detail)
            if not match:
                continue
            
            task_id, wrong_loc = match.group(1), match.group(2)
            
            # Find closest matching location name (simple string matching)
            best_match = None
            best_score = 0
            for loc_name in location_names:
                # Simple similarity: count common words
                wrong_words = set(wrong_loc.lower().split())
                loc_words = set(loc_name.lower().split())
                common = len(wrong_words & loc_words)
                if common > best_score:
                    best_score = common
                    best_match = loc_name
            
            if best_match and best_score > 0:
                # Replace in task definition
                pattern = rf'(\*\*{task_id}\..*?- \*Location:\*\s+){re.escape(wrong_loc)}'
                self.content = re.sub(pattern, rf'\1{best_match}', self.content)
                fixed_count += 1
        
        if fixed_count > 0:
            self.fixes_applied.append(f"Fixed {fixed_count} location name(s)")
            return True
        
        return False
    
    def _fix_item_references(self, issue) -> bool:
        """Remove invalid item references from 'Required For' fields"""
        if not issue.details:
            return False
        
        print(f"  🔧 Fixing {len(issue.details)} invalid item reference(s)...")
        
        fixed_count = 0
        for detail in issue.details:
            # Extract item ID and invalid task reference
            match = re.search(r"Item '([^']+)': Required For references unknown task '([^']+)'", detail)
            if not match:
                continue
            
            item_id, unknown_task = match.group(1), match.group(2)
            
            # Change "Required For: TASKID" to "Required For: None"
            pattern = rf'(- \*\*ID\*\*: `{re.escape(item_id)}`.*?- \*\*Required For\*\*:)[^\n]*{re.escape(unknown_task)}[^\n]*'
            replacement = r'\1 None (optional item)'
            
            if re.search(pattern, self.content, re.DOTALL):
                self.content = re.sub(pattern, replacement, self.content, flags=re.DOTALL)
                fixed_count += 1
        
        if fixed_count > 0:
            self.fixes_applied.append(f"Fixed {fixed_count} item reference(s)")
            return True
        
        return False
    
    def _fix_insufficient_interaction(self, issue) -> bool:
        """Add handoff tasks to improve cross-role interaction"""
        if "handoff" not in issue.message.lower():
            return False
        
        print(f"  🔧 Adding handoff task(s) for cross-role interaction...")
        
        # Find first two roles in the scenario
        role_matches = list(re.finditer(r'### (\w+)\n\n\*\*Tasks:\*\*', self.content))
        if len(role_matches) < 2:
            return False
        
        role1, role2 = role_matches[0].group(1), role_matches[1].group(1)
        role1_code = role1[:2].upper()
        role2_code = role2[:2].upper()
        
        # Get next task number for role1
        existing = re.findall(rf'\*\*{role1_code}(\d+)\.\s+', self.content)
        next_num = max([int(n) for n in existing], default=0) + 1
        
        # Add a handoff task
        handoff_task = f"\n{len(existing) + 1}. **{role1_code}{next_num}. 🔍 SEARCH** - Find Equipment for {role2}\n   - *Description:* Search for equipment needed by {role2} and coordinate handoff.\n   - *Location:* Any\n   - *Prerequisites:* None\n"
        
        # Insert after role1's tasks
        insert_pos = role_matches[0].end()
        self.content = self.content[:insert_pos] + handoff_task + self.content[insert_pos:]
        
        self.fixes_applied.append("Added handoff task for cross-role interaction")
        return True
    
    def rollback(self):
        """Rollback to original content"""
        self.content = self.original_content
        self.filepath.write_text(self.content)
        print(f"🔄 Rolled back changes to {self.filepath.name}")


def main():
    parser = argparse.ArgumentParser(description="Auto-fix scenario validation issues")
    parser.add_argument("files", nargs="+", help="Scenario files to fix")
    parser.add_argument("--max-attempts", type=int, default=3, help="Max fix attempts per file")
    parser.add_argument("--rollback-on-fail", action="store_true", help="Rollback if fixing fails")
    
    args = parser.parse_args()
    
    results = []
    
    for file_pattern in args.files:
        files = list(Path().glob(file_pattern)) if '*' in file_pattern else [Path(file_pattern)]
        
        for filepath in files:
            if not filepath.exists():
                print(f"❌ File not found: {filepath}")
                continue
            
            fixer = ScenarioAutoFixer(filepath, max_attempts=args.max_attempts)
            success = fixer.run_fix_loop()
            
            if not success and args.rollback_on_fail:
                fixer.rollback()
            
            results.append((filepath.name, success))
    
    # Summary
    print(f"\n\n{'='*80}")
    print("AUTO-FIX SUMMARY")
    print(f"{'='*80}\n")
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    print(f"Total: {len(results)} scenarios")
    print(f"✅ Fixed and passing: {passed}")
    print(f"❌ Still failing: {failed}")
    
    if failed > 0:
        print(f"\nFailed scenarios:")
        for name, success in results:
            if not success:
                print(f"  • {name}")
    
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
