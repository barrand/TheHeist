# Inventory & Items Format

## Overview

Items can be found in locations through room searches or obtained from NPCs. Players can pick up, carry, transfer, and use items to complete tasks.

## Format in Experience Files

**IMPORTANT**: Both locations and items MUST have explicit **ID** fields. These IDs determine the image filenames:
- Location images: `location_{id}.png` (e.g., `location_crew_hideout.png`)
- Item images: `item_{id}.png` (e.g., `item_safe_cracking_tools.png`)

### Locations Section Format

```markdown
## Locations

### Crew Hideout (Starting Location)
- **ID**: `crew_hideout`
- **Name**: Crew Hideout
- **Description**: Secret base where the crew plans the heist
- **Visual**: Gritty underground hideout with exposed brick walls...
```

### Location Items Section

Add an `## Items by Location` section listing all discoverable items. Use the location name (not ID) as the section header:

```markdown
## Items by Location

### Crew Hideout
- **ID**: `safe_cracking_tools`
  - **Name**: Safe Cracking Tools
  - **Description**: Professional lockpick set and dial manipulation tools
  - **Visual**: Open black leather case with metallic tools
  - **Required For**: SC2 (Crack the Vault Lock)
  - **Hidden**: false (visible when searching)

- **ID**: `blueprints`
  - **Name**: Museum Blueprints
  - **Description**: Stolen floor plans showing vault location and security systems
  - **Visual**: Rolled architectural blueprints with security markings
  - **Required For**: MM1 (alternative way to learn vault location)
  - **Hidden**: false

### Grand Hall
- **ID**: `guest_list`
  - **Name**: Guest List
  - **Description**: VIP guest list for tonight's gala
  - **Required For**: None (red herring)
  - **Hidden**: false

- **ID**: `security_badge`
  - **Name**: Security Badge
  - **Description**: Dropped security badge - could be useful
  - **Required For**: Multiple tasks (grants access)
  - **Hidden**: true (requires thorough search to find)

### Museum Basement
- **ID**: `vault_key`
  - **Name**: Vault Access Key
  - **Description**: Brass key hanging on the wall - looks important
  - **Required For**: Enter Vault Room (unlocks location)
  - **Hidden**: false
```

## Item Properties

### Core Fields (Required)
- **ID**: Unique identifier (snake_case)
- **Name**: Display name shown to players
- **Description**: What the item is and looks like
- **Location**: Where it's found (set by location section)

### Gameplay Fields
- **Required For**: Task IDs or objectives this item enables
  - Can be task ID (e.g., "SC2")
  - Can be location unlock (e.g., "Enter Vault Room")
  - Can be "None" for flavor items or red herrings
- **Hidden**: Boolean
  - `false` = Discovered with normal search
  - `true` = Requires thorough/multiple searches

### Optional Fields
- **Quantity**: Number available (default: 1)
- **Consumable**: Whether item is used up (default: false)
- **Transferable**: Can give to other players (default: true)

## Item Types

### Mission-Critical Items
Items required to complete objectives:
- Tools for minigames (safe cracking tools, wire cutters)
- Keys and access cards (unlock locations or containers)
- Documents with information (codes, maps, schedules)

### Supporting Items
Items that help but aren't strictly required:
- Disguises
- Distraction items
- Communication devices

### Red Herrings
Items that seem useful but aren't:
- Guest lists
- Irrelevant documents
- Decorative objects

## Gameplay Mechanics

### Room Search
When player taps "🔍 Search" button:
1. Backend checks current location's items
2. Returns list of items at that location
3. Shows "FOUND" screen with items and descriptions
4. Player chooses what to pick up

### Inventory Management
- Each player has their own inventory
- Items take up space (future: could add weight/slot limits)
- Can view in Bag screen (🎒 button)
- Can transfer to players in same room
- Can give to NPCs (if they accept it)

### Item Requirements
Tasks can require items:
```markdown
2. **SC2. 🎮 dial_rotation** - Crack the Vault Lock
   - *Description:* Use safe cracking tools to open the vault
   - *Required Item:* `safe_cracking_tools`
   - *Location:* Vault Room
```

If player doesn't have required item:
- Task shows as locked with "⚠️ Needs: Safe Cracking Tools"
- Player must search Crew Hideout to find the tools
- Once picked up, task becomes available

## Example: Complete Item Flow

1. **Discovery**: MM searches Crew Hideout → Finds "Safe Cracking Tools"
2. **Pickup**: MM picks up tools (added to inventory)
3. **Travel**: MM travels to Grand Hall to meet SC
4. **Transfer**: MM opens Bag → Transfer to SC (both at Grand Hall)
5. **Usage**: SC travels to Vault Room → Task now available (has tools)
6. **Complete**: SC uses tools in minigame to crack vault

## Backend Data Models

Items are stored in:
- `GameState.items_by_location: Dict[str, List[Item]]` - Available items per location
- `Player.inventory: List[Item]` - Items each player is carrying

When item is picked up:
- Removed from location's available items
- Added to player's inventory
- Broadcast to team (optional)

## UI Screens

### Search Results Screen
```
┌─────────────────────────────┐
│  SEARCH RESULTS          ✕  │
│  Crew Hideout               │
│                             │
│  ITEMS FOUND:               │
│  ┌───────────────────────┐ │
│  │ 🔧 Safe Cracking Tools│ │
│  │ Professional lockpick │ │
│  │ set and dial tools    │ │
│  │                       │ │
│  │   [PICK UP]     [ ]   │ │
│  └───────────────────────┘ │
│                             │
│  ┌───────────────────────┐ │
│  │ 📄 Museum Blueprints  │ │
│  │ Floor plans showing   │ │
│  │ vault location        │ │
│  │                       │ │
│  │   [PICK UP]     [ ]   │ │
│  └───────────────────────┘ │
│                             │
│        [DONE]              │
└─────────────────────────────┘
```

### Bag/Inventory Screen
```
┌─────────────────────────────┐
│  YOUR BAG               ✕   │
│                             │
│  CARRYING (2/10):           │
│  ┌───────────────────────┐ │
│  │ 🔧 Safe Cracking Tools│ │
│  │ Professional lockpick │ │
│  │                       │ │
│  │ [USE] [TRANSFER] [X]  │ │
│  └───────────────────────┘ │
│                             │
│  ┌───────────────────────┐ │
│  │ 📄 Museum Blueprints  │ │
│  │ Floor plans showing   │ │
│  │ vault location        │ │
│  │                       │ │
│  │ [USE] [TRANSFER] [X]  │ │
│  └───────────────────────┘ │
│                             │
└─────────────────────────────┘
```

### Transfer Modal (from Bag)
```
┌─────────────────────────────┐
│  TRANSFER ITEM          ✕   │
│  Safe Cracking Tools        │
│                             │
│  WHO'S HERE:                │
│  ┌───────────────────────┐ │
│  │ 👤 Sam (Safe Cracker) │ │
│  │   [GIVE TO SAM]       │ │
│  └───────────────────────┘ │
│                             │
│  ┌───────────────────────┐ │
│  │ 💬 Marcus Romano      │ │
│  │ Security Guard        │ │
│  │   [GIVE TO MARCUS]    │ │
│  └───────────────────────┘ │
│                             │
│        Cancel               │
└─────────────────────────────┘
```
