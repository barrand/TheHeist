# Museum Gala Vault Heist - Experience File

**ID**: `museum_gala_vault`
**Scenario**: Museum Gala Vault Heist
**Selected Roles**: Mastermind, Safe Cracker
**Player Count**: 2 players

## 🎯 Team Objectives

These are the high-level goals visible to both players from the start.

1.  **Infiltrate the Gala**: Gain access to the museum interior without raising suspicion.
2.  **Access and Crack the Vault**: Locate the vault, bypass its security, and open it.
3.  **Steal the Jewels and Escape**: Secure the target jewels and exit the museum unnoticed.

## Scenario Overview

The city's most prestigious Natural History Museum is hosting its annual black-tie gala, a perfect cover for a heist. The legendary "Eye of Orion" jewels are on display in a state-of-the-art vault located in the museum's basement. Security is tight, featuring armed guards, advanced camera systems, motion sensors, and a sophisticated vault lock. The Mastermind will orchestrate the infiltration, gather critical intelligence, and manage distractions, while the Safe Cracker will handle physical bypasses, system disabling, and the ultimate challenge of cracking the vault. The goal is to get in, get the jewels, and get out, leaving no trace behind.

## Locations

This scenario takes place across the following locations:

### Off-Site Preparation
-   **Safe House** - Crew meeting, briefing, equipment staging.
-   **Getaway Vehicle Staging** - Driver's pre-arranged parking spot for the getaway car.

### Museum Exterior
-   **Museum Front Steps** - Main entrance, public arrival, red carpet.
-   **Museum Side Entrance** - Staff/service entrance, less visible.

### Museum Interior - Public Areas
-   **Grand Hall** - Main gala space, guest mingling, champagne fountain, exhibits.
-   **Coat Check Room** - Guest item storage, often unattended.
-   **Gift Shop (Closed)** - Public area, but closed during gala; potential access point.

### Museum Interior - Staff/Restricted Areas
-   **Security Checkpoint** - Entry point to staff areas, usually manned.
-   **Service Corridor (Catering Station)** - Staff passages, food prep, deliveries.
-   **Janitor's Closet** - Cleaning supplies, potential master keys.
-   **Curator's Office** - Administrative office, personal items, potential clues.
-   **Security Room** - Camera feeds, guard station, security system controls.
-   **Maintenance Room** - Building systems, electrical panels, tools.

### Vault Area
-   **Vault Corridor** - Approach to the vault, often with additional security.
-   **Vault Room** - Target location, jewel display.

**Total Locations**: 15

## Task Types

Every task in this heist is one of five types:

-   **🎮 Minigame**: Player-controlled action from `roles.json`
-   **💬 NPC/LLM**: Dialogue or interaction with AI-controlled character
-   **🔍 Search/Hunt**: Player searches a location for hidden items
-   **🤝 Item Handoff**: Physical item transfer between players (tracked in inventory)
-   **🗣️ Info Share**: Verbal information exchange between players (real-life conversation)

## Discovery Tasks

Here are the key discovery moments that will unfold during the heist:

1.  **SC: Examine the Main Vault Door** (`SC_EXAMINE_VAULT_DOOR_01`)
    *   **Type**: Object Examination
    *   **Discovery**: Reveals the specific model of the vault, its primary locking mechanism (6-digit combination), and a secondary electronic lock. Crucial for planning.

2.  **MM: Observe Gala Flow & Security** (`MM_OBSERVE_GALA_01`)
    *   **Type**: Environmental Observation
    *   **Discovery**: Identifies guard patrol patterns, camera coverage gaps (blind spots), and key choke points in the public areas.

3.  **SC: Search Curator's Desk** (`SC_SEARCH_CURATOR_DESK_01`)
    *   **Type**: Environmental Storytelling
    *   **Discovery**: Finds a partially shredded note with a partial combination segment and a hint about the curator's routine or a specific date.

4.  **MM: Talk to the Overworked Caterer** (`MM_TALK_CATERER_01`)
    *   **Type**: NPC Information Exchange (Request Chain)
    *   **Discovery**: The caterer, Sofia, is stressed and needs a specific vintage champagne. Helping her reveals potential staff-only access codes or a hidden keycard location.

