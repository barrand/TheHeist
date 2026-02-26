"""
Scenario Generation Test Harness

Generates multiple random scenarios and validates each one.
Tests the complete pipeline: generation → validation → analysis.

Usage:
    python test_scenario_generation.py
    python test_scenario_generation.py --count 10 --scenarios museum_gala_vault train_robbery
"""

import argparse
import json
import random
import sys
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class TestResult:
    """Result from testing one scenario generation"""
    scenario_id: str
    player_count: int
    roles: List[str]
    file_path: str
    validation_passed: bool
    issues_count: int
    warnings_count: int
    graph_issues: List[str]
    playability_issues: List[str]


class ScenarioTestHarness:
    """Test harness for scenario generation and validation"""
    
    def __init__(self, scenarios_file: str = None):
        """
        Initialize test harness
        
        Args:
            scenarios_file: Path to scenarios.json (defaults to shared_data/scenarios.json)
        """
        if scenarios_file is None:
            scenarios_file = Path(__file__).parent.parent.parent / "shared_data" / "scenarios.json"
        
        with open(scenarios_file) as f:
            data = json.load(f)
            self.scenarios = data['scenarios']
        
        # Load roles
        roles_file = Path(__file__).parent.parent.parent / "shared_data" / "roles.json"
        with open(roles_file) as f:
            data = json.load(f)
            self.all_roles = [r['role_id'] for r in data['roles']]
    
    def generate_random_scenario_config(self, scenario_id: str = None) -> Dict:
        """
        Generate a random scenario configuration
        
        Args:
            scenario_id: Specific scenario to use, or None for random
        
        Returns:
            Dict with scenario_id, player_count, and roles
        """
        if scenario_id is None:
            scenario = random.choice(self.scenarios)
            scenario_id = scenario['scenario_id']
        else:
            scenario = next((s for s in self.scenarios if s['scenario_id'] == scenario_id), None)
            if not scenario:
                raise ValueError(f"Unknown scenario: {scenario_id}")
        
        # Random player count (2-6 for testing)
        player_count = random.randint(2, 6)
        
        # Select required roles + random additional roles
        required_roles = scenario.get('required_roles', [])
        additional_count = player_count - len(required_roles)
        
        if additional_count < 0:
            # Too many required roles, just use required ones (limit player_count)
            roles = required_roles[:player_count]
        else:
            # Add random roles
            available = [r for r in self.all_roles if r not in required_roles]
            additional = random.sample(available, min(additional_count, len(available)))
            roles = required_roles + additional
        
        return {
            'scenario_id': scenario_id,
            'player_count': player_count,
            'roles': roles
        }
    
    def run_test(self, config: Dict, output_dir: Path) -> TestResult:
        """
        Generate and validate a single scenario
        
        Args:
            config: Scenario configuration from generate_random_scenario_config()
            output_dir: Directory to save generated files
        
        Returns:
            TestResult with validation findings
        """
        scenario_id = config['scenario_id']
        player_count = config['player_count']
        roles = config['roles']
        
        print(f"\n{'='*80}")
        print(f"Testing: {scenario_id} ({player_count} players)")
        print(f"Roles: {', '.join(roles)}")
        print(f"{'='*80}")
        
        # Generate scenario
        output_file = output_dir / f"test_{scenario_id}_{player_count}players.md"
        
        print("\n1. Generating scenario...")
        cmd = [
            "python3",
            str(Path(__file__).parent / "generate_experience.py"),
            "--scenario", scenario_id,
            "--roles", *roles,
            "--output", str(output_file)
        ]
        
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Generation failed: {result.stderr}")
            return TestResult(
                scenario_id=scenario_id,
                player_count=player_count,
                roles=roles,
                file_path=str(output_file),
                validation_passed=False,
                issues_count=1,
                warnings_count=0,
                graph_issues=["Generation failed"],
                playability_issues=[]
            )
        
        print(f"✅ Generated: {output_file.name}")
        
        # Validate scenario
        print("\n2. Validating scenario...")
        
        try:
            from validate_scenario import ScenarioValidator
            
            validator = ScenarioValidator(output_file)
            report = validator.validate_all()
            
            critical_count = sum(1 for i in report.issues if i.level.value == "CRITICAL")
            important_count = sum(1 for i in report.issues if i.level.value == "IMPORTANT")
            
            print(f"\nValidation: {'✅ PASSED' if report.passed else '❌ FAILED'}")
            print(f"  Critical: {critical_count}")
            print(f"  Important: {important_count}")
            print(f"  Advisory: {len(report.issues) - critical_count - important_count}")
            
            # Show critical issues
            if critical_count > 0:
                print("\n  Critical issues:")
                for issue in report.issues:
                    if issue.level.value == "CRITICAL":
                        print(f"    • [{issue.rule_number}] {issue.title}")
            
            return TestResult(
                scenario_id=scenario_id,
                player_count=player_count,
                roles=roles,
                file_path=str(output_file),
                validation_passed=report.passed,
                issues_count=critical_count,
                warnings_count=important_count,
                graph_issues=[i.title for i in report.issues if i.level.value == "CRITICAL"],
                playability_issues=[]
            )
            
        except Exception as e:
            print(f"❌ Validation error: {e}")
            import traceback
            traceback.print_exc()
            
            return TestResult(
                scenario_id=scenario_id,
                player_count=player_count,
                roles=roles,
                file_path=str(output_file),
                validation_passed=False,
                issues_count=1,
                warnings_count=0,
                graph_issues=[f"Validation error: {e}"],
                playability_issues=[]
            )
    
    def run_test_suite(self, count: int = 10, specific_scenarios: List[str] = None,
                       output_dir: str = None) -> List[TestResult]:
        """
        Run full test suite
        
        Args:
            count: Number of scenarios to generate
            specific_scenarios: Optional list of specific scenario IDs to test
            output_dir: Directory for output files (defaults to backend/scripts/output/test_scenarios/)
        
        Returns:
            List of TestResult objects
        """
        if output_dir is None:
            output_dir = Path(__file__).parent / "output" / "test_scenarios"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print("\n" + "="*80)
        print("SCENARIO GENERATION TEST SUITE")
        print("="*80)
        print(f"\nGenerating {count} test scenarios...")
        print(f"Output directory: {output_dir}")
        
        results = []
        
        for i in range(count):
            # Generate random config
            if specific_scenarios:
                scenario_id = random.choice(specific_scenarios)
            else:
                scenario_id = None
            
            config = self.generate_random_scenario_config(scenario_id)
            result = self.run_test(config, output_dir)
            results.append(result)
        
        # Print summary
        self.print_summary(results)
        
        return results
    
    def print_summary(self, results: List[TestResult]):
        """Print test suite summary"""
        print("\n" + "="*80)
        print("TEST SUITE SUMMARY")
        print("="*80)
        
        total = len(results)
        passed = sum(1 for r in results if r.validation_passed)
        failed = total - passed
        
        print(f"\nTotal scenarios tested: {total}")
        print(f"✅ Passed: {passed} ({passed/total*100:.0f}%)")
        print(f"❌ Failed: {failed} ({failed/total*100:.0f}%)")
        
        if failed > 0:
            print(f"\n❌ Failed Scenarios:")
            print("-" * 80)
            for r in results:
                if not r.validation_passed:
                    print(f"\n  {r.scenario_id} ({r.player_count} players)")
                    print(f"    Roles: {', '.join(r.roles)}")
                    print(f"    Issues: {r.issues_count}")
                    for issue in r.graph_issues[:3]:  # Show first 3
                        print(f"      • {issue}")
        
        # Most common issues
        all_issues = []
        for r in results:
            all_issues.extend(r.graph_issues)
        
        if all_issues:
            from collections import Counter
            issue_counts = Counter(all_issues)
            
            print(f"\n📊 Most Common Issues:")
            print("-" * 80)
            for issue, count in issue_counts.most_common(5):
                print(f"  {count}x: {issue}")
        
        print("\n" + "="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Test scenario generation and validation")
    parser.add_argument("--count", type=int, default=10, help="Number of scenarios to generate")
    parser.add_argument("--scenarios", nargs="+", help="Specific scenario IDs to test")
    parser.add_argument("--output", help="Output directory for test files")
    
    args = parser.parse_args()
    
    harness = ScenarioTestHarness()
    results = harness.run_test_suite(
        count=args.count,
        specific_scenarios=args.scenarios,
        output_dir=args.output
    )
    
    # Exit with error code if any tests failed
    failed_count = sum(1 for r in results if not r.validation_passed)
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == '__main__':
    main()
