#!/usr/bin/env python3
"""
Generate scene images for all 11 heist scenarios.

Uses Imagen 4.0 (premium tier) for high-quality establishing shots.
Only 11 scenarios total, generated once, so premium quality is worth it.

Usage:
    python generate_scenario_images.py              # Generate all scenarios
    python generate_scenario_images.py --scenario museum_gala_vault  # Generate specific one
    python generate_scenario_images.py --list        # List all scenarios
"""

import argparse
import sys
from pathlib import Path
from generate_scene_image import generate_scene_image


# ============================================
# SCENARIO SCENE DESIGNS
# ============================================

SCENARIO_DESIGNS = {
    "museum_gala_vault": {
        "name": "Museum Gala Vault Heist",
        "description": "Grand museum hall during elegant black-tie gala event, ornate marble columns, chandeliers, well-dressed guests mingling in formal attire, priceless art on walls, vault door glimpsed in background, dramatic purple lighting through tall windows, year 2020 contemporary setting, no text, no signage",
    },
    
    "mansion_panic_room": {
        "name": "Mansion Panic Room",
        "description": "Luxurious mansion interior at night, modern architecture, reinforced steel door visible in wall, marble floors, contemporary furniture, floor-to-ceiling windows showing dark gardens outside, purple mood lighting, year 2020 contemporary setting, no text, no signage, no labels",
    },
    
    "casino_vault_night": {
        "name": "Casino Vault Night",
        "description": "Sophisticated upscale casino interior at night, elegant gaming tables with well-dressed players, slot machines with glowing displays, plush carpeting, ornate ceiling details, vault entrance visible through doorway in background, dramatic purple and gold lighting, refined atmosphere, year 2020 contemporary setting, no text, no signage",
    },
    
    "train_robbery_car": {
        "name": "Armored Train Robbery",
        "description": "Interior of modern armored train car in motion, reinforced walls, locked cargo container, dim lighting, motion blur through windows showing landscape passing by, security equipment visible, purple emergency lighting, year 2020 contemporary setting",
    },
    
    "secure_lab_prototype": {
        "name": "Secure Lab Prototype",
        "description": "Spacious high-tech research laboratory, large open floor plan, clean room with protective suits hanging on wall, advanced scientific equipment on workbenches, prototype device under glass display case in center, computer terminals with glowing screens, tall ceilings, purple accent lighting from equipment, year 2020 contemporary setting, no text, no signage",
    },
    
    "office_bug_plant": {
        "name": "Secure Office Bug Plant",
        "description": "Executive corporate office, modern desk with computer monitors, large windows overlooking city skyline at night, filing cabinets, contemporary office furniture, purple city lights visible through windows, year 2020 contemporary setting, no text, no signage",
    },
    
    "art_gallery_swap": {
        "name": "Gallery Art Swap",
        "description": "Modern art gallery interior, white walls with spotlit paintings, minimalist design, famous artwork prominently displayed, polished concrete floors, purple accent lighting from track lights, year 2020 contemporary setting",
    },
    
    "bank_safe_deposit": {
        "name": "Bank Safe Deposit Box",
        "description": "Bank vault corridor with rows of safe deposit boxes on walls, steel vault door, numbered boxes from floor to ceiling, reinforced walls, contemporary bank interior, purple emergency lighting, year 2020 contemporary setting, no text on boxes",
    },
    
    "evidence_room_cleanup": {
        "name": "Police Evidence Room",
        "description": "Spacious police evidence storage room, tall metal shelving units with wide variety of evidence items including sealed bags, labeled boxes, confiscated weapons on racks, tagged electronics, file folders, larger room with multiple aisles, fluorescent lighting, organized but full storage area, purple undertones from window blinds, year 2020 contemporary setting, no readable text",
    },
    
    "prison_extract": {
        "name": "Custody Extraction",
        "description": "Prison detention facility interior, reinforced concrete walls with heavy steel doors, barred holding cells visible, security checkpoint area with metal detector gateway, institutional gray and blue color scheme, harsh fluorescent lighting with purple undertones, prison bars and secure corridors, year 2020 contemporary setting, no text, no signage",
    },
    
    "dockside_container": {
        "name": "Dockside Container Heist",
        "description": "Shipping container yard at night, stacked cargo containers with numbers, crane in background, security lights, chain-link fencing, forklift parked nearby, industrial atmosphere, purple harbor lights reflecting on wet pavement, year 2020 contemporary setting",
    }
}


