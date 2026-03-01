#!/usr/bin/env python3
"""
Stress Test — Generate & E2E Test Random Scenarios

Generates N random scenarios (random player counts, roles, scenario types),
runs each through the E2E gameplay test, and prints a summary of results.
Aborts early if too many consecutive failures indicate something is haywire.

Usage:
    # Backend must be running first!
    python3 backend/scripts/stress_test.py
    python3 backend/scripts/stress_test.py --count 5 --max-turns 200
    python3 backend/scripts/stress_test.py --count 20 --abort-after 3
    python3 backend/scripts/stress_test.py --min-players 2 --max-players 6
"""

import asyncio
import argparse
import json
import logging
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

# Resolve paths
_SCRIPT_DIR = Path(__file__).parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
_BACKEND_DIR = _SCRIPT_DIR.parent

sys.path.insert(0, str(_PROJECT_ROOT))
sys.path.insert(0, str(_SCRIPT_DIR))

from backend.scripts.e2e_testing import GameplayTestOrchestrator

logger = logging.getLogger(__name__)

# ─── Data ────────────────────────────────────────────────────────────────────

def _load_scenarios() -> list:
    path = _PROJECT_ROOT / "shared_data" / "scenarios.json"
    with open(path) as f:
        return json.load(f)["scenarios"]

def _load_roles() -> list:
    path = _PROJECT_ROOT / "shared_data" / "roles.json"
    with open(path) as f:
        return [r["role_id"] for r in json.load(f)["roles"]]


# ─── Random scenario config ─────────────────────────────────────────────────

def pick_random_config(
    scenarios: list,
    all_roles: list,
    min_players: int,
    max_players: int,
) -> dict:
    scenario = random.choice(scenarios)
    player_count = random.randint(min_players, max_players)
    suggested = scenario.get("roles_suggested", [])
    remaining = [r for r in all_roles if r not in suggested]
    random.shuffle(remaining)
    roles = list(suggested)
    while len(roles) < player_count and remaining:
        roles.append(remaining.pop())
    roles = roles[:player_count]
    random.shuffle(roles)
    return {
        "scenario_id": scenario["scenario_id"],
        "scenario_name": scenario["name"],
        "roles": roles,
        "player_count": len(roles),
    }


# ─── Result tracking ────────────────────────────────────────────────────────

@dataclass
class RunResult:
    index: int
    scenario_id: str
    scenario_name: str
    roles: List[str]
    player_count: int
    gen_success: bool = False
    gen_error: Optional[str] = None
    gen_duration_s: float = 0.0
    e2e_status: Optional[str] = None
    e2e_turns: int = 0
    e2e_issues: List[str] = field(default_factory=list)
    e2e_duration_s: float = 0.0
    skipped: bool = False
    skip_reason: Optional[str] = None


# ─── Main logic ──────────────────────────────────────────────────────────────

async def run_e2e_test(
    md_path: Path,
    backend_url: str,
    max_turns: int,
) -> dict:
    orchestrator = GameplayTestOrchestrator(
        backend_url=backend_url,
        max_turns=max_turns,
        skip_npc_conversations=True,
    )
    result = await orchestrator.test_scenario(
        scenario_file=md_path,
        difficulty="easy",
    )
    return {
        "status": result.status,
        "turns": result.turns_taken,
        "issues": list(result.issues),
    }


def generate_scenario(scenario_id: str, roles: list, seed: int = None):
    from scenario_pipeline import run_pipeline
    return run_pipeline(scenario_id=scenario_id, roles=roles, seed=seed)


