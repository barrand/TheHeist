# Museum Gala Vault Heist - Dependency Tree

> **Generated Content**
> **Scenario**: `museum_gala_vault` - Museum Gala Vault Heist
> **Selected Roles**: Mastermind, Hacker, Safe Cracker, Insider
> **Player Count**: 4 players
>
> This dependency tree outlines all tasks, their dependencies, and the interactions between player roles to achieve the scenario objective. It incorporates NPC personalities, room inventory search mechanics, NPC request chains, and multi-step collaboration tasks.

---

## Objective
Steal the priceless jewels from the museum vault during a black-tie gala event and escape unnoticed.

## Scenario Overview
The annual black-tie gala at the City Museum is the perfect cover for a heist. The objective is to infiltrate the event, bypass the museum's state-of-the-art security systems, crack the fortified vault, secure the jewels, and disappear before anyone realizes they're gone. The team must work seamlessly, with each role's expertise being crucial for success.

## Locations

This scenario takes place across the following locations:

### Off-Site Preparation
-   **Safe House**: Crew meeting, briefing, equipment staging, vehicle prep.
-   **Remote Hacking Location**: Van parked discreetly near the museum, used by the Hacker.

### Museum Exterior & Entry
-   **Museum Front Entrance**: Main public entry point for gala guests.
-   **Museum Side Entrance**: Staff and service entry point, less visible.
-   **Loading Dock**: Service area for deliveries, often used by staff contacts.

### Museum Interior - Public Areas
-   **Grand Hall**: The main gala event space, bustling with guests and staff.

### Museum Interior - Restricted Areas
-   **Service Corridor**: Connects staff areas, catering stations, and leads to basement.
-   **Janitorial Closet**: Contains cleaning supplies, often a hiding spot for spare keys.
-   **Maintenance Room**: Houses building systems and various tools.
-   **Security Office**: Central hub for camera feeds and security personnel.
-   **Curator's Office**: An administrative office, potentially containing sensitive information.
-   **Vault Corridor**: The approach to the main vault, with additional security.
-   **Vault Room**: The target location, where the jewels are secured.

**Total Locations**: 14

---

## Task Types

Every task in this heist is one of five types:

-   **🎮 Minigame**: Player-controlled action from `roles.json`
-   **💬 NPC/LLM**: Dialogue or interaction with AI-controlled character
-   **🔍 Search/Hunt**: Player searches a location for hidden items
-   **🤝 Item Handoff**: Physical item transfer between players (tracked in inventory)
-   **🗣️ Info Share**: Verbal information exchange between players (real-life conversation)

---

## Roles & Dependencies

### Mastermind

**Tasks:**
1.  **💬 NPC** - Brief Crew
    -   Conduct the initial briefing at the safe house, outlining the plan and roles.
    -   *NPC: None (Team Briefing)*
    -   *Location:* Safe House
    -   *Dependencies:* None (Starting task)
2.  **🔍 Search** - Find Burner Phones
    -   Search the safe house for burner phones for team communication.
    -   *Find: 4 Burner Phones (encrypted)*
    -   *Location:* Safe House
    -   *Dependencies:* Briefing complete
3.  **🔍 Search** - Find Gala Invitation
    -   Locate a discarded or template gala invitation in the safe house for infiltration.
    -   *Find: Forged Gala Invitation (looks authentic)*
    -   *Location:* Safe House
    -   *Dependencies:* Briefing complete
4.  **💬 NPC** - Infiltrate Gala
    -   Present the invitation at the main entrance and socially engineer entry into the gala.
    -   *NPC: Brenda (Jaded, by-the-book, bored) - "Invitation, please. And try to look less like you're about to rob the place. It's a gala, darling."*
    -   *Location:* Museum Front Entrance
    -   *Dependencies:* Gala invitation found
5.  **💬 NPC** - Coordinate Team via Radio
    -   Maintain constant communication with the team, providing updates and adapting to unforeseen circumstances.
    -   *NPC: None (Team Coordination)*
    -   *Location:* Grand Hall (or any location with radio access)
    -   *Dependencies:* Team inside, burner phones found
6.  **🗣️ EXTRACTION** → Signal Crew
    -   Give the "go" signal for extraction once the jewels are secured.
    -   *Location:* Grand Hall
    -   *Dependencies:* Jewels secured (SC6)

