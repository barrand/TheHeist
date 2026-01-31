# Museum Gala Vault Heist - Dependency Tree

> **Generated Content**  
> **Scenario**: `museum_gala_vault` - Museum Gala Vault Heist  
> **Selected Roles**: Mastermind, Hacker, Safe Cracker, Insider  
> **Player Count**: 4 players  

---

## Objective
Steal the priceless "Star of Andromeda" diamond from the museum vault during the annual black-tie gala and escape unnoticed.

## Scenario Overview
The prestigious "Star of Andromeda" diamond is the centerpiece of the annual Museum Gala, displayed in a high-security vault in the museum's basement. The event is teeming with wealthy guests, vigilant security, and sophisticated electronic countermeasures. The 4-player crew must infiltrate the gala as invited guests and staff, disable cameras and motion sensors, crack the vault's physical and electronic locks, secure the diamond, and execute a clean, silent escape.

## Locations

This scenario takes place across the following locations:

### Off-Site Preparation
- **Safe House** - Crew meeting, briefing, equipment storage
- **Hacker's Van** - Remote access point for Hacker (parked near museum)

### Museum Exterior
- **Museum Front Entrance** - Main gala entrance, public access
- **Museum Side Entrance** - Staff/service entrance (restricted)
- **Alleyway Behind Museum** - Discrete area for item handoffs and potential escape

### Museum Interior - Public Areas
- **Grand Hall** - Main gala space, guest mingling, diamond exhibit display (before vault transfer)
- **Coat Check** - Guest storage, lost & found, potential search area
- **Guest Restrooms** - Public facilities, potential search area for cleaning supplies

### Museum Interior - Staff/Restricted Areas
- **Catering Station** - Service corridor area, staff presence, supplies
- **Security Room** - Camera feeds, guard station, security system controls
- **Janitorial Closet** - Cleaning supplies, potential for master keys
- **Curator's Office** - Administrative office, contains vault code on computer
- **Maintenance Room** - Building systems, tools, motion sensor controls

### Vault Area
- **Vault Corridor** - Approach to the main vault, motion sensors
- **Vault Room** - Target location, diamond display, multi-layered vault

### Escape
- **Getaway Vehicle** - Parked near a discrete exit point for final escape

**Total Locations**: 15

---

## Task Types

Every task in this heist is one of five types:

- **🎮 Minigame**: Player-controlled action from `roles.json`
- **💬 NPC/LLM**: Dialogue or interaction with AI-controlled character
- **🔍 Search/Hunt**: Player searches a location for hidden items
- **🤝 Item Handoff**: Physical item transfer between players (tracked in inventory)
- **🗣️ Info Share**: Verbal information exchange between players (real-life conversation)

---

## Roles & Dependencies

### Mastermind

**Tasks:**
1.  **🔍 Search** - Hunt for Museum Blueprints
    - Locate the detailed museum blueprints in the safe house for planning.
    - *Find: Museum Blueprints (detailed layout, security schematics)*
    - *Location:* Safe House
    - *Dependencies:* None (starting task)
2.  **💬 NPC** - Brief Crew in Safe House
    - Review blueprints, assign roles, set contingencies, outline critical path.
    - *NPC: None (Internal crew briefing)*
    - *Location:* Safe House
    - *Dependencies:* Blueprints found
3.  **💬 NPC** - Infiltrate Gala
    - Socially engineer entry at the main entrance, using charm and confidence to bypass initial checks.
    - *NPC: Bouncer Boris (imposing, by-the-book, easily impressed by authority) - "Invitation, sir? And your name on the guest list? I don't see your name here..."*
    - *Location:* Museum Front Entrance
    - *Dependencies:* Crew briefed
4.  **💬 NPC** - Coordinate Team via Radio
    - Use encrypted radio to synchronize movements, adapt to complications, and provide real-time instructions.
    - *NPC: None (Internal crew communication)*
    - *Location:* Grand Hall
    - *Dependencies:* Team inside museum
5.  **🔍 Search** - Hunt for a Guest's Lost Phone
    - Find a valuable item to return to an NPC, earning trust or creating a distraction.
    - *Find: High-end smartphone (contains contact info)*
    - *Location:* Coat Check
    - *Dependencies:* Team inside museum