async def run_one(
    index: int,
    config: dict,
    backend_url: str,
    max_turns: int,
) -> RunResult:
    result = RunResult(
        index=index,
        scenario_id=config["scenario_id"],
        scenario_name=config["scenario_name"],
        roles=config["roles"],
        player_count=config["player_count"],
    )

    roles_str = ", ".join(config["roles"])
    header = f"[{index}] {config['scenario_name']} ({config['player_count']}p: {roles_str})"
    logger.info("")
    logger.info("=" * 70)
    logger.info(f"  {header}")
    logger.info("=" * 70)

    # ── Generate ──
    logger.info(f"  Generating scenario...")
    t0 = time.monotonic()
    try:
        gen = await asyncio.to_thread(
            generate_scenario, config["scenario_id"], config["roles"]
        )
        result.gen_duration_s = time.monotonic() - t0
    except Exception as e:
        result.gen_duration_s = time.monotonic() - t0
        result.gen_error = str(e)
        logger.error(f"  ❌ Generation crashed: {e}")
        return result

    if not gen.success:
        result.gen_error = gen.error or "unknown"
        logger.error(f"  ❌ Generation failed: {result.gen_error}")
        return result

    result.gen_success = True
    logger.info(
        f"  ✅ Generated in {result.gen_duration_s:.1f}s — "
        f"{gen.tasks} tasks, {gen.locations} locs, {gen.items} items"
    )

    if gen.remaining_critical > 0:
        result.skipped = True
        result.skip_reason = f"{gen.remaining_critical} unresolved critical issues"
        logger.warning(f"  ⚠️ Skipping E2E — {result.skip_reason}")
        return result

    # ── E2E Test ──
    logger.info(f"  Running E2E test (max {max_turns} turns)...")
    t1 = time.monotonic()
    try:
        e2e = await run_e2e_test(gen.md_path, backend_url, max_turns)
        result.e2e_duration_s = time.monotonic() - t1
        result.e2e_status = e2e["status"]
        result.e2e_turns = e2e["turns"]
        result.e2e_issues = e2e["issues"]
    except Exception as e:
        result.e2e_duration_s = time.monotonic() - t1
        result.e2e_status = "ERROR"
        result.e2e_issues = [str(e)]
        logger.error(f"  ❌ E2E crashed: {e}")
        return result

    status_icon = {
        "WIN": "✅", "STUCK": "⚠️", "TIMEOUT": "⏰", "ERROR": "❌"
    }.get(result.e2e_status, "❓")

    logger.info(
        f"  {status_icon} E2E: {result.e2e_status} in {result.e2e_turns} turns "
        f"({result.e2e_duration_s:.1f}s)"
    )
    if result.e2e_issues:
        for issue in result.e2e_issues[:3]:
            logger.info(f"    - {issue}")
        if len(result.e2e_issues) > 3:
            logger.info(f"    ... and {len(result.e2e_issues) - 3} more")

    return result


def print_summary(results: List[RunResult], aborted: bool):
    wins = [r for r in results if r.e2e_status == "WIN"]
    stucks = [r for r in results if r.e2e_status == "STUCK"]
    timeouts = [r for r in results if r.e2e_status == "TIMEOUT"]
    errors = [r for r in results if r.e2e_status == "ERROR"]
    gen_fails = [r for r in results if not r.gen_success]
    skipped = [r for r in results if r.skipped]

    print("\n")
    print("=" * 70)
    print("  STRESS TEST SUMMARY")
    print("=" * 70)
    print(f"  Total runs:         {len(results)}")
    print(f"  ✅ WIN:             {len(wins)}")
    print(f"  ⚠️  STUCK:           {len(stucks)}")
    print(f"  ⏰ TIMEOUT:         {len(timeouts)}")
    print(f"  ❌ ERROR:           {len(errors)}")
    print(f"  🚫 Gen failed:      {len(gen_fails)}")
    print(f"  ⏭️  Skipped (crit):  {len(skipped)}")
    if aborted:
        print(f"  🛑 ABORTED EARLY — too many consecutive failures")
    print()

    total_gen_time = sum(r.gen_duration_s for r in results)
    total_e2e_time = sum(r.e2e_duration_s for r in results)
    print(f"  Total gen time:  {total_gen_time:.0f}s ({total_gen_time/60:.1f}m)")
    print(f"  Total E2E time:  {total_e2e_time:.0f}s ({total_e2e_time/60:.1f}m)")
    print(f"  Total wall time: {total_gen_time + total_e2e_time:.0f}s ({(total_gen_time + total_e2e_time)/60:.1f}m)")
    print()

    if wins:
        avg_turns = sum(r.e2e_turns for r in wins) / len(wins)
        print(f"  Win stats: avg {avg_turns:.0f} turns, "
              f"range {min(r.e2e_turns for r in wins)}-{max(r.e2e_turns for r in wins)}")

    # Detailed table
    print()
    print(f"  {'#':>3}  {'Status':>8}  {'Turns':>5}  {'Players':>7}  Scenario")
    print(f"  {'─'*3}  {'─'*8}  {'─'*5}  {'─'*7}  {'─'*35}")
    for r in results:
        status = r.e2e_status or ("GEN_FAIL" if not r.gen_success else "SKIP")
        roles = ", ".join(r.roles)
        turns_str = str(r.e2e_turns) if r.e2e_turns else "-"
        print(f"  {r.index:>3}  {status:>8}  {turns_str:>5}  {r.player_count:>7}  {r.scenario_name} ({roles})")

    # Issue summary
    all_issues = []
    for r in results:
        for issue in r.e2e_issues:
            all_issues.append(f"[{r.index}] {issue}")

    if all_issues:
        print()
        print(f"  Issues ({len(all_issues)} total):")
        for issue in all_issues[:20]:
            print(f"    - {issue}")
        if len(all_issues) > 20:
            print(f"    ... and {len(all_issues) - 20} more")

    print()
    print("=" * 70)

    success_rate = len(wins) / len(results) * 100 if results else 0
    print(f"  Success rate: {success_rate:.0f}% ({len(wins)}/{len(results)})")
    print("=" * 70)
    print()


