#!/usr/bin/env python3
"""
Batch E2E Test Runner

Runs E2E tests on multiple scenarios and reports results.
"""

import subprocess
import sys
from pathlib import Path

def run_e2e_test(scenario_file: str, difficulty: str = "easy") -> dict:
    """Run a single E2E test and return result"""
    
    scenario_name = Path(scenario_file).stem
    print(f"\n{'='*80}")
    print(f"🎮 Testing: {scenario_name}")
    print(f"{'='*80}")
    
    cmd = [
        "python3",
        "scripts/test_gameplay_e2e.py",
        "--scenario", scenario_file,
        "--difficulty", difficulty,
        "--skip-npc"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            cwd="/Users/bbarrand/Documents/Projects/TheHeist/backend",
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Extract result from output
        lines = result.stdout.split('\n')
        status = "UNKNOWN"
        turns = 0
        tasks = {}
        
        for line in lines:
            if "Status:" in line and "(" in line:
                # Parse: "Status: WIN (18 turns)"
                parts = line.split("Status:")[1].strip().split("(")
                status = parts[0].strip()
                if len(parts) > 1:
                    turns_str = parts[1].split()[0]
                    turns = int(turns_str)
            
            # Parse per-role tasks: "  hacker: 5 tasks, 0 NPC conversations, 8 idle turns"
            if ":" in line and "tasks," in line:
                role = line.split(":")[0].strip()
                task_count = int(line.split(":")[1].split("tasks")[0].strip())
                tasks[role] = task_count
        
        return {
            "scenario": scenario_name,
            "status": status,
            "turns": turns,
            "tasks": tasks,
            "exit_code": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        print(f"⏱️  TIMEOUT after 120s")
        return {
            "scenario": scenario_name,
            "status": "TIMEOUT",
            "turns": 0,
            "tasks": {},
            "exit_code": 1
        }
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {
            "scenario": scenario_name,
            "status": "ERROR",
            "turns": 0,
            "tasks": {},
            "exit_code": 2
        }


def main():
    scenarios = [
        "experiences/generated_museum_heist_3players.md",
        "experiences/generated_bank_vault_3players.md",
        "experiences/generated_office_infiltration_2players.md",
    ]
    
    print("\n" + "="*80)
    print("🎲 BATCH E2E TEST RUNNER")
    print(f"Testing {len(scenarios)} scenarios")
    print("="*80)
    
    results = []
    for scenario in scenarios:
        result = run_e2e_test(scenario)
        results.append(result)
    
    # Summary report
    print("\n" + "="*80)
    print("📊 BATCH E2E TEST RESULTS")
    print("="*80)
    
    passed = 0
    for result in results:
        status_emoji = "✅" if result["status"] == "WIN" else "❌"
        total_tasks = sum(result["tasks"].values())
        
        print(f"{status_emoji} {result['scenario']:40s} {result['status']:10s} ({result['turns']:3d} turns, {total_tasks:2d} tasks)")
        
        if result["status"] == "WIN":
            passed += 1
    
    print(f"\n{'='*80}")
    print(f"🎉 RESULTS: {passed}/{len(results)} scenarios PASSED")
    print(f"{'='*80}\n")
    
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
