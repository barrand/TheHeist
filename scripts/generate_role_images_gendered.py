#!/usr/bin/env python3
"""
Generate character portraits for all 12 heist roles in male and female versions.

Each role is generated twice - once as male, once as female - keeping ethnicity consistent.
This allows players to see themselves represented in the character they choose.

Usage:
    python generate_role_images_gendered.py              # Generate all roles (male + female)
    python generate_role_images_gendered.py --role hacker  # Generate specific role (both genders)
    python generate_role_images_gendered.py --gender female # Generate all roles as female only
    python generate_role_images_gendered.py --list        # List all roles
"""

import argparse
import sys
from pathlib import Path
from generate_npc_image import generate_npc_image


# ============================================
# ROLE CHARACTER DESIGNS
# ============================================
# Each role has ethnicity-specific design that works for both male and female

ROLE_DESIGNS = {
    "mastermind": {
        "name": "The Mastermind",
        "role": "Strategic Planner",
        "ethnicity": "distinguished 40-year-old Indian",
        "clothing": "tailored suit with rolled-up sleeves, tactical vest over dress shirt",
        "background": "command center with blueprints, maps, and monitors displaying floor plans",
        "expression": "confident and calculating",
        "details": "holding tablet showing heist blueprints, wearing smart glasses",
        "attitude": "commanding and intelligent, natural leader",
        "accent_colors": "purple",
        "description": "The strategic brain behind every operation - calm, collected, always three steps ahead"
    },
    
    "hacker": {
        "name": "The Hacker",
        "role": "Tech Specialist",
        "ethnicity": "young Korean",
        "clothing": "tech hoodie with cyberpunk patches, fingerless gloves, AR glasses",
        "background": "dark room filled with multiple glowing monitors showing code and security feeds",
        "expression": "focused and intense",
        "details": "neon underglow on equipment, tangled cables and wires around, laptop open",
        "attitude": "tech-obsessed genius, in the zone",
        "accent_colors": "purple",
        "description": "Master of digital security - if it's electronic, they can crack it"
    },
    
    "safe_cracker": {
        "name": "The Safe Cracker",
        "role": "Lock Expert",
        "ethnicity": "Middle Eastern",
        "clothing": "worn leather jacket, tool belt with precision instruments, magnifying headset",
        "background": "vault room with massive safe door, combination dials visible",
        "expression": "concentrated and precise",
        "details": "holding stethoscope against safe, lockpicking tools visible in belt",
        "attitude": "patient craftsman, meticulous perfectionist",
        "accent_colors": "purple",
        "description": "No lock too complex, no vault too secure - patient hands and sharp ears"
    },
    
    "driver": {
        "name": "The Driver",
        "role": "Getaway Specialist",
        "ethnicity": "Latina/Latino",
        "clothing": "leather racing jacket with sponsor patches, driving gloves, aviator sunglasses",
        "background": "urban street at night with sleek getaway car behind, city lights blurred",
        "expression": "cool and confident",
        "details": "holding car keys, radio earpiece visible, racing watch on wrist",
        "attitude": "fearless adrenaline junkie, ice-cool under pressure",
        "accent_colors": "purple",
        "description": "Born behind the wheel - lightning reflexes and intimate knowledge of every back street"
    },
    
    "insider": {
        "name": "The Insider",
        "role": "Legitimate Access",
        "ethnicity": "professional Black",
        "clothing": "crisp business suit, company ID badge prominently displayed, polished appearance",
        "background": "corporate office lobby with security checkpoint and marble floors",
        "expression": "trustworthy and professional",
        "details": "holding briefcase and access card, perfectly groomed, company lanyard",
        "attitude": "legitimate and above suspicion, dual identity",
        "accent_colors": "purple",
        "description": "The key to the front door - legitimate employee with insider knowledge and access"
    },
    
    "grifter": {
        "name": "The Grifter",
        "role": "Social Engineer",
        "ethnicity": "charismatic European",
        "clothing": "expensive designer suit, silk pocket square, luxury watch, perfectly styled",
        "background": "elegant hotel lobby or gala event, well-dressed crowd blurred in background",
        "expression": "charming and disarming smile",
        "details": "holding champagne glass, multiple fake badges and IDs subtly visible in pocket",
        "attitude": "silver-tongued smooth talker, can talk their way into anywhere",
        "accent_colors": "purple",
        "description": "Master manipulator - a different story for every mark, charm that opens any door"
    },
    
    "muscle": {
        "name": "The Muscle",
        "role": "Physical Security",
        "ethnicity": "imposing Polynesian with muscular build",
        "clothing": "tactical gear, reinforced vest, fingerless tactical gloves, combat boots",
        "background": "industrial warehouse or loading dock, dramatic lighting",
        "expression": "intimidating but controlled",
        "details": "ear piece visible, utility belt with tactical equipment, muscular build",
        "attitude": "quiet intensity, speaks through presence not words",
        "accent_colors": "purple",
        "description": "The enforcer - handles physical obstacles and provides silent intimidation when needed"
    },
    
    "lookout": {
        "name": "The Lookout",
        "role": "Surveillance Expert",
        "ethnicity": "sharp-eyed 15-year-old South Asian",
        "clothing": "tactical urban wear, multiple pockets, binoculars around neck, night vision goggles on head",
        "background": "rooftop overlooking city at dusk, multiple camera feeds on tablet",
        "expression": "alert and observant",
        "details": "holding radio, tablet showing security camera grid, scanning surroundings",
        "attitude": "hyper-aware eagle eye, notices everything others miss",
        "accent_colors": "purple",
        "description": "Eyes and ears of the operation - never misses a detail, sees threats before they arrive"
    },
    
    "fence": {
        "name": "The Fence",
        "role": "Equipment Supplier",
        "ethnicity": "street-smart 40-year-old white",
        "clothing": "vintage jacket covered in pins and patches, multiple rings, layers of necklaces",
        "background": "cluttered back-alley shop filled with stolen goods, antiques, and equipment",
        "expression": "shrewd and calculating",
        "details": "examining jewel with magnifying loupe, surrounded by tools and forgeries",
        "attitude": "wheeler-dealer, knows the value of everything",
        "accent_colors": "purple",
        "description": "The connect - if you need it, they can get it, for the right price"
    },
    
    "cat_burglar": {
        "name": "The Cat Burglar",
        "role": "Stealth Infiltrator",
        "ethnicity": "agile Japanese",
        "clothing": "form-fitting black stealth suit, climbing harness, soft-soled boots, balaclava pulled down",
        "background": "high-rise building exterior at night, dangling from rope, city lights far below",
        "expression": "focused and fearless",
        "details": "grappling equipment visible, climbing gloves, laser grid pattern reflected in eyes",
        "attitude": "graceful shadow, moves like smoke",
        "accent_colors": "purple",
        "description": "Gravity-defying infiltrator - goes over, under, and through where others can't follow"
    },
    
    "cleaner": {
        "name": "The Cleaner",
        "role": "Evidence Expert",
        "ethnicity": "meticulous Scandinavian",
        "clothing": "professional dark suit with latex gloves tucked in pocket, subtle cleaning supplies holster",
        "background": "sterile workspace with UV lights revealing fingerprints on surfaces",
        "expression": "calm and methodical",
        "details": "holding UV flashlight, spray bottle visible, wearing subtle forensic equipment",
        "attitude": "ghost who leaves no trace, making problems disappear",
        "accent_colors": "purple",
        "description": "Makes it like you were never there - erases evidence, cleans up mistakes, ghosts the scene"
    },
    
    "pickpocket": {
        "name": "The Pickpocket",
        "role": "Sleight of Hand Artist",
        "ethnicity": "street-smart 15-year-old Southeast Asian",
        "clothing": "inconspicuous casual street clothes, light jacket with hidden pockets, sneakers",
        "background": "crowded street or train station, blurred pedestrians passing by",
        "expression": "innocent and unassuming",
        "details": "hands in natural position showing subtle sleight-of-hand gesture, wallet half-visible",
        "attitude": "ghost in plain sight, invisible in crowds",
        "accent_colors": "purple",
        "description": "Fingers faster than the eye - lifts wallets, keys, and badges without anyone noticing"
    }
}