6.  **💬 NPC** - Create Diversion with Lost Phone
    - Return the lost phone to a prominent guest, creating a scene or distracting staff.
    - *NPC: Socialite Penelope (narcissistic, chatty, easily flattered) - "Oh my goodness, my phone! You're a lifesaver! I was just about to call my publicist about this ghastly lighting!"*
    - *Location:* Grand Hall
    - *Dependencies:* Lost phone found
7.  **🗣️ EXTRACTION_SIGNAL** → Signal Crew
    - Give the "go" signal over the radio when the vault is open and the diamond secured, initiating the escape.
    - *Location:* Grand Hall
    - *Dependencies:* Diamond secured, Hacker wiped logs
8.  **🤝 JEWELS** ← Receive from Safe Cracker
    - Take possession of the "Star of Andromeda" diamond for the final getaway.
    - *Location:* Alleyway Behind Museum
    - *Dependencies:* Safe Cracker brings diamond

### Hacker

**Tasks:**
1.  **🔍 Search** - Hunt for Specialized Ethernet Cable
    - Locate the specific cable needed for the custom hacking device.
    - *Find: CAT8 Ethernet cable (short, braided)*
    - *Location:* Hacker's Van
    - *Dependencies:* None (starting task)
2.  **🎮 wire_connecting** - Prep Hacking Device
    - Assemble the custom USB hacking device, connecting colored wires to match ports on both sides.
    - *Location:* Hacker's Van
    - *Dependencies:* Ethernet cable found
3.  **🔍 Search** - Hunt for a Backup Power Bank
    - Find a portable power bank to ensure the hacking device stays charged during critical operations.
    - *Find: High-capacity power bank*
    - *Location:* Hacker's Van
    - *Dependencies:* Device prepped
4.  **🤝 HACK_DEVICE** → Deliver to Insider
    - Pass the prepared hacking device to the Insider for discreet planting.
    - *Location:* Alleyway Behind Museum
    - *Dependencies:* Device prepped, power bank found
5.  **🎮 cipher_wheel_alignment** - Disable Cameras
    - Access the museum's security system remotely and loop camera feeds, creating a blind spot.
    - *Location:* Hacker's Van (Remote Access)
    - *Dependencies:* Hacking device planted by Insider
6.  **🗣️ VAULT_CODE** ← Receive from Insider
    - Get the digital vault access code via radio communication from the Insider.
    - *Location:* Hacker's Van (Radio Communication)
    - *Dependencies:* Insider retrieves code
7.  **🎮 card_swipe** - Unlock Vault Door
    - Override the electronic lock on the vault's main door from the remote access point.
    - *Location:* Hacker's Van (Remote Access)
    - *Dependencies:* Vault code received, cameras disabled
8.  **🎮 simon_says_sequence** - Wipe Security Logs
    - Erase all digital traces of the intrusion from the museum's servers before the team makes their final exit.
    - *Location:* Hacker's Van (Remote Access)
    - *Dependencies:* Diamond secured, extraction signal

### Safe Cracker

**Tasks:**
1.  **🔍 Search** - Hunt for Basic Lockpick Set
    - Locate the essential lockpicking tools from the safe house equipment stash.
    - *Find: Professional-grade lockpick set (various rakes and tension wrenches)*
    - *Location:* Safe House
    - *Dependencies:* None (starting task)
2.  **🤝 LOCKPICKS** ← Receive from Safe Cracker (Self)
    - Secure the basic lockpick set in personal inventory.
    - *Location:* Safe House
    - *Dependencies:* Lockpicks found
3.  **💬 NPC** - Navigate to Vault Corridor
    - Blend in with staff or use stealth to move through restricted basement corridors towards the vault.
    - *NPC: Janitor Eddie (conspiracy theorist, bored, gossipy) - "You ain't seen nothin'. Just keep movin'. I heard the director arguing about the diamond's insurance, something's fishy."*
    - *Location:* Vault Corridor (Approach)
    - *Dependencies:* Building access granted, motion sensors disabled
4.  **🔍 Search** - Hunt for Acoustic Stethoscope
    - Find a specialized listening device (e.g., from maintenance) to accurately hear the vault tumblers.
    - *Find: Industrial Acoustic Stethoscope (for pipes, but works for safes)*
    - *Location:* Maintenance Room
    - *Dependencies:* Vault corridor reached, vault door unlocked
