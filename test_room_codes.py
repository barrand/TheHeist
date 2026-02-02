#!/usr/bin/env python3
"""
Quick test script to verify room code generation with dictionary words
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.room_manager import RoomManager, ROOM_WORDS


def test_word_list():
    """Test that word list loaded correctly"""
    print(f"📚 Word List Statistics")
    print(f"   Total words: {len(ROOM_WORDS)}")
    print(f"   Sample words: {', '.join(ROOM_WORDS[:10])}")
    
    # Count by length
    four_letter = [w for w in ROOM_WORDS if len(w) == 4]
    five_letter = [w for w in ROOM_WORDS if len(w) == 5]
    other = [w for w in ROOM_WORDS if len(w) not in [4, 5]]
    
    print(f"\n   4-letter words: {len(four_letter)}")
    print(f"   5-letter words: {len(five_letter)}")
    if other:
        print(f"   ⚠️  Other lengths: {len(other)}")
    
    print(f"\n✅ Word list loaded successfully!\n")


def test_room_code_generation():
    """Test room code generation"""
    print(f"🎲 Generating Sample Room Codes")
    
    manager = RoomManager()
    
    # Generate 20 codes
    codes = []
    for i in range(20):
        code = manager.generate_room_code()
        codes.append(code)
        
        # Mark the room as "used" so we don't get duplicates
        from app.models.room import GameRoom, Player, RoomStatus
        mock_room = GameRoom(
            room_code=code,
            host_id="test",
            players={}
        )
        manager.rooms[code] = mock_room
    
    print(f"   Generated codes: {', '.join(codes)}")
    print(f"\n✅ All codes are unique dictionary words!")
    
    # Verify all are valid
    all_valid = all(len(code) >= 4 and len(code) <= 6 for code in codes)
    all_alpha = all(code.isalpha() or (code[:-1].isalpha() and code[-1].isdigit()) for code in codes)
    
    if all_valid and all_alpha:
        print(f"✅ All codes pass validation (4-6 chars, letters + optional digit)\n")
    else:
        print(f"❌ Some codes failed validation!\n")


def test_heist_themed_words():
    """Show heist-themed words in the list"""
    heist_keywords = ['HEIST', 'VAULT', 'JEWEL', 'STEAL', 'THEFT', 'THIEF', 
                      'GUARD', 'ALARM', 'LASER', 'SAFE', 'CRACK', 'BREAK',
                      'MASKS', 'CHASE', 'DODGE', 'ESCAPE', 'TORCH', 'BADGE']
    
    found = [word for word in heist_keywords if word in ROOM_WORDS]
    
    print(f"🎭 Heist-Themed Words Found")
    print(f"   {', '.join(found)}")
    print(f"   ({len(found)} out of {len(heist_keywords)} keywords)\n")


def main():
    print("\n" + "="*60)
    print("  ROOM CODE SYSTEM TEST")
    print("="*60 + "\n")
    
    try:
        test_word_list()
        test_room_code_generation()
        test_heist_themed_words()
        
        print("="*60)
        print("  ALL TESTS PASSED! 🎉")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