def get_ethnicity_for_gender(ethnicity, gender):
    """Convert gender-neutral ethnicity to gendered version"""
    if gender == "male":
        return f"{ethnicity} man"
    else:  # female
        return f"{ethnicity} woman"


def list_roles():
    """Print all available roles"""
    print("\n" + "="*60)
    print("  AVAILABLE ROLES (Male & Female versions)")
    print("="*60 + "\n")
    
    for role_id, design in ROLE_DESIGNS.items():
        print(f"🎭 {role_id}")
        print(f"   Name: {design['name']}")
        print(f"   Ethnicity: {design['ethnicity']}")
        print(f"   Description: {design['description']}")
        print()


def generate_role_image(role_id, gender="both"):
    """Generate image for a specific role"""
    if role_id not in ROLE_DESIGNS:
        print(f"❌ Unknown role: {role_id}")
        print(f"   Available roles: {', '.join(ROLE_DESIGNS.keys())}")
        sys.exit(1)
    
    design = ROLE_DESIGNS[role_id]
    genders_to_generate = ["male", "female"] if gender == "both" else [gender]
    
    for gen in genders_to_generate:
        print("\n" + "="*60)
        print(f"  GENERATING: {design['name']} ({gen.upper()})")
        print("="*60 + "\n")
        print(f"📝 {design['description']}\n")
        
        # Determine output path
        output_path = Path('output/role_images') / f"{role_id}_{gen}.png"
        
        # Get gendered ethnicity
        ethnicity_gendered = get_ethnicity_for_gender(design['ethnicity'], gen)
        
        # Generate using the NPC image script
        generate_npc_image(
            name=design['name'],
            role=design['role'],
            gender=gen,
            ethnicity=ethnicity_gendered,
            clothing=design['clothing'],
            background=design['background'],
            expression=design['expression'],
            details=design['details'],
            attitude=design['attitude'],
            accent_colors=design['accent_colors'],
            output_file=str(output_path)
        )
        
        print(f"✅ Generated {design['name']} ({gen}) portrait!")
        print(f"💾 Saved to: {output_path}\n")