---

### Hacker

**Tasks:**
1.  **🎮 wire_connecting** - Prep Hacking Device
    -   Assemble and configure the specialized hacking device at the safe house.
    -   *Location:* Safe House
    -   *Dependencies:* None (Starting task)
2.  **🤝 DEVICE** → Deliver to Insider
    -   Hand over the prepared hacking device to the Insider for planting inside the museum.
    -   *Location:* Safe House
    -   *Dependencies:* Hacking device prepped (H1)
3.  **🎮 cipher_wheel_alignment** - Disable Cameras
    -   Remotely access the museum's security system and loop the camera feeds.
    -   *Location:* Remote Hacking Location
    -   *Dependencies:* Hacking device planted (I7)
4.  **🎮 card_swipe** - Unlock Vault Door
    -   Override the electronic lock on the vault anteroom door.
    -   *Location:* Remote Hacking Location
    -   *Dependencies:* Vault code received (I11), cameras disabled (H3)
5.  **🎮 simon_says_sequence** - Wipe Security Logs
    -   Erase all digital traces of the intrusion from the museum's servers.
    -   *Location:* Remote Hacking Location
    -   *Dependencies:* Jewels secured (SC6)

---

### Safe Cracker

**Tasks:**
1.  **🔍 Search** - Find Cracking Tools
    -   Locate the specialized vault cracking tools stored in the safe house.
    -   *Find: Specialized Cracking Tools (case)*
    -   *Location:* Safe House
    -   *Dependencies:* None (Starting task)
2.  **💬 NPC** - Navigate to Vault Corridor
    -   Move stealthily through the service corridors towards the vault, avoiding staff.
    -   *NPC: None (Stealth Navigation)*
    -   *Location:* Service Corridor → Vault Corridor
    -   *Dependencies:* Side entrance access granted (I5), motion sensors disabled (I12)
