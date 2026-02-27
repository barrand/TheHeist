#!/usr/bin/env python3
"""Quick validation of search tasks in generated scenarios"""

import json
import sys
from pathlib import Path

def validate_search_tasks(json_file: str) -> bool:
    """Check that all search tasks have items assigned"""
    
    data = json.load(open(json_file))
    scenario_id = data.get('scenario_id', 'unknown')
    
    print(f"\n{'='*60}")
    print(f"Validating: {scenario_id}")
    print(f"{'='*60}")
    
    issues = []
    
    for task in data.get('tasks', []):
        if task.get('type') == 'search':
            items = task.get('search_items', [])
            if not items:
                issues.append(f"  ❌ Task {task['id']} @ {task['location']}: NO ITEMS")
            else:
                print(f"  ✅ Task {task['id']} @ {task['location']}: {len(items)} items {items}")
    
    if issues:
        print("\n🚨 ISSUES FOUND:")
        for issue in issues:
            print(issue)
        return False
    else:
        print(f"  ✅ All search tasks have items")
        return True


if __name__ == "__main__":
    scenarios = [
        "experiences/museum_heist.json",
        "experiences/bank_vault.json",
        "experiences/office_infiltration.json",
    ]
    
    all_valid = True
    for scenario in scenarios:
        if not validate_search_tasks(scenario):
            all_valid = False
    
    print(f"\n{'='*60}")
    if all_valid:
        print("✅ ALL SCENARIOS VALID")
    else:
        print("❌ SOME SCENARIOS HAVE ISSUES")
    print(f"{'='*60}\n")
    
    sys.exit(0 if all_valid else 1)
