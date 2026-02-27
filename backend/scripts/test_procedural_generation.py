#!/usr/bin/env python3
"""
Test Procedural Scenario Generation

Generates scenarios using the procedural graph generator,
validates them, and exports to JSON + markdown.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from generators.procedural_generator import (
    generate_scenario_graph,
    GeneratorConfig
)
from generators.graph_validator import validate_graph
from generators.json_exporter import export_to_json
from generators.markdown_renderer import export_to_markdown


def test_generation(scenario_id: str, roles: list, seed: int = None):
    """Generate and validate a single scenario"""
    
    print(f"\n{'='*80}")
    print(f"🎲 Generating scenario: {scenario_id}")
    print(f"   Roles: {', '.join(roles)}")
    print(f"   Seed: {seed if seed else 'random'}")
    print(f"{'='*80}\n")
    
    # Configure generator
    config = GeneratorConfig(seed=seed)
    
    # Generate graph
    print("1️⃣  Generating procedural graph...")
    graph = generate_scenario_graph(scenario_id, roles, config)
    
    print(f"   ✅ Generated:")
    print(f"      - {len(graph.locations)} locations")
    print(f"      - {len(graph.items)} items")
    print(f"      - {len(graph.npcs)} NPCs")
    print(f"      - {len(graph.tasks)} tasks")
    print()
    
    # Validate graph
    print("2️⃣  Validating graph structure...")
    result = validate_graph(graph)
    
    if result.valid:
        print("   ✅ Graph is valid!\n")
    else:
        print("   ❌ Validation failed:\n")
        for error in result.errors:
            print(f"      [{error.severity.upper()}] {error.rule}")
            print(f"      {error.message}")
            for detail in error.details[:3]:  # Show first 3 details
                print(f"        - {detail}")
            if len(error.details) > 3:
                print(f"        ... and {len(error.details) - 3} more")
            print()
        
        if any(e.severity == "critical" for e in result.errors):
            print("   🛑 Critical errors found. Aborting export.\n")
            return False
    
    # Export to JSON
    print("3️⃣  Exporting to JSON...")
    json_path = export_to_json(graph)
    print(f"   ✅ Saved: {json_path}\n")
    
    # Export to markdown (for humans)
    print("4️⃣  Rendering markdown (optional, for humans)...")
    md_path = export_to_markdown(graph)
    print(f"   ✅ Saved: {md_path}\n")
    
    print("=" * 80)
    print(f"✅ SUCCESS: {scenario_id} generated and validated")
    print("=" * 80)
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Test procedural scenario generation"
    )
    parser.add_argument(
        "--scenario",
        default="museum_heist",
        help="Scenario ID"
    )
    parser.add_argument(
        "--roles",
        nargs="+",
        default=["mastermind", "hacker", "safe_cracker", "insider"],
        help="Player roles"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=3,
        help="Number of scenarios to generate"
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("🎲 PROCEDURAL SCENARIO GENERATION TEST")
    print("="*80)
    
    scenarios = [
        ("museum_heist", ["mastermind", "hacker", "safe_cracker"]),
        ("bank_vault", ["hacker", "safe_cracker", "driver"]),
        ("office_infiltration", ["insider", "hacker"]),
    ]
    
    # Generate multiple scenarios
    success_count = 0
    for i in range(args.count):
        scenario_id, roles = scenarios[i % len(scenarios)]
        seed = args.seed + i if args.seed else None
        
        if test_generation(scenario_id, roles, seed):
            success_count += 1
    
    print(f"\n{'='*80}")
    print(f"🎉 RESULTS: {success_count}/{args.count} scenarios generated successfully")
    print(f"{'='*80}\n")
    
    return 0 if success_count == args.count else 1


if __name__ == "__main__":
    sys.exit(main())
