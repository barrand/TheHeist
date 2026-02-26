#!/usr/bin/env python3
"""
E2E Gameplay Test Script

Tests a scenario by spawning bot players and running a full playthrough.

Usage:
    python3 test_gameplay_e2e.py --scenario backend/experiences/generated_museum_2players.md
    python3 test_gameplay_e2e.py --scenario backend/experiences/generated_museum_2players.md --difficulty hard
    python3 test_gameplay_e2e.py --scenario backend/scripts/output/test_scenarios/06_bank_3players.md
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.scripts.e2e_testing import GameplayTestOrchestrator

# Configure logging
def setup_logging(verbose: bool = False, show_progress: bool = True):
    """Setup logging with optional progress display"""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Enhanced format with colors (if terminal supports it)
    format_str = '%(asctime)s [%(levelname)8s] %(message)s'
    
    logging.basicConfig(
        level=level,
        format=format_str,
        datefmt='%H:%M:%S'
    )
    
    # Reduce noise from websockets library
    logging.getLogger('websockets').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def test_scenario(scenario_file: Path, difficulty: str, backend_url: str):
    """Run E2E test on a scenario"""
    
    logger.info("="  * 60)
    logger.info(f"Starting E2E Gameplay Test")
    logger.info(f"Scenario: {scenario_file}")
    logger.info(f"Difficulty: {difficulty}")
    logger.info(f"Backend: {backend_url}")
    logger.info("=" * 60)
    
    # Create orchestrator
    orchestrator = GameplayTestOrchestrator(
        backend_url=backend_url,
        max_turns=500
    )
    
    # Run test
    result = await orchestrator.test_scenario(
        scenario_file=scenario_file,
        difficulty=difficulty
    )
    
    # Print result
    print("\n")
    print(result.summary())
    print("\n")
    
    # Return exit code
    if result.status == "WIN":
        logger.info("✅ Test PASSED")
        return 0
    elif result.status == "ERROR":
        logger.error("❌ Test ERROR")
        return 2
    else:
        logger.warning(f"⚠️  Test {result.status}")
        return 1


def main():
    parser = argparse.ArgumentParser(description="E2E gameplay test")
    parser.add_argument(
        "--scenario",
        type=str,
        required=True,
        help="Path to scenario markdown file"
    )
    parser.add_argument(
        "--difficulty",
        type=str,
        choices=["easy", "medium", "hard"],
        default="medium",
        help="Difficulty level (default: medium)"
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
    
    setup_logging(verbose=args.verbose)
    
    scenario_file = Path(args.scenario)
    if not scenario_file.exists():
        logger.error(f"Scenario file not found: {scenario_file}")
        return 1
    
    # Run test
    exit_code = asyncio.run(test_scenario(
        scenario_file=scenario_file,
        difficulty=args.difficulty,
        backend_url=args.backend_url
    ))
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