def generate_all_roles(gender="both"):
    """Generate images for all 12 roles"""
    genders_to_generate = ["male", "female"] if gender == "both" else [gender]
    total_images = len(ROLE_DESIGNS) * len(genders_to_generate)
    
    print("\n" + "="*60)
    print(f"  GENERATING {total_images} ROLE PORTRAITS")
    print("="*60 + "\n")
    print(f"🎨 Borderlands art style for consistency")
    print(f"👥 Generating {', '.join(genders_to_generate)} version(s)")
    print(f"🎭 12 unique roles\n")
    
    successful = []
    failed = []
    count = 0
    
    for role_id, design in ROLE_DESIGNS.items():
        for gen in genders_to_generate:
            count += 1
            print(f"[{count}/{total_images}] Generating {design['name']} ({gen})...")
            print("-" * 60)
            
            try:
                # Generate single gender version
                generate_role_image(role_id, gender=gen)
                successful.append(f"{role_id}_{gen}")
            except Exception as e:
                print(f"❌ Failed to generate {role_id} ({gen}): {e}\n")
                failed.append(f"{role_id}_{gen}")
            
            if count < total_images:
                print()  # Spacing between generations
    
    # Summary
    print("\n" + "="*60)
    print("  GENERATION COMPLETE")
    print("="*60 + "\n")
    print(f"✅ Successfully generated: {len(successful)}/{total_images} images")
    if successful:
        print(f"   {', '.join(successful)}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}/{total_images} images")
        print(f"   {', '.join(failed)}")
    
    print(f"\n💾 Images saved to: output/role_images/")
    print(f"📱 Ready to use in role selection modal!\n")


def main():
    parser = argparse.ArgumentParser(
        description='Generate character portraits for all 12 heist roles (male & female)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all roles (male + female = 24 images)
  python generate_role_images_gendered.py
  
  # Generate all roles as female only
  python generate_role_images_gendered.py --gender female
  
  # Generate specific role (both genders)
  python generate_role_images_gendered.py --role hacker
  
  # Generate specific role as male only
  python generate_role_images_gendered.py --role hacker --gender male
  
  # List all available roles
  python generate_role_images_gendered.py --list

Available Roles:
  mastermind, hacker, safe_cracker, driver, insider, grifter,
  muscle, lookout, fence, cat_burglar, cleaner, pickpocket
        """
    )
    
    parser.add_argument(
        '--role',
        help='Generate specific role only (e.g., "hacker", "mastermind")'
    )
    
    parser.add_argument(
        '--gender',
        choices=['male', 'female', 'both'],
        default='both',
        help='Generate male, female, or both versions (default: both)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available roles'
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_roles()
    elif args.role:
        generate_role_image(args.role, gender=args.gender)
    else:
        generate_all_roles(gender=args.gender)


if __name__ == '__main__':
    main()