5.  **SC: Examine Security Panel in Maintenance Room** (`SC_EXAMINE_MAINTENANCE_PANEL_01`)
    *   **Type**: Object Examination
    *   **Discovery**: Identifies the panel controlling vault corridor motion sensors. Reveals it's an old model that can be manually bypassed with careful timing.

6.  **MM: Investigate Staff Entrance Access Point** (`MM_INVESTIGATE_STAFF_ENTRANCE_01`)
    *   **Type**: Environmental Observation & NPC Interaction
    *   **Discovery**: Reveals the staff entrance requires a keycard and is guarded by Frank, who appears easily distracted by his phone.

## Roles & Dependencies

### Mastermind

**Tasks:**
1.  **MM1. 💬 NPC** - Brief Safe Cracker in Safehouse
    *   *Description:* Review blueprints, discuss initial plan, assign roles for recon.
    *   *NPC: Yourself (Mastermind, focused, strategic) - "Alright, this is the plan. We hit the museum during the gala. You handle the hardware, I'll handle the social. Let's start with recon."*
    *   *Location:* Safe House
    *   *Dependencies:* None (starting task)

2.  **MM2. 💬 NPC** - Infiltrate Gala
    *   *Description:* Blend in with guests, present invitation if needed, gain entry.
    *   *NPC: Doorman (stoic, by-the-book) - "Invitation, please. Enjoy the gala."*
    *   *Location:* Museum Front Steps
    *   *Dependencies:* `MM1` (briefing complete)

3.  **MM3. 🔍 Observe Gala Flow & Security** `[DISCOVERY]`
    *   *Description:* Discreetly watch guard patrols, identify camera locations, look for patterns or weaknesses.
    *   *Discovery:* "Guards patrol every 15 minutes, but there's a 5-minute window when they converge near the champagne fountain. Cameras cover main hall, but the service corridor is a blind spot."
    *   *Spawns:* `MM4` (Distract Main Hall Guard), `SC1` (Scout Service Corridor)
    *   *Location:* Grand Hall
    *   *Dependencies:* `MM2` (inside gala)

4.  **MM4. 💬 NPC** - Distract Main Hall Guard `[TEAM TASK]`
    *   *Description:* Engage a patrolling guard in conversation to divert their attention from a key area.
    *   *NPC: Officer Miller (bored, complains about long shifts) - "Another gala. Just standing here, watching rich people eat tiny food. I'd kill for a decent burger."*
    *   *Location:* Grand Hall
    *   *Dependencies:* `MM3` (observed patterns)

5.  **MM5. 💬 NPC** - Talk to the Overworked Caterer `[DISCOVERY]`
    *   *Description:* Approach a stressed caterer, see if they need help or have useful information.
    *   *NPC: Sofia (stressed, nervous, overworked) - "The chef is furious! I need a specific bottle of vintage champagne from the cellar for a VIP, and I can't leave my station!"*
    *   *Discovery:* "Caterer needs a specific item. If helped, she might reveal staff-only access codes or a hidden keycard location."
    *   *Spawns:* `SC2` (Find Vintage Champagne), `MM6` (Get Staff Keycard Location from Caterer - dependent on champagne)
    *   *Location:* Service Corridor (Catering Station)
    *   *Dependencies:* `MM3` (observed blind spots, allowing access)

6.  **MM6. 💬 NPC** - Get Staff Keycard Location from Caterer
    *   *Description:* Deliver the champagne to Sofia, then subtly ask about staff access.
    *   *NPC: Sofia (relieved, grateful) - "Oh, thank goodness! Here, take this old staff keycard I found in my apron, it might still work for the staff entrance. And the vault's combination? I overheard the director saying it's the museum's founding year, 1932, plus the current year..."*
    *   *Location:* Service Corridor (Catering Station)
    *   *Dependencies:* `SC3` (champagne delivered), `SC_ACQUIRE_STAFF_KEYCARD_01` (spawns this task)

