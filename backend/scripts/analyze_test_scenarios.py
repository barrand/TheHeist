#!/usr/bin/env python3
"""Analyze and report on test scenarios"""

import re
from pathlib import Path
from validate_scenario import ScenarioValidator

def extract_scenario_info(filepath):
    """Extract key info from scenario file"""
    content = filepath.read_text()
    
    # Extract metadata from header
    scenario_id = re.search(r'\*\*ID\*\*: `([^`]+)`', content)
    scenario_name = re.search(r'\*\*Scenario\*\*: (.+)', content)
    roles = re.search(r'\*\*Selected Roles\*\*: (.+)', content)
    player_count = re.search(r'\*\*Player Count\*\*: (\d+)', content)
    objective = re.search(r'## Objective\n\n(.+?)(?=\n\n)', content, re.DOTALL)
    
    return {
        'scenario_id': scenario_id.group(1) if scenario_id else 'Unknown',
        'scenario_name': scenario_name.group(1) if scenario_name else 'Unknown',
        'roles': roles.group(1) if roles else 'Unknown',
        'player_count': int(player_count.group(1)) if player_count else 0,
        'objective': objective.group(1).strip() if objective else 'Unknown'
    }

def main():
    test_dir = Path(__file__).parent / "output" / "test_scenarios"
    scenario_files = sorted(test_dir.glob("[0-9]*.md"))
    
    print("\n" + "="*100)
    print("TEST SCENARIO GENERATION & VALIDATION REPORT")
    print("="*100)
    print(f"\nAnalyzing {len(scenario_files)} scenarios...\n")
    
    results = []
    
    for i, filepath in enumerate(scenario_files, 1):
        print(f"\n{'='*100}")
        print(f"SCENARIO {i}/10: {filepath.name}")
        print("="*100)
        
        # Extract info
        info = extract_scenario_info(filepath)
        
        print(f"\n📋 DETAILS:")
        print(f"  Scenario: {info['scenario_name']}")
        print(f"  ID: {info['scenario_id']}")
        print(f"  Players: {info['player_count']}")
        print(f"  Roles: {info['roles']}")
        print(f"\n🎯 OBJECTIVE:")
        print(f"  {info['objective']}")
        
        # Validate
        print(f"\n🔍 VALIDATION:")
        validator = ScenarioValidator(filepath)
        report = validator.validate_all()
        
        critical = sum(1 for issue in report.issues if issue.level.value == "CRITICAL")
        important = sum(1 for issue in report.issues if issue.level.value == "IMPORTANT")
        advisory = sum(1 for issue in report.issues if issue.level.value == "ADVISORY")
        
        status = "✅ PASSED" if report.passed else "❌ FAILED"
        print(f"  Status: {status}")
        print(f"  Critical Issues: {critical}")
        print(f"  Important Issues: {important}")
        print(f"  Advisory Issues: {advisory}")
        
        if report.issues:
            print(f"\n  Issues Found:")
            for issue in report.issues:
                if issue.level.value == "CRITICAL":
                    print(f"    🚨 [{issue.rule_number}] {issue.title}")
                elif issue.level.value == "IMPORTANT":
                    print(f"    ⚠️  [{issue.rule_number}] {issue.title}")
                else:
                    print(f"    💭 [{issue.rule_number}] {issue.title}")
        
        results.append({
            'name': filepath.name,
            'info': info,
            'passed': report.passed,
            'critical': critical,
            'important': important,
            'advisory': advisory,
            'issues': report.issues
        })
    
    # Summary
    print(f"\n\n{'='*100}")
    print("SUMMARY")
    print("="*100)
    
    passed_count = sum(1 for r in results if r['passed'])
    failed_count = len(results) - passed_count
    
    print(f"\nTotal Scenarios: {len(results)}")
    print(f"✅ Passed: {passed_count} ({passed_count/len(results)*100:.0f}%)")
    print(f"❌ Failed: {failed_count} ({failed_count/len(results)*100:.0f}%)")
    
    # Issue statistics
    total_critical = sum(r['critical'] for r in results)
    total_important = sum(r['important'] for r in results)
    total_advisory = sum(r['advisory'] for r in results)
    
    print(f"\nTotal Issues:")
    print(f"  🚨 Critical: {total_critical}")
    print(f"  ⚠️  Important: {total_important}")
    print(f"  💭 Advisory: {total_advisory}")
    
    # Most common issues
    from collections import Counter
    all_issues = []
    for r in results:
        for issue in r['issues']:
            all_issues.append(f"[{issue.rule_number}] {issue.title}")
    
    if all_issues:
        issue_counts = Counter(all_issues)
        print(f"\n📊 Most Common Issues:")
        for issue, count in issue_counts.most_common(10):
            print(f"  {count}x: {issue}")
    
    # Player count distribution
    player_counts = Counter(r['info']['player_count'] for r in results)
    print(f"\n👥 Player Count Distribution:")
    for count in sorted(player_counts.keys()):
        print(f"  {count} players: {player_counts[count]} scenarios")
    
    print(f"\n{'='*100}\n")

if __name__ == '__main__':
    main()