5.  **🔍 Search** - Hunt for Loose Floor Tile
    - Search the vault corridor for a hidden compartment or forgotten maintenance key under a loose tile.
    - *Find: Small emergency key for a utility panel*
    - *Location:* Vault Corridor
    - *Dependencies:* Vault corridor reached
6.  **🎮 dial_rotation** - Crack Vault (Part 1)
    - Manipulate the outer dial of the vault door, stopping at precise numbers to align the first set of tumblers.
    - *Location:* Vault Room
    - *Dependencies:* Stethoscope found, lockpicks secured, vault door unlocked
7.  **🎮 listen_for_clicks** - Crack Vault (Part 2)
    - Use the acoustic stethoscope to listen for the internal clicks of the tumblers, completing the combination.
    - *Location:* Vault Room
    - *Dependencies:* Dial rotation complete
8.  **🤝 JEWELS** ← Receive from Safe Cracker (Self)
    - Secure the "Star of Andromeda" diamond from its display case into a padded pouch.
    - *Location:* Vault Room
    - *Dependencies:* Vault open
9.  **🤝 JEWELS** → Deliver to Mastermind
    - Hand over the secured diamond to the Mastermind at the designated rendezvous point for final extraction.
    - *Location:* Alleyway Behind Museum
    - *Dependencies:* Diamond secured, extraction signal

### Insider

**Tasks:**
1.  **💬 NPC** - Meet Stressed Caterer
    - Approach a busy caterer to obtain a staff uniform, who is too stressed to help unless a favor is done.
    - *NPC: Caterer Sofia (stressed, nervous, overworked) - "Uniform? I can't even find my truffle oil! Chef is going to kill me if I don't get those canapés out!"*
    - *Request: Bring Rare Truffle Oil*
    - *Location:* Catering Station
    - *Dependencies:* None (starting task)
2.  **🔍 Search** - Hunt for Rare Truffle Oil
    - Search the catering station's supply shelves for the specific ingredient requested by the caterer.
    - *Find: Bottle of artisanal truffle oil*
    - *Location:* Catering Station
    - *Dependencies:* Caterer made request
3.  **🤝 TRUFFLE_OIL** → Deliver to Caterer
    - Hand over the found truffle oil to the grateful caterer.
    - *Location:* Catering Station
    - *Dependencies:* Truffle oil found
4.  **💬 NPC** - Receive Staff Uniform & Badge
    - The relieved caterer provides a spare staff uniform and access badge as thanks.
    - *NPC: Caterer Sofia - "Oh thank god! Here, take this spare uniform and badge. Just... don't tell anyone I gave it to you."*
    - *Location:* Catering Station
    - *Dependencies:* Truffle oil delivered
5.  **🎮 badge_swipe** - Grant Side Entrance Access
    - Use the acquired staff badge to unlock the museum's side entrance for the team.
    - *Location:* Museum Side Entrance
    - *Dependencies:* Staff uniform and badge acquired
6.  **🤝 HACK_DEVICE** ← Receive from Hacker
    - Get the hacking device from the Hacker at a discreet handoff point.
    - *Location:* Alleyway Behind Museum
    - *Dependencies:* Hacker delivers device
7.  **💬 NPC** - Distract Security Guard to Plant Device
    - Engage a security guard in conversation, creating an opportunity to discreetly plant the hacking device.
    - *NPC: Officer Jenkins (bored, suspicious, easily distracted by gossip) - "Staff only back here. What's going on? Is it true the curator is getting fired?"*
    - *Location:* Security Room
    - *Dependencies:* Hacking device received, cameras disabled
8.  **🎮 badge_swipe** - Plant Hacking Device
    - While the guard is distracted, use the badge to access a network port and plug in the hacking device. (Minigame represents the precision of plugging it in without being noticed).
    - *Location:* Security Room
    - *Dependencies:* Guard distracted
9.  **💬 NPC** - Distract Museum Curator
    - Keep the curator occupied in the Grand Hall, ensuring their office remains clear for access.
    - *NPC: Dr. Aris Chen (narcissistic, pedantic, art-obsessed) - "Indeed, the symbolism of the Star of Andromeda is often misinterpreted. Allow me to elaborate on its cosmological significance..."*
    - *Location:* Grand Hall
    - *Dependencies:* Cameras disabled