7.  **MM7. 💬 NPC** - Distract Staff Entrance Guard `[TEAM TASK]`
    *   *Description:* Engage the guard at the staff entrance to create an opening.
    *   *NPC: Frank (burned out, obsessed with fantasy football) - "Another gala. Just standing here, watching rich people eat tiny food. I'd kill for a decent burger."*
    *   *Clue Design:* MM distracts him with fantasy football talk. Frank mumbles about "the curator always changing his password, something about a special date, like '47' or '32'..." (partial combination clue).
    *   *Location:* Museum Side Entrance
    *   *Dependencies:* `MM_INVESTIGATE_STAFF_ENTRANCE_01` (discovered guard)

8.  **MM8. 🗣️ INFO** - Share Combination Clue with SC
    *   *Description:* Relay any combination digits or hints gathered to the Safe Cracker.
    *   *Location:* Radio Communication
    *   *Dependencies:* `MM6` (Caterer clue), `MM7` (Guard clue)

9.  **MM9. 💬 NPC** - Coordinate Escape Route
    *   *Description:* Radio to the getaway driver, confirm readiness and clear path.
    *   *Location:* Museum Side Entrance (near exit)
    *   *Dependencies:* `SC_SECURE_JEWELS_01` (jewels secured)

### Safe Cracker

**Tasks:**
1.  **SC1. 🔍 Search** - Scout Service Corridor
    *   *Description:* Look for an inconspicuous entry point into staff-only areas.
    *   *Find: Unlocked service door leading to a back staircase.*
    *   *Location:* Service Corridor
    *   *Dependencies:* `MM3` (observed blind spot)