def list_scenarios():
    """Print all available scenarios"""
    print("\n" + "="*60)
    print("  AVAILABLE SCENARIOS")
    print("="*60 + "\n")
    
    for scenario_id, design in SCENARIO_DESIGNS.items():
        print(f"🎭 {scenario_id}")
        print(f"   Name: {design['name']}")
        print()


def generate_scenario_image(scenario_id):
    """Generate image for a specific scenario"""
    if scenario_id not in SCENARIO_DESIGNS:
        print(f"❌ Unknown scenario: {scenario_id}")
        print(f"   Available scenarios: {', '.join(SCENARIO_DESIGNS.keys())}")
        sys.exit(1)
    
    design = SCENARIO_DESIGNS[scenario_id]
    
    print("\n" + "="*60)
    print(f"  GENERATING: {design['name']}")
    print("="*60 + "\n")
    
    # Determine output path
    output_path = Path('output/static_images') / f"{scenario_id}.png"
    
    # Generate using Imagen 4.0 (premium tier) with scene-optimized prompts
    generate_scene_image(
        scene_description=design['description'],
        accent_colors="purple",
        output_file=str(output_path)
    )
    
    print(f"✅ Generated {design['name']} scene!")
    print(f"💾 Saved to: {output_path}\n")


def generate_all_scenarios():
    """Generate images for all 11 scenarios"""
    print("\n" + "="*60)
    print("  GENERATING ALL 11 SCENARIO SCENES")
    print("="*60 + "\n")
    print("✨ Using Imagen 4.0 (premium tier - high quality!)")
    print("🎨 Borderlands art style for consistency")
    print("🎭 Dramatic establishing shots for each heist")
    print("💎 Only 11 images, generated once - worth the premium!\n")
    
    successful = []
    failed = []
    
    for i, (scenario_id, design) in enumerate(SCENARIO_DESIGNS.items(), 1):
        print(f"[{i}/11] Generating {design['name']}...")
        print("-" * 60)
        
        try:
            generate_scenario_image(scenario_id)
            successful.append(scenario_id)
        except Exception as e:
            print(f"❌ Failed to generate {scenario_id}: {e}\n")
            failed.append(scenario_id)
        
        if i < len(SCENARIO_DESIGNS):
            print()  # Spacing between generations
    
    # Summary
    print("\n" + "="*60)
    print("  GENERATION COMPLETE")
    print("="*60 + "\n")
    print(f"✅ Successfully generated: {len(successful)}/11 scenarios")
    if successful:
        print(f"   {', '.join(successful)}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}/11 scenarios")
        print(f"   {', '.join(failed)}")
    
    print(f"\n💾 Images saved to: output/static_images/")
    print(f"📱 Ready to use in scenario selection modal!\n")


def main():
    parser = argparse.ArgumentParser(
        description='Generate scene images for all 11 heist scenarios',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all 11 scenarios
  python generate_scenario_images.py
  
  # Generate specific scenario
  python generate_scenario_images.py --scenario museum_gala_vault
  python generate_scenario_images.py --scenario casino_vault_night
  
  # List all available scenarios
  python generate_scenario_images.py --list

Available Scenarios:
  museum_gala_vault, mansion_panic_room, casino_vault_night,
  train_robbery_car, secure_lab_prototype, office_bug_plant,
  art_gallery_swap, bank_safe_deposit, evidence_room_cleanup,
  prison_extract, dockside_container
        """
    )
    
    parser.add_argument(
        '--scenario',
        help='Generate specific scenario only'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available scenarios'
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_scenarios()
    elif args.scenario:
        generate_scenario_image(args.scenario)
    else:
        generate_all_scenarios()


if __name__ == '__main__':
    main()