# ─── CLI ─────────────────────────────────────────────────────────────────────

def parse_include_config(spec: str, scenarios: list) -> dict:
    """Parse 'scenario_id:role1,role2,...' into a config dict."""
    parts = spec.split(":", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid --include format: {spec!r} (expected 'scenario_id:role1,role2,...')")
    scenario_id, roles_str = parts
    roles = [r.strip() for r in roles_str.split(",")]
    scenario_name = scenario_id
    for s in scenarios:
        if s["scenario_id"] == scenario_id:
            scenario_name = s["name"]
            break
    return {
        "scenario_id": scenario_id,
        "scenario_name": scenario_name,
        "roles": roles,
        "player_count": len(roles),
    }


async def main_async(args):
    scenarios = _load_scenarios()
    all_roles = _load_roles()

    included = [parse_include_config(spec, scenarios) for spec in args.include]
    random_configs = [
        pick_random_config(scenarios, all_roles, args.min_players, args.max_players)
        for _ in range(args.count)
    ]
    configs = included + random_configs

    total = len(configs)
    logger.info(f"Stress test: {len(included)} targeted + {args.count} random = {total} scenarios, "
                f"{args.min_players}-{args.max_players} players, "
                f"abort after {args.abort_after} consecutive failures")
    logger.info(f"Backend: {args.backend_url}")
    logger.info("")

    results: List[RunResult] = []
    consecutive_failures = 0
    aborted = False

    for i, config in enumerate(configs, 1):
        result = await run_one(i, config, args.backend_url, args.max_turns)
        results.append(result)

        is_success = result.e2e_status == "WIN"
        if is_success:
            consecutive_failures = 0
        else:
            consecutive_failures += 1

        if consecutive_failures >= args.abort_after:
            logger.error("")
            logger.error(f"🛑 ABORTING — {consecutive_failures} consecutive failures")
            logger.error(f"   Something is likely haywire. Fix issues before continuing.")
            aborted = True
            break

    print_summary(results, aborted)
    return 0 if not aborted and all(r.e2e_status == "WIN" for r in results if r.gen_success and not r.skipped) else 1


def main():
    parser = argparse.ArgumentParser(
        description="Stress test: generate random scenarios and run E2E tests"
    )
    parser.add_argument("--count", type=int, default=20,
                        help="Number of scenarios to generate and test (default: 20)")
    parser.add_argument("--min-players", type=int, default=2,
                        help="Minimum player count (default: 2)")
    parser.add_argument("--max-players", type=int, default=6,
                        help="Maximum player count (default: 6)")
    parser.add_argument("--max-turns", type=int, default=200,
                        help="Max turns per E2E test before timeout (default: 200)")
    parser.add_argument("--abort-after", type=int, default=3,
                        help="Abort after N consecutive failures (default: 3)")
    parser.add_argument("--backend-url", type=str, default="http://localhost:8000",
                        help="Backend URL (default: http://localhost:8000)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducibility")
    parser.add_argument("--include", type=str, action="append", default=[],
                        help="Specific configs to prepend: 'scenario_id:role1,role2,...' "
                             "(e.g. 'train_robbery_car:fence,cat_burglar,mastermind,muscle'). "
                             "Repeat --include for multiple configs.")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose (DEBUG) logging")

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)8s] %(message)s',
        datefmt='%H:%M:%S',
    )
    logging.getLogger('websockets').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())