2.  **SC2. 🔍 Search** - Find Vintage Champagne
    *   *Description:* Search the museum's cellar or storage areas for the specific vintage champagne Sofia needs.
    *   *Find: Bottle of "Château Lafite Rothschild 1982" champagne.*
    *   *Location:* Gift Shop (Closed) (back storage area)
    *   *Dependencies:* `MM5` (Caterer's request)

3.  **SC3. 🤝 CHAMPAGNE** → Deliver to Mastermind
    *   *Description:* Hand over the champagne to the Mastermind to give to Sofia.
    *   *Location:* Service Corridor (Catering Station)
    *   *Dependencies:* `SC2` (champagne found)

4.  **SC4. 🎮 lockpick_timing** - Bypass Keycard Reader (Staff Entrance)
    *   *Description:* Use a specialized tool to bypass the electronic lock on the staff entrance.
    *   *Location:* Museum Side Entrance
    *   *Dependencies:* `SC_ACQUIRE_STAFF_KEYCARD_01` (keycard acquired) or `MM7` (Guard distracted)

5.  **SC5. 🔍 Examine the Main Vault Door** `[DISCOVERY]`
    *   *Description:* Inspect the vault door to determine its model, locking mechanisms, and any visible weaknesses.
    *   *Discovery:* "Vanderbilt Model 3200. Needs a 6-digit combination. There's also a secondary electronic lock."
    *   *Spawns:* `SC6` (Bypass Electronic Lock), `SC_FIND_VAULT_COMBINATION_01` (Team Task)
    *   *Location:* Vault Room
    *   *Dependencies:* `SC4` (accessed staff areas)

6.  **SC6. 🎮 lockpick_timing** - Bypass Electronic Lock (Vault Door)
    *   *Description:* Use a specialized bypass tool on the vault's electronic secondary lock.
    *   *Location:* Vault Room
    *   *Dependencies:* `SC5` (vault examined)

7.  **SC7. 🔍 Search** - Curator's Desk `[DISCOVERY]`
    *   *Description:* Search the curator's office for clues, documents, or items related to the vault combination.
    *   *Discovery:* "Found a partially shredded note. '...first two digits...47...schedule...'. Looks like the curator uses personal dates for security."
    *   *Spawns:* `MM8` (Share Combination Clue with SC), `SC_FIND_REMAINING_COMBINATION_CLUES_01` (Team Task)
    *   *Location:* Curator's Office
    *   *Dependencies:* `SC_FIND_VAULT_COMBINATION_01` (task spawned)

8.  **SC8. 🔍 Examine Security Panel in Maintenance Room** `[DISCOVERY]`
    *   *Description:* Inspect the electrical panel in the maintenance room for controls related to the vault area.
    *   *Discovery:* "This panel controls the motion sensors in the vault corridor. It's an old model, looks like it can be manually bypassed with careful timing."
    *   *Spawns:* `SC9` (Disable Vault Corridor Motion Sensors)
    *   *Location:* Maintenance Room
    *   *Dependencies:* `SC6` (electronic lock bypassed)

9.  **SC9. 🎮 lockpick_timing** - Disable Vault Corridor Motion Sensors
    *   *Description:* Carefully disable the motion sensors in the vault corridor by manipulating the maintenance panel.
    *   *Location:* Maintenance Room
    *   *Dependencies:* `SC8` (panel examined)

10. **SC10. 🗣️ INFO** - Receive Combination Clues from Mastermind
    *   *Description:* Listen to the Mastermind's radio updates on combination digits or hints.
    *   *Location:* Radio Communication
    *   *Dependencies:* `MM8` (MM shares clues)

11. **SC11. 🎮 dial_rotation** - Crack Vault (Part 1)
    *   *Description:* Manipulate the main dial, using the gathered combination digits to align the tumblers.
    *   *Location:* Vault Room
    *   *Dependencies:* `SC9` (motion sensors disabled), `SC10` (received combination clues)

12. **SC12. 🎮 listen_for_clicks** - Crack Vault (Part 2)
    *   *Description:* Use auditory cues and a stethoscope to fine-tune the dial, listening for the final clicks that unlock the vault.
    *   *Location:* Vault Room
    *   *Dependencies:* `SC11` (dial rotation part 1 complete)

13. **SC13. 🤝 JEWELS** - Secure and Transport Jewels
    *   *Description:* Carefully remove the "Eye of Orion" jewels from their display and prepare for transport.
    *   *Location:* Vault Room
    *   *Dependencies:* `SC12` (vault cracked)

14. **SC14. 💬 NPC** - Escape through Side Entrance
    *   *Description:* Exit the museum via the pre-arranged side entrance.
    *   *Location:* Museum Side Entrance
    *   *Dependencies:* `SC13` (jewels secured), `MM9` (escape coordinated)

## Key Collaboration Points

*   **Infiltration**: Mastermind observes, Safe Cracker acts on observed weaknesses (e.g., bypassing a lock).
*   **Information Gathering**: Mastermind socializes for clues, Safe Cracker searches physical locations for other clues. Both relay information (`MM8`, `SC10`).
*   **Distractions**: Mastermind initiates distractions (e.g., `MM4`, `MM7`) to create openings for Safe Cracker to move or perform tasks.
*   **Item Handoffs**: Safe Cracker finds key items (e.g., champagne, keycard) and hands them off to Mastermind for social tasks, or vice versa for technical tasks.
*   **Vault Access**: Mastermind provides critical combination clues, Safe Cracker executes the cracking minigames.
*   **Escape**: Mastermind coordinates the final getaway, Safe Cracker secures the objective.

## Task Summary

Total tasks: 23
Critical path tasks: 16
Supporting tasks: 7

By type:
-   Minigames (🎮): 8 (35%)
-   NPC/LLM interactions (💬): 9 (39%)
-   Search/Hunt (🔍): 4 (17%)
-   Item handoffs (🤝): 2 (9%)
-   Info shares (🗣️): 2 (9%)

**Social interactions total**: 74% (NPC + Search + Handoffs + Info shares)

## Dependency Tree Diagrams

### Legend
-   🎮 **Minigames**: Player-controlled actions from `roles.json`
-   💬 **NPC/LLM**: Dialogue with AI characters
-   🤝 **Item Handoff**: Physical transfer (inventory-tracked)
-   🗣️ **Info Share**: Verbal exchange (real-life conversation)

### Full Dependency Tree

```mermaid
flowchart TD
    START([START HEIST])

    %% Mastermind Tasks
    START --> MM1{💬 MM: Brief SC in Safehouse}
    MM1 --> MM2{💬 MM: Infiltrate Gala}
    MM2 --> GALA_INFILTRATED[GALA INFILTRATED]

    GALA_INFILTRATED --> MM3{🔍 MM: Observe Gala Flow & Security}
    MM3 --> MM4{💬 MM: Distract Main Hall Guard}
    MM3 --> MM5{💬 MM: Talk to Overworked Caterer}
    MM3 --> MM_INVESTIGATE_STAFF_ENTRANCE_01{💬 MM: Investigate Staff Entrance Access Point}

    MM5 --> SC2{🔍 SC: Find Vintage Champagne}
    SC2 --> SC3[🤝 CHAMPAGNE to MM]
    SC3 --> MM6{💬 MM: Get Staff Keycard Location from Caterer}

    MM_INVESTIGATE_STAFF_ENTRANCE_01 --> MM7{💬 MM: Distract Staff Entrance Guard}
    MM6 --> MM8[🗣️ INFO: Share Combination Clue with SC]
    MM7 --> MM8

    %% Safe Cracker Tasks
    GALA_INFILTRATED --> SC1{🔍 SC: Scout Service Corridor}
    SC1 --> STAFF_AREA_ACCESS[STAFF AREA ACCESS]
    MM7 --> SC4{🎮 lockpick_timing: Bypass Keycard Reader (Staff Entrance)}
    STAFF_AREA_ACCESS --> SC4
    MM6 --> SC4

    SC4 --> VAULT_CORRIDOR_ACCESSIBLE[VAULT CORRIDOR ACCESSIBLE]
    VAULT_CORRIDOR_ACCESSIBLE --> SC5{🔍 SC: Examine Main Vault Door}

    SC5 --> SC6{🎮 lockpick_timing: Bypass Electronic Lock (Vault Door)}
    SC5 --> SC7{🔍 SC: Search Curator's Desk}
    SC5 --> SC8{🔍 SC: Examine Security Panel in Maintenance Room}

    SC6 --> SC9{🎮 lockpick_timing: Disable Vault Corridor Motion Sensors}
    SC8 --> SC9

    MM8 --> SC10[🗣️ INFO: Receive Combination Clues from MM]
    SC7 --> SC10

    SC9 --> SC11{🎮 dial_rotation: Crack Vault (Part 1)}
    SC10 --> SC11
    SC11 --> SC12{🎮 listen_for_clicks: Crack Vault (Part 2)}
    SC12 --> VAULT_CRACKED[VAULT CRACKED]

    VAULT_CRACKED --> SC13[🤝 JEWELS: Secure and Transport Jewels]
    SC13 --> JEWELS_SECURED[JEWELS SECURED]

    JEWELS_SECURED --> MM9{💬 MM: Coordinate Escape Route}
    MM9 --> SC14{💬 SC: Escape through Side Entrance}
    SC14 --> HEIST_COMPLETE([HEIST COMPLETE])
```

### Critical Path Only (Simplified)

```mermaid
flowchart TD
    START([START HEIST])

    START --> MM1{💬 MM: Brief SC}
    MM1 --> MM2{💬 MM: Infiltrate Gala}
    MM2 --> MM3{🔍 MM: Observe Gala Security}
    MM3 --> MM_INVESTIGATE_STAFF_ENTRANCE_01{💬 MM: Investigate Staff Entrance}
    MM_INVESTIGATE_STAFF_ENTRANCE_01 --> MM7{💬 MM: Distract Staff Guard}

    MM7 --> SC4{🎮 lockpick_timing: Bypass Keycard Reader}
    SC4 --> SC5{🔍 SC: Examine Vault Door}
    SC5 --> SC6{🎮 lockpick_timing: Bypass Electronic Lock}
    SC5 --> SC7{🔍 SC: Search Curator's Desk}
    SC5 --> SC8{🔍 SC: Examine Maintenance Panel}

    SC6 --> SC9{🎮 lockpick_timing: Disable Motion Sensors}
    SC8 --> SC9

    SC7 --> SC10[🗣️ INFO: Receive Combination Clues]
    MM3 --> SC10
    
    SC9 --> SC11{🎮 dial_rotation: Crack Vault (Part 1)}
    SC10 --> SC11
    SC11 --> SC12{🎮 listen_for_clicks: Crack Vault (Part 2)}

    SC12 --> SC13[🤝 JEWELS: Secure Jewels]
    SC13 --> MM9{💬 MM: Coordinate Escape}
    MM9 --> SC14{💬 SC: Escape}
    SC14 --> HEIST_COMPLETE([HEIST COMPLETE])
```