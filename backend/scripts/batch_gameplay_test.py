#!/usr/bin/env python3
"""
Batch E2E Gameplay Test Script

Tests multiple scenarios across all difficulty levels.

Usage:
    # Test all scenarios in a directory
    python3 batch_gameplay_test.py --scenarios backend/scripts/output/test_scenarios/*.md
    
    # Test all difficulty levels
    python3 batch_gameplay_test.py --scenarios scenarios/*.md --all-difficulties
    
    # Test specific difficulties
    python3 batch_gameplay_test.py --scenarios scenarios/*.md --difficulties easy medium
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from typing import List
import glob

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.scripts.e2e_testing import GameplayTestOrchestrator, GameplayTestResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)


async def test_scenario_with_difficulty(
    orchestrator: GameplayTestOrchestrator,
    scenario_file: Path,
    difficulty: str
) -> GameplayTestResult:
    """Test a single scenario at one difficulty"""
    logger.info(f"Testing {scenario_file.name} @ {difficulty}...")
    
    result = await orchestrator.test_scenario(
        scenario_file=scenario_file,
        difficulty=difficulty
    )
    
    return result


async def batch_test(
    scenario_files: List[Path],
    difficulties: List[str],
    backend_url: str,
    parallel: int = 1
) -> List[GameplayTestResult]:
    """
    Run batch tests
    
    Args:
        scenario_files: List of scenario files to test
        difficulties: List of difficulties to test
        backend_url: Backend URL
        parallel: Number of tests to run in parallel (default: 1, sequential)
    
    Returns:
        List of all test results
    """
    
    orchestrator = GameplayTestOrchestrator(
        backend_url=backend_url,
        max_turns=500
    )
    
    results = []
    
    # Generate all test combinations
    tests = []
    for scenario_file in scenario_files:
        for difficulty in difficulties:
            tests.append((scenario_file, difficulty))
    
    logger.info(f"Running {len(tests)} tests ({len(scenario_files)} scenarios × {len(difficulties)} difficulties)")
    
    if parallel == 1:
        # Sequential execution
        for i, (scenario_file, difficulty) in enumerate(tests, 1):
            logger.info(f"Test {i}/{len(tests)}: {scenario_file.name} @ {difficulty}")
            result = await test_scenario_with_difficulty(orchestrator, scenario_file, difficulty)
            results.append(result)
            
            # Brief summary
            status_emoji = "✅" if result.status == "WIN" else "❌" if result.status == "ERROR" else "⚠️ "
            logger.info(f"{status_emoji} {result.status} in {result.turns_taken} turns")
    
    else:
        # Parallel execution (batches)
        for i in range(0, len(tests), parallel):
            batch = tests[i:i + parallel]
            logger.info(f"Running batch {i//parallel + 1} ({len(batch)} tests in parallel)")
            
            tasks = [
                test_scenario_with_difficulty(orchestrator, sf, diff)
                for sf, diff in batch
            ]
            
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
    
    return results


def print_summary(results: List[GameplayTestResult]):
    """Print comprehensive summary of all tests"""
    
    print("\n" + "=" * 80)
    print("BATCH TEST RESULTS")
    print("=" * 80)
    
    # Group by difficulty
    by_difficulty = {}
    for result in results:
        if result.difficulty not in by_difficulty:
            by_difficulty[result.difficulty] = []
        by_difficulty[result.difficulty].append(result)
    
    # Summary per difficulty
    for difficulty in ["easy", "medium", "hard"]:
        if difficulty not in by_difficulty:
            continue
        
        results_for_diff = by_difficulty[difficulty]
        wins = sum(1 for r in results_for_diff if r.status == "WIN")
        total = len(results_for_diff)
        
        print(f"\n{difficulty.upper()}:")
        print(f"  {wins}/{total} scenarios passed ({wins/total*100:.1f}%)")
        
        # List failures
        failures = [r for r in results_for_diff if r.status != "WIN"]
        if failures:
            print(f"  Failed scenarios:")
            for r in failures:
                print(f"    - {r.scenario_name}: {r.status} ({r.turns_taken} turns)")
                for issue in r.issues[:3]:  # First 3 issues
                    print(f"      • {issue}")
    
    # Overall summary
    total_tests = len(results)
    total_wins = sum(1 for r in results if r.status == "WIN")
    total_deadlocks = sum(1 for r in results if r.status == "DEADLOCK")
    total_timeouts = sum(1 for r in results if r.status == "TIMEOUT")
    total_errors = sum(1 for r in results if r.status == "ERROR")
    
    print(f"\n" + "-" * 80)
    print(f"OVERALL: {total_wins}/{total_tests} tests passed ({total_wins/total_tests*100:.1f}%)")
    print(f"  Wins: {total_wins}")
    print(f"  Deadlocks: {total_deadlocks}")
    print(f"  Timeouts: {total_timeouts}")
    print(f"  Errors: {total_errors}")
    print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Batch E2E gameplay testing")
    parser.add_argument(
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
        "--backend-url",
        type=str,
        default="http://localhost:8000",
        help="Backend URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of tests to run in parallel (default: 1, sequential)"
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
    for pattern in args.scenarios:
        matches = glob.glob(pattern)
        scenario_files.extend([Path(f) for f in matches])
    
    scenario_files = list(set(scenario_files))  # Remove duplicates
    scenario_files.sort()
    
    if not scenario_files:
        logger.error("No scenario files found")
        return 1
    
    logger.info(f"Found {len(scenario_files)} scenario files")
    logger.info(f"Testing difficulties: {', '.join(difficulties)}")
    
    # Run batch test
    results = asyncio.run(batch_test(
        scenario_files=scenario_files,
        difficulties=difficulties,
        backend_url=args.backend_url,
        parallel=args.parallel
    ))
    
    # Print summary
    print_summary(results)
    
    # Return exit code
    total_wins = sum(1 for r in results if r.status == "WIN")
    if total_wins == len(results):
        return 0  # All passed
    else:
        return 1  # Some failed


if __name__ == "__main__":
    sys.exit(main())
