#!/usr/bin/env python3
"""
Full Scenario Test Pipeline

Runs both structural validation and E2E gameplay testing.

Workflow:
1. Structural validation (fast)
2. If passed, run E2E gameplay test (slow)
3. Generate combined report

Usage:
    python3 full_scenario_test.py --scenario scenarios/museum_heist.md
    python3 full_scenario_test.py --scenario scenarios/*.md --all-difficulties
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
import glob
from typing import List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.scripts.validate_scenario import ScenarioValidator, ValidationLevel
from backend.scripts.e2e_testing import GameplayTestOrchestrator, GameplayTestResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)


async def test_scenario_full(
    scenario_file: Path,
    difficulty: str,
    backend_url: str,
    skip_structural: bool = False
) -> dict:
    """
    Run full test pipeline on a scenario
    
    Args:
        scenario_file: Path to scenario file
        difficulty: Difficulty level
        backend_url: Backend URL
        skip_structural: Skip structural validation
    
    Returns:
        Dict with results from both validation stages
    """
    
    print("\n" + "=" * 80)
    print(f"FULL SCENARIO TEST: {scenario_file.name}")
    print(f"Difficulty: {difficulty}")
    print("=" * 80)
    
    results = {
        "scenario_file": str(scenario_file),
        "difficulty": difficulty,
        "structural_validation": None,
        "gameplay_test": None,
        "overall_status": "UNKNOWN"
    }
    
    # Step 1: Structural Validation
    if not skip_structural:
        print("\n[1/2] Running Structural Validation...")
        print("-" * 80)
        
        validator = ScenarioValidator(scenario_file)
        validation_report = validator.validate_all()
        
        results["structural_validation"] = {
            "passed": validation_report.passed,
            "critical_count": validation_report.count_by_level(ValidationLevel.CRITICAL),
            "error_count": validation_report.count_by_level(ValidationLevel.ERROR),
            "warning_count": validation_report.count_by_level(ValidationLevel.WARNING)
        }
        
        if validation_report.passed:
            print("✅ Structural validation PASSED")
        else:
            print(f"❌ Structural validation FAILED")
            print(f"   Critical: {results['structural_validation']['critical_count']}")
            print(f"   Errors: {results['structural_validation']['error_count']}")
            print(f"   Warnings: {results['structural_validation']['warning_count']}")
            
            # Print first few issues
            for issue in validation_report.issues[:5]:
                print(f"   - {issue.title}")
            
            results["overall_status"] = "STRUCTURAL_VALIDATION_FAILED"
            return results
    
    # Step 2: E2E Gameplay Test
    print("\n[2/2] Running E2E Gameplay Test...")
    print("-" * 80)
    
    orchestrator = GameplayTestOrchestrator(
        backend_url=backend_url,
        max_turns=500
    )
    
    gameplay_result = await orchestrator.test_scenario(
        scenario_file=scenario_file,
        difficulty=difficulty
    )
    
    results["gameplay_test"] = {
        "status": gameplay_result.status,
        "turns_taken": gameplay_result.turns_taken,
        "player_count": gameplay_result.player_count,
        "tasks_completed": sum(gameplay_result.tasks_completed_per_role.values()),
        "issues_count": len(gameplay_result.issues)
    }
    
    # Determine overall status
    if gameplay_result.status == "WIN":
        results["overall_status"] = "PASSED"
        print("✅ Gameplay test PASSED")
    else:
        results["overall_status"] = "GAMEPLAY_TEST_FAILED"
        print(f"❌ Gameplay test FAILED: {gameplay_result.status}")
    
    # Print gameplay summary
    print(f"\n{gameplay_result.summary()}")
    
    return results


async def test_multiple_scenarios(
    scenario_files: List[Path],
    difficulties: List[str],
    backend_url: str,
    skip_structural: bool
) -> List[dict]:
    """Test multiple scenarios"""
    
    all_results = []
    
    for scenario_file in scenario_files:
        for difficulty in difficulties:
            result = await test_scenario_full(
                scenario_file=scenario_file,
                difficulty=difficulty,
                backend_url=backend_url,
                skip_structural=skip_structural
            )
            all_results.append(result)
    
    return all_results


def print_overall_summary(results: List[dict]):
    """Print summary of all tests"""
    
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for r in results if r["overall_status"] == "PASSED")
    structural_failed = sum(1 for r in results if r["overall_status"] == "STRUCTURAL_VALIDATION_FAILED")
    gameplay_failed = sum(1 for r in results if r["overall_status"] == "GAMEPLAY_TEST_FAILED")
    
    print(f"\nTotal Tests: {total}")
    print(f"  ✅ Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"  ❌ Structural Validation Failed: {structural_failed}")
    print(f"  ❌ Gameplay Test Failed: {gameplay_failed}")
    
    # List failures
    if structural_failed > 0:
        print(f"\nStructural Validation Failures:")
        for r in results:
            if r["overall_status"] == "STRUCTURAL_VALIDATION_FAILED":
                scenario_name = Path(r["scenario_file"]).stem
                sv = r["structural_validation"]
                print(f"  - {scenario_name} @ {r['difficulty']}: {sv['critical_count']} critical, {sv['error_count']} errors")
    
    if gameplay_failed > 0:
        print(f"\nGameplay Test Failures:")
        for r in results:
            if r["overall_status"] == "GAMEPLAY_TEST_FAILED":
                scenario_name = Path(r["scenario_file"]).stem
                gt = r["gameplay_test"]
                print(f"  - {scenario_name} @ {r['difficulty']}: {gt['status']} ({gt['turns_taken']} turns)")
    
    print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Full scenario test pipeline")
    parser.add_argument(
        "--scenario",
        "--scenarios",
        type=str,
        nargs="+",
        required=True,
        help="Scenario files (supports glob patterns)"
    )
    parser.add_argument(
        "--all-difficulties",
        action="store_true",
        help="Test all difficulty levels (easy, medium, hard)"
    )
    parser.add_argument(
        "--difficulties",
        type=str,
        nargs="+",
        choices=["easy", "medium", "hard"],
        help="Specific difficulties to test"
    )
    parser.add_argument(
        "--skip-structural",
        action="store_true",
        help="Skip structural validation (jump straight to gameplay test)"
    )
    parser.add_argument(
        "--backend-url",
        type=str,
        default="http://localhost:8000",
        help="Backend URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine difficulties
    if args.all_difficulties:
        difficulties = ["easy", "medium", "hard"]
    elif args.difficulties:
        difficulties = args.difficulties
    else:
        difficulties = ["medium"]
    
    # Expand glob patterns
    scenario_files = []
    for pattern in args.scenario:
        matches = glob.glob(pattern)
        scenario_files.extend([Path(f) for f in matches])
    
    scenario_files = list(set(scenario_files))
    scenario_files.sort()
    
    if not scenario_files:
        logger.error("No scenario files found")
        return 1
    
    logger.info(f"Testing {len(scenario_files)} scenarios × {len(difficulties)} difficulties = {len(scenario_files) * len(difficulties)} total tests")
    
    # Run tests
    results = asyncio.run(test_multiple_scenarios(
        scenario_files=scenario_files,
        difficulties=difficulties,
        backend_url=args.backend_url,
        skip_structural=args.skip_structural
    ))
    
    # Print summary
    if len(results) > 1:
        print_overall_summary(results)
    
    # Return exit code
    passed = sum(1 for r in results if r["overall_status"] == "PASSED")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