10. **🔍 Search** - Hunt for Master Key
    - Locate a master key ring in the janitorial closet, needed to access the Curator's Office.
    - *Find: Master Key Ring (includes Curator's Office key)*
    - *Location:* Janitorial Closet
    - *Dependencies:* Curator distracted, cameras disabled
11. **🎮 memory_matching** - Retrieve Vault Code
    - Access the Curator's computer (requires key) and play a memory game to recall the briefly displayed vault code.
    - *Location:* Curator's Office
    - *Dependencies:* Master key found, curator distracted
12. **🗣️ VAULT_CODE** → Share with Hacker
    - Radio the retrieved vault code to the Hacker for remote vault access.
    - *Location:* Curator's Office
    - *Dependencies:* Vault code retrieved
13. **🎮 badge_swipe** - Disable Motion Sensors
    - Access a maintenance panel in the Maintenance Room and use the staff badge to deactivate motion sensors in the Vault Corridor.
    - *Location:* Maintenance Room
    - *Dependencies:* Vault door unlocked
14. **🔍 Search** - Hunt for Cleaning Supplies
    - Find a spray bottle and cloth in the restrooms for minor cleanup of fingerprints on door handles.
    - *Find: All-purpose cleaning spray and microfiber cloth*
    - *Location:* Guest Restrooms
    - *Dependencies:* Extraction signal given
15. **🤝 CLEANING_SUPPLIES** → Deliver to Safe Cracker
    - Pass the cleaning supplies to the Safe Cracker for immediate fingerprint wiping in the vault area.
    - *Location:* Vault Corridor
    - *Dependencies:* Cleaning supplies found
16. **💬 NPC** - Create Diversion (False Alarm)
    - Trigger a minor, non-critical alarm (e.g., fire alarm pull station in a non-essential area) to draw security away from the escape route.
    - *NPC: None (system interaction)*
    - *Location:* Service Corridor
    - *Dependencies:* Extraction signal given
17. **🎮 inventory_check** - Dispose of Uniform/Badge
    - Quickly remove and stash the staff uniform and badge in a discreet location before exiting the museum.
    - *Location:* Museum Side Entrance
    - *Dependencies:* Diversion created

---

## Critical Path

The minimum sequence of tasks required to achieve the objective:

1.  **Mastermind**: `🔍 Search: Safe House for Museum Blueprints`
2.  **Mastermind**: `💬 NPC: Brief Crew in Safe House`
3.  **Mastermind**: `💬 NPC: Infiltrate Gala`
4.  **Hacker**: `🔍 Search: Hacker's Van for Specialized Ethernet Cable`
5.  **Hacker**: `🎮 wire_connecting: Prep Hacking Device`
6.  **Hacker**: `🤝 HACK_DEVICE` → Deliver to Insider
7.  **Insider**: `💬 NPC: Meet Stressed Caterer` (Request: Truffle Oil)
8.  **Insider**: `🔍 Search: Catering Station for Rare Truffle Oil`
9.  **Insider**: `🤝 TRUFFLE_OIL` → Deliver to Caterer
10. **Insider**: `💬 NPC: Receive Staff Uniform & Badge`
11. **Insider**: `🎮 badge_swipe: Grant Side Entrance Access`
12. **Insider**: `💬 NPC: Distract Security Guard to Plant Device` (Needs Hacking Device from Hacker)
13. **Insider**: `🎮 badge_swipe: Plant Hacking Device`
14. **Hacker**: `🎮 cipher_wheel_alignment: Disable Cameras`
15. **Insider**: `💬 NPC: Distract Museum Curator`
16. **Insider**: `🔍 Search: Janitorial Closet for Master Key`
17. **Insider**: `🎮 memory_matching: Retrieve Vault Code`
18. **Insider**: `🗣️ VAULT_CODE` → Share with Hacker
19. **Hacker**: `🎮 card_swipe: Unlock Vault Door`
20. **Insider**: `🎮 badge_swipe: Disable Motion Sensors`
21. **Safe Cracker**: `🔍 Search: Safe House for Basic Lockpick Set`
22. **Safe Cracker**: `🤝 LOCKPICKS` ← Receive from Safe Cracker (Self)
23. **Safe Cracker**: `💬 NPC: Navigate to Vault Corridor`
24. **Safe Cracker**: `🔍 Search: Maintenance Room for Acoustic Stethoscope`
25. **Safe Cracker**: `🎮 dial_rotation: Crack Vault (Part 1)`
26. **Safe Cracker**: `🎮 listen_for_clicks: Crack Vault (Part 2)`
27. **Safe Cracker**: `🤝 JEWELS` ← Receive from Safe Cracker (Self)
28. **Hacker**: `🎮 simon_says_sequence: Wipe Security Logs`
29. **Mastermind**: `🗣️ EXTRACTION_SIGNAL` → Signal Crew
30. **Safe Cracker**: `🤝 JEWELS` → Deliver to Mastermind
31. **Mastermind**: `🤝 JEWELS` ← Receive from Safe Cracker
32. **Insider**: `💬 NPC: Create Diversion (False Alarm)`
33. **Insider**: `🎮 inventory_check: Dispose of Uniform/Badge`
34. **Mastermind**: `💬 NPC: Coordinate Escape` (Final social engineering to exit)
35. **Mastermind**: Escape with Jewels (Implicit final action)

## Supporting Tasks

Tasks that provide backup, intelligence, or cleanup, enhancing success but not strictly required for the critical path:

-   **Mastermind**: `🔍 Search: Coat Check for a Guest's Lost Phone`, `💬 NPC: Create Diversion with Lost Phone`
-   **Hacker**: `🔍 Search: Hacker's Van for a Backup Power Bank`
-   **Safe Cracker**: `🔍 Search: Vault Corridor for Loose Floor Tile` (potentially finds a useful item, but not critical)
-   **Insider**: `🔍 Search: Guest Restrooms for Cleaning Supplies`, `🤝 CLEANING_SUPPLIES` → Deliver to Safe Cracker

## Task Summary

Total tasks: 42  
Critical path tasks: 35  
Supporting tasks: 7  

By type:
-   Minigames (🎮): 12 (28.5%)
-   NPC/LLM interactions (💬): 11 (26.2%)
-   Search/Hunt (🔍): 10 (23.8%)
-   Item handoffs (🤝): 7 (16.7%)
-   Info shares (🗣️): 3 (7.1%)

**Social interactions total**: 73.8% (NPC + Search + Handoffs + Info shares)

**Key Collaboration Points:**
-   Mastermind's initial briefing sets the stage for all roles.
-   Hacker's device is critical and must be handed off to the Insider for planting.
-   Insider's uniform acquisition is a multi-step NPC request chain.
-   Insider's distraction of the guard enables the planting of the device.
-   Hacker's camera disablement opens the way for Insider and Safe Cracker.
-   Insider's retrieval and sharing of the vault code is essential for Hacker.
-   Hacker's vault door unlock enables Insider to disable motion sensors.
-   Insider's motion sensor disablement allows Safe Cracker to approach the vault safely.
-   Safe Cracker requires tools found via search and access provided by other roles to crack the vault.
-   Safe Cracker's diamond handoff to Mastermind is the final objective transfer.
-   Hacker's log wipe and Insider's diversion/cleanup are crucial for a clean escape, coordinated by Mastermind.

**NPC Personality Highlights:**
Each NPC interaction is designed to be unique:
-   **Bouncer Boris**: Imposing but susceptible to confident social engineering.
-   **Caterer Sofia**: Stressed and overworked, requiring a specific item to be appeased.
-   **Officer Jenkins**: Bored and prone to gossip, easily distracted by juicy rumors.
-   **Dr. Aris Chen**: Narcissistic and pedantic, loves to talk about himself and his "expertise."
-   **Janitor Eddie**: Conspiracy theorist, bored with his job, but might offer cryptic hints.
-   **Socialite Penelope**: Flamboyant and easily flattered, creates a scene when her phone is returned.

These personalities create varied social challenges, encouraging players to adapt their approach and enhancing replayability.

---

## Dependency Tree Diagrams

### Legend
- 🎮 **Minigames**: Player-controlled actions from `roles.json`
- 💬 **NPC/LLM**: Dialogue with AI characters
- 🔍 **Search/Hunt**: Player searches a location for hidden items
- 🤝 **Item Handoff**: Physical transfer (inventory-tracked)
- 🗣️ **Info Share**: Verbal exchange (real-life conversation)
- [STATE] : Milestone or state achieved

### Full Dependency Tree

```mermaid
flowchart TD
    START([START HEIST])
    
    %% Mastermind Prep
    START --> MM1_S{{🔍 Search: Safe House for Blueprints}}
    MM1_S --> MM2_C{{💬 MM: Brief Crew in Safe House}}
    
    %% Hacker Prep
    START --> H1_S{{🔍 Search: Hacker's Van for Ethernet Cable}}
    H1_S --> H2_G{{🎮 wire_connecting: Prep Hacking Device}}
    H2_G --> H3_S{{🔍 Search: Hacker's Van for Power Bank}}
    H3_S --> H4_H[🤝 HACK_DEVICE to Insider]
    
    %% Safe Cracker Prep
    START --> SC1_S{{🔍 Search: Safe House for Lockpick Set}}
    SC1_S --> SC2_H[🤝 LOCKPICKS to SC]
    
    %% Insider Prep (NPC Request Chain)
    START --> I1_C{{💬 Insider: Meet Stressed Caterer}}
    I1_C --> I2_S{{🔍 Search: Catering Station for Truffle Oil}}
    I2_S --> I3_H[🤝 TRUFFLE_OIL to Caterer]
    I3_H --> I4_C{{💬 Insider: Receive Staff Uniform & Badge}}
    I4_C --> I5_G{{🎮 badge_swipe: Grant Side Entrance Access}}
    
    %% Infiltration
    MM2_C --> MM3_C{{💬 MM: Infiltrate Gala}}
    MM3_C --> TEAM_INSIDE[TEAM INSIDE MUSEUM]
    I5_G --> TEAM_INSIDE
    
    %% Hacker Device Planting
    TEAM_INSIDE --> I6_H[🤝 HACK_DEVICE from Hacker]
    I6_H --> I7_C{{💬 Insider: Distract Security Guard to Plant Device}}
    I7_C --> I8_G{{🎮 badge_swipe: Plant Hacking Device}}
    
    %% Hacker Disables Cameras
    I8_G --> H5_G{{🎮 cipher_wheel_alignment: Disable Cameras}}
    CAMERAS_DISABLED[CAMERAS DISABLED]
    H5_G --> CAMERAS_DISABLED
    
    %% Mastermind Supports
    TEAM_INSIDE --> MM4_C{{💬 MM: Coordinate Team via Radio}}
    CAMERAS_DISABLED --> MM5_S{{🔍 Search: Coat Check for Lost Phone}}
    MM5_S --> MM6_C{{💬 MM: Create Diversion with Lost Phone}}
    
    %% Insider Gets Vault Code
    CAMERAS_DISABLED --> I9_C{{💬 Insider: Distract Museum Curator}}
    I9_C --> I10_S{{🔍 Search: Janitorial Closet for Master Key}}
    I10_S --> I11_G{{🎮 memory_matching: Retrieve Vault Code}}
    I11_G --> I12_F[🗣️ VAULT_CODE to Hacker]
    
    %% Hacker Unlocks Vault Door
    I12_F --> H6_G{{🎮 card_swipe: Unlock Vault Door}}
    VAULT_DOOR_UNLOCKED[VAULT DOOR UNLOCKED]
    H6_G --> VAULT_DOOR_UNLOCKED
    
    %% Insider Disables Sensors
    VAULT_DOOR_UNLOCKED --> I13_G{{🎮 badge_swipe: Disable Motion Sensors}}
    MOTION_SENSORS_DISABLED[MOTION SENSORS DISABLED]
    I13_G --> MOTION_SENSORS_DISABLED
    
    %% Safe Cracker Cracks Vault
    SC2_H --> SC3_C{{💬 SC: Navigate to Vault Corridor}}
    MOTION_SENSORS_DISABLED --> SC3_C
    VAULT_DOOR_UNLOCKED --> SC3_C
    SC3_C --> SC4_S{{🔍 Search: Maintenance Room for Stethoscope}}
    SC3_C --> SC5_S{{🔍 Search: Vault Corridor for Loose Tile}}
    SC4_S --> SC6_G{{🎮 dial_rotation: Crack Vault (Part 1)}}
    SC2_H --> SC6_G
    SC6_G --> SC7_G{{🎮 listen_for_clicks: Crack Vault (Part 2)}}
    SC7_G --> VAULT_OPEN[VAULT OPEN]
    VAULT_OPEN --> SC8_H[🤝 JEWELS to SC]
    DIAMOND_SECURED[DIAMOND SECURED]
    SC8_H --> DIAMOND_SECURED
    
    %% Escape & Cleanup
    DIAMOND_SECURED --> H7_G{{🎮 simon_says_sequence: Wipe Security Logs}}
    LOGS_WIPED[LOGS WIPED]
    H7_G --> LOGS_WIPED
    
    DIAMOND_SECURED --> MM7_F[🗣️ EXTRACTION_SIGNAL to Crew]
    LOGS_WIPED --> MM7_F
    
    MM7_F --> SC9_H[🤝 JEWELS to MM]
    DIAMOND_SECURED --> SC9_H
    
    MM7_F --> I14_S{{🔍 Search: Restrooms for Cleaning Supplies}}
    I14_S --> I15_H[🤝 CLEANING_SUPPLIES to SC]
    
    MM7_F --> I16_C{{💬 Insider: Create Diversion (False Alarm)}}
    MM7_F --> I17_G{{🎮 inventory_check: Dispose of Uniform/Badge}}
    
    SC9_H --> MM8_H[🤝 JEWELS from SC]
    I15_H --> SC_CLEANUP[SC WIPES FINGERPRINTS]
    
    MM8_H --> MM9_C{{💬 MM: Coordinate Escape}}
    I16_C --> MM9_C
    I17_G --> MM9_C
    SC_CLEANUP --> MM9_C
    
    MM9_C --> END([CLEAN GETAWAY SUCCESS])
```

### Critical Path Only (Simplified)

```mermaid
flowchart TD
    START([START])
    
    START --> MM1{{🔍 Search: Blueprints}}
    MM1 --> MM2{{💬 MM: Brief Crew}}
    MM2 --> MM3{{💬 MM: Infiltrate Gala}}
    
    START --> H1{{🔍 Search: Ethernet Cable}}
    H1 --> H2{{🎮 wire_connecting: Prep Device}}
    H2 --> H3[🤝 HACK_DEVICE to Insider]
    
    START --> I1{{💬 Insider: Meet Caterer}}
    I1 --> I2{{🔍 Search: Truffle Oil}}
    I2 --> I3[🤝 TRUFFLE_OIL to Caterer]
    I3 --> I4{{💬 Insider: Get Uniform}}
    I4 --> I5{{🎮 badge_swipe: Grant Access}}
    
    MM3 --> I6[🤝 HACK_DEVICE from Hacker]
    I5 --> I6
    
    I6 --> I7{{💬 Insider: Distract Guard to Plant Device}}
    I7 --> I8{{🎮 badge_swipe: Plant Device}}
    
    I8 --> H4{{🎮 cipher_wheel_alignment: Disable Cameras}}
    
    H4 --> I9{{💬 Insider: Distract Curator}}
    I9 --> I10{{🔍 Search: Master Key}}
    I10 --> I11{{🎮 memory_matching: Get Vault Code}}
    I11 --> I12[🗣️ VAULT_CODE to Hacker]
    
    I12 --> H5{{🎮 card_swipe: Unlock Vault Door}}
    
    H5 --> I13{{🎮 badge_swipe: Disable Motion Sensors}}
    
    START --> SC1{{🔍 Search: Lockpick Set}}
    SC1 --> SC2[🤝 LOCKPICKS to SC]
    
    I13 --> SC3{{💬 SC: Navigate to Vault}}
    SC2 --> SC3
    H5 --> SC3
    
    SC3 --> SC4{{🔍 Search: Stethoscope}}
    SC4 --> SC5{{🎮 dial_rotation: Crack Vault (Part 1)}}
    SC5 --> SC6{{🎮 listen_for_clicks: Crack Vault (Part 2)}}
    SC6 --> SC7[🤝 JEWELS to SC]
    
    SC7 --> H6{{🎮 simon_says_sequence: Wipe Logs}}
    H6 --> MM4[🗣️ EXTRACTION_SIGNAL]
    
    MM4 --> SC8[🤝 JEWELS to MM]
    MM4 --> I14{{💬 Insider: Create Diversion}}
    MM4 --> I15{{🎮 inventory_check: Dispose Uniform}}
    
    SC8 --> MM5[🤝 JEWELS from SC]
    I14 --> MM6{{💬 MM: Coordinate Escape}}
    I15 --> MM6
    MM5 --> MM6
    
    MM6 --> END([SUCCESS])
```