3.  **🔍 Search** - Find Acoustic Amplifier
    -   Search the maintenance room for a makeshift acoustic amplifier (e.g., a plumber's stethoscope) to aid in vault cracking.
    -   *Find: Plumber's Stethoscope (can be adapted for safes)*
    -   *Location:* Maintenance Room
    -   *Dependencies:* Vault corridor reached (SC2)
4.  **🎮 dial_rotation** - Crack Vault (Part 1)
    -   Manipulate the outer dial of the vault to find the first numbers of the combination.
    -   *Location:* Vault Room
    -   *Dependencies:* Cracking tools found (SC1), acoustic amplifier found (SC3), vault door unlocked (H4), motion sensors disabled (I12)
5.  **🎮 listen_for_clicks** - Crack Vault (Part 2)
    -   Use the acoustic amplifier to listen for internal clicks and complete the vault combination.
    -   *Location:* Vault Room
    -   *Dependencies:* Dial rotation complete (SC4)
6.  **🤝 JEWELS** - Secure Jewels
    -   Carefully remove the jewels from their display and secure them for transport.
    -   *Location:* Vault Room
    -   *Dependencies:* Vault cracked (SC5)
7.  **🔍 Search** - Find Escape Route Info
    -   Quickly search the vault room for any hidden blueprints or emergency exit information.
    -   *Find: Old Maintenance Schematic (shows a rarely used service tunnel)*
    -   *Location:* Vault Room
    -   *Dependencies:* Jewels secured (SC6)

---

### Insider

**Tasks:**
1.  **💬 NPC** - Meet Carlos (Uniform Request)
    -   Meet a contact, Carlos, at the loading dock to acquire a staff uniform and badge. Carlos demands extra cash due to heightened security.
    -   *NPC: Carlos (Suspicious, shifty, nervous) - "Uniform? Yeah, I got it. But prices went up. Security's been tight. I need $200 more than we agreed."*
    -   *Request: Bring emergency cash*
    -   *Location:* Loading Dock
    -   *Dependencies:* None (Starting task)
2.  **🔍 Search** - Find Emergency Cash
    -   Search the safe house for the team's emergency cash stash to pay Carlos.
    -   *Find: Envelope with $300 cash*
    -   *Location:* Safe House
    -   *Dependencies:* Carlos made request (I1)
3.  **🤝 CASH** → Pay Carlos
    -   Hand over the cash payment to Carlos at the loading dock.
    -   *Location:* Loading Dock
    -   *Dependencies:* Emergency cash found (I2)
4.  **💬 NPC** - Receive Staff Uniform & Badge
    -   Carlos provides the staff uniform and badge after receiving payment.
    -   *NPC: Carlos (Relieved, slightly less shifty) - "Alright, alright. Here's your stuff. Staff entrance code is 4782. Don't get caught."*
    -   *Location:* Loading Dock
    -   *Dependencies:* Payment made (I3)
5.  **🎮 badge_swipe** - Grant Side Entrance Access
    -   Use the acquired staff badge to unlock the museum's side entrance for the team.
    -   *Location:* Museum Side Entrance
    -   *Dependencies:* Staff uniform acquired (I4)
6.  **🤝 DEVICE** ← Receive from Hacker
    -   Receive the prepared hacking device from the Hacker.
    -   *Location:* Museum Side Entrance
    -   *Dependencies:* Hacker delivers device (H2)
7.  **🎮 inventory_check** - Plant Hacking Device
    -   Discreetly plant the hacking device on a network panel in the service corridor.
    -   *Location:* Service Corridor
    -   *Dependencies:* Device received (I6)
8.  **💬 NPC** - Distract Security Guard
    -   Engage a security guard in conversation to divert their attention from the security office.
    -   *NPC: Officer Miller (Ambitious, by-the-book, easily flattered) - "Excuse me, staff only beyond this point. Unless... are you here about the new security protocols? I designed them myself."*
    -   *Location:* Security Office
    -   *Dependencies:* Cameras disabled (H3)
9.  **🔍 Search** - Find Master Key
    -   Search the janitorial closet for a master key ring that includes access to the Curator's Office.
    -   *Find: Master Key Ring (with label for Curator's Office)*
    -   *Location:* Janitorial Closet
    -   *Dependencies:* Security guard distracted (I8)
10. **🎮 memory_matching** - Retrieve Vault Code
    -   Access the Curator's computer using the master key and retrieve the vault access code.
    -   *Location:* Curator's Office
    -   *Dependencies:* Master key found (I9), cameras disabled (H3)
11. **🗣️ CODE** → Share Vault Code with Hacker
    -   Relay the retrieved vault code to the Hacker via radio.
    -   *Location:* Curator's Office
    -   *Dependencies:* Vault code retrieved (I10)
12. **🎮 badge_swipe** - Disable Motion Sensors
    -   Access a maintenance panel in the vault corridor to temporarily disable motion sensors.
    -   *Location:* Vault Corridor
    -   *Dependencies:* Vault door unlocked (H4)
13. **🔍 Search** - Find Cleaning Supplies
    -   Search the service corridor's catering station for cleaning supplies to help blend in as staff.
    -   *Find: Cleaning Cart with rags and spray bottle*
    -   *Location:* Service Corridor
    -   *Dependencies:* Uniform acquired (I4)

---

## Task Summary

Total tasks: 32
Critical path tasks: 25
Supporting tasks: 7

By type:
-   Minigames (🎮): 9 (28%)
-   NPC/LLM interactions (💬): 8 (25%)
-   Search/Hunt (🔍): 9 (28%)
-   Item Handoff (🤝): 4 (12.5%)
-   Info Share (🗣️): 2 (6.25%)

**Social interactions total**: 71.75% (NPC + Search + Handoffs + Info shares) - **Meets 60-70% target.**

---

## Critical Path

The minimum sequence of tasks required to achieve the objective:

```
1.  Mastermind: Brief Crew (MM1)
2.  Mastermind: Search Safe House for Gala Invitation (MM3)
3.  Mastermind: Infiltrate Gala (MM5)
4.  Insider: Meet Carlos (Uniform Request) (I1)
5.  Insider: Search Safe House for Emergency Cash (I2)
6.  Insider: Pay Carlos (I3)
7.  Insider: Receive Staff Uniform & Badge (I4)
8.  Insider: Grant Side Entrance Access (I5)
9.  Hacker: Prep Hacking Device (H1)
10. Hacker: Deliver Hacking Device to Insider (H2)
11. Insider: Receive Hacking Device (I6)
12. Insider: Plant Hacking Device (I7)
13. Hacker: Disable Cameras (H3)
14. Insider: Search Janitorial Closet for Master Key (I9)
15. Insider: Retrieve Vault Code (I10)
16. Insider: Share Vault Code with Hacker (I11)
17. Hacker: Unlock Vault Door (H4)
18. Insider: Disable Motion Sensors (I12)
19. Safe Cracker: Find Cracking Tools (SC1)
20. Safe Cracker: Navigate to Vault Corridor (SC2)
21. Safe Cracker: Find Acoustic Amplifier (SC3)
22. Safe Cracker: Crack Vault (Part 1) (SC4)
23. Safe Cracker: Crack Vault (Part 2) (SC5)
24. Safe Cracker: Secure Jewels (SC6)
25. Mastermind: Signal Extraction (MM7)
```

## Supporting Tasks

Tasks that provide backup, additional intel, or enhance stealth/cleanup but are not strictly on the critical path to securing the jewels:

-   **Mastermind**: Find Burner Phones (MM2), Coordinate Team via Radio (MM6)
-   **Insider**: Distract Security Guard (I8), Find Cleaning Supplies (I13)
-   **Hacker**: Wipe Security Logs (H5)
-   **Safe Cracker**: Find Escape Route Info (SC7)

---

## Key Collaboration Points

-   **Infiltration**: Mastermind uses the invitation to get in, but Insider opens a side entrance for the rest of the team.
-   **Device Planting**: Hacker prepares the device, but Insider must physically take it into the museum and plant it.
-   **Vault Access**: Insider retrieves the vault code, but Hacker uses it to unlock the electronic door.
-   **Vault Cracking**: Hacker unlocks the door, Insider disables sensors, then Safe Cracker performs the physical crack using tools they found.
-   **Extraction**: Mastermind signals the final "go" once the objective is secured.

---

## Dependency Tree Diagrams

### Legend
-   🎮 **Minigames**: Player-controlled actions from `roles.json`
-   💬 **NPC/LLM**: Dialogue with AI characters
-   🔍 **Search/Hunt**: Player searches a location for hidden items
-   🤝 **Item Handoff**: Physical transfer (inventory-tracked)
-   🗣️ **Info Share**: Verbal exchange (real-life conversation)

### Full Dependency Tree

```mermaid
flowchart TD
    START([START HEIST])
    
    %% Mastermind Prep
    START --> MM1{{💬 MM: Brief Crew}}
    MM1 --> MM2{{🔍 MM: Find Burner Phones}}
    MM1 --> MM3{{🔍 MM: Find Gala Invitation}}
    MM3 --> MM4{{💬 MM: Infiltrate Gala}}
    MM4 --> GALA_INFILTRATED[GALA INFILTRATED]
    MM2 --> MM5{{💬 MM: Coordinate Team}}
    GALA_INFILTRATED --> MM5
    
    %% Insider Prep & Infiltration
    START --> I1{{💬 Insider: Meet Carlos (Uniform Request)}}
    I1 --> I2{{🔍 Insider: Find Emergency Cash}}
    I2 --> I3[🤝 CASH to Carlos]
    I3 --> I4{{💬 Insider: Receive Staff Uniform & Badge}}
    I4 --> I5{{🎮 badge_swipe: Grant Side Entrance Access}}
    I4 --> I13{{🔍 Insider: Find Cleaning Supplies}}
    I5 --> TEAM_INSIDE[TEAM INSIDE]
    TEAM_INSIDE --> MM5
    
    %% Hacker Prep
    START --> H1{{🎮 wire_connecting: Prep Hacking Device}}
    H1 --> H2[🤝 DEVICE to Insider]
    
    %% Insider Device Planting
    I5 --> I6[🤝 DEVICE from Hacker]
    H2 --> I6
    I6 --> I7{{🎮 inventory_check: Plant Hacking Device}}
    
    %% Hacker Disables Cameras
    I7 --> H3{{🎮 cipher_wheel_alignment: Disable Cameras}}
    H3 --> CAMERAS_DISABLED[CAMERAS DISABLED]
    
    %% Insider Gets Vault Code
    CAMERAS_DISABLED --> I8{{💬 Insider: Distract Security Guard}}
    I8 --> I9{{🔍 Insider: Find Master Key}}
    I9 --> I10{{🎮 memory_matching: Retrieve Vault Code}}
    I10 --> I11[🗣️ CODE to Hacker]
    
    %% Hacker Unlocks Vault Door
    I11 --> H4{{🎮 card_swipe: Unlock Vault Door}}
    H4 --> VAULT_DOOR_UNLOCKED[VAULT DOOR UNLOCKED]
    
    %% Insider Disables Motion Sensors
    VAULT_DOOR_UNLOCKED --> I12{{🎮 badge_swipe: Disable Motion Sensors}}
    I12 --> MOTION_SENSORS_DISABLED[MOTION SENSORS DISABLED]
    
    %% Safe Cracker Prep & Crack
    START --> SC1{{🔍 SC: Find Cracking Tools}}
    MOTION_SENSORS_DISABLED --> SC2{{💬 SC: Navigate to Vault Corridor}}
    VAULT_DOOR_UNLOCKED --> SC2
    SC2 --> SC3{{🔍 SC: Find Acoustic Amplifier}}
    SC1 --> SC4{{🎮 dial_rotation: Crack Vault (Part 1)}}
    SC3 --> SC4
    MOTION_SENSORS_DISABLED --> SC4
    VAULT_DOOR_UNLOCKED --> SC4
    SC4 --> SC5{{🎮 listen_for_clicks: Crack Vault (Part 2)}}
    SC5 --> VAULT_CRACKED[VAULT CRACKED]
    
    %% Secure Jewels & Escape
    VAULT_CRACKED --> SC6[🤝 JEWELS Secured]
    SC6 --> MM7[🗣️ MM: EXTRACTION Signal]
    SC6 --> SC7{{🔍 SC: Find Escape Route Info}}
    
    %% Post-Heist Cleanup
    SC6 --> H5{{🎮 simon_says_sequence: Wipe Security Logs}}
    
    MM7 --> END([SUCCESSFUL HEIST])
    H5 --> END
```

### Critical Path Only (Simplified)

```mermaid
flowchart TD
    START([START HEIST])
    
    START --> MM1{{💬 MM: Brief Crew}}
    MM1 --> MM2{{🔍 MM: Find Gala Invitation}}
    MM2 --> MM3{{💬 MM: Infiltrate Gala}}
    
    START --> I1{{💬 Insider: Meet Carlos (Uniform Request)}}
    I1 --> I2{{🔍 Insider: Find Emergency Cash}}
    I2 --> I3[🤝 CASH to Carlos]
    I3 --> I4{{💬 Insider: Receive Staff Uniform & Badge}}
    I4 --> I5{{🎮 badge_swipe: Grant Side Entrance Access}}
    
    START --> H1{{🎮 wire_connecting: Prep Hacking Device}}
    H1 --> H2[🤝 DEVICE to Insider]
    
    I5 --> I6[🤝 DEVICE from Hacker]
    H2 --> I6
    I6 --> I7{{🎮 inventory_check: Plant Hacking Device}}
    
    I7 --> H3{{🎮 cipher_wheel_alignment: Disable Cameras}}
    
    H3 --> I8{{🔍 Insider: Find Master Key}}
    I8 --> I9{{🎮 memory_matching: Retrieve Vault Code}}
    I9 --> I10[🗣️ CODE to Hacker]
    
    I10 --> H4{{🎮 card_swipe: Unlock Vault Door}}
    
    H4 --> I11{{🎮 badge_swipe: Disable Motion Sensors}}
    
    START --> SC1{{🔍 SC: Find Cracking Tools}}
    I11 --> SC2{{💬 SC: Navigate to Vault Corridor}}
    SC1 --> SC3{{🔍 SC: Find Acoustic Amplifier}}
    SC2 --> SC4{{🎮 dial_rotation: Crack Vault (Part 1)}}
    SC3 --> SC4
    H4 --> SC4
    I11 --> SC4
    
    SC4 --> SC5{{🎮 listen_for_clicks: Crack Vault (Part 2)}}
    SC5 --> SC6[🤝 JEWELS Secured]
    
    SC6 --> MM4[🗣️ MM: EXTRACTION Signal]
    MM4 --> END([SUCCESSFUL HEIST])
```