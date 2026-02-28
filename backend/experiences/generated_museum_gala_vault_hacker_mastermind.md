---
---
---
---
---
---
# Infiltrate the high-security 'Aether's Echo' gala, bypass its cutting-edge biometric defenses, and steal the legendary 'Star of Cygnus' diamond from its deep vault before dawn.

**ID**: `museum_gala_vault`
**Scenario**: Infiltrate the high-security 'Aether's Echo' gala, bypass its cutting-edge biometric defenses, and steal the legendary 'Star of Cygnus' diamond from its deep vault before dawn.
**Selected Roles**: Hacker, Mastermind
**Player Count**: 2 players

## Objective
Infiltrate the high-security 'Aether's Echo' gala, bypass its cutting-edge biometric defenses, and steal the legendary 'Star of Cygnus' diamond from its deep vault before dawn.

## Locations

### Exterior
- **The Grand Façade** (`grand_facade`): Rain-slicked cobblestones reflect the dazzling lights spilling from the Beaux-Arts museum entrance, where velvet ropes funnel a stream of elegantly dressed patrons.

### Interior
- **Nebula Ballroom** (`nebula_ballroom`): Under a ceiling painted with swirling constellations, the opulent ballroom buzzes with high society, champagne flutes clinking amidst soft jazz and hushed conversations.
- **Curator's Private Study** (`curators_private_study`): Hidden behind a rotating bookshelf in a quiet gallery, this cluttered office is filled with antique maps, rare books, and a half-empty decanter of aged scotch.
- **Archival Data Core** (`archival_data_core`): A cold, hum-filled server room where blinking indicator lights illuminate rows of silent, climate-controlled servers storing the museum's entire digital history and security protocols.
- **Sub-Basement Service Tunnels** (`sub_basement_tunnels`): A labyrinth of damp, echoing concrete passages, thick with exposed pipes and conduit, leading deeper into the museum's forgotten foundations.
- **The Chronos Lock** (`chronos_lock`): A circular antechamber of polished steel and reinforced glass, guarded by a temporal displacement field shimmering with faint blue energy and laser grids.

**Total Locations**: 6

## Items by Location

### Archival Data Core
- **Data Core Maintenance Manual** (`item_5`)
  - **Description**: A comprehensive guide for accessing and maintaining the archival data systems.
  - **Visual**: A thick, worn technical manual with complex diagrams and schematics, its cover dusty and corners dog-eared.
  - **Hidden**: false

- **Backup Drive Encryption Key** (`item_6`)
  - **Description**: A specialized cryptographic key for accessing encrypted emergency data backups.
  - **Visual**: A small, metallic USB drive with a single, softly pulsing blue LED and an intricate, almost alien-like symbol etched into its casing.
  - **Hidden**: true
  - **Unlock**:
    - Task `MM1`
    - Task `H3`

### The Chronos Lock
- **Chronos Lock Schematic** (`item_9`)
  - **Description**: The intricate blueprint detailing the vault's unique time-activated locking mechanism.
  - **Visual**: A large, translucent vellum sheet showcasing highly detailed diagrams of gears, circuits, and quantum entanglement components, glowing faintly.
  - **Hidden**: false

- **Biometric Scanner Calibrator** (`item_10`)
  - **Description**: A specialized tool used to adjust and fine-tune the Chronos Lock's biometric scanner.
  - **Visual**: A sleek, handheld device with a small, glowing touchscreen displaying complex waveform patterns and a precise calibration dial.
  - **Hidden**: false

### Curator's Private Study
- **Curator's Login Note** (`item_4`)
  - **Description**: A sticky note with what appears to be the curator's old login credentials.
  - **Visual**: A slightly crumpled yellow sticky note, stuck to a monitor, with smudged but legible handwriting for a username and password.
  - **Hidden**: false

### The Grand Façade
- **Gala Invitation Chip** (`item_1`)
  - **Description**: An ornate card with an embedded RFID chip for event access.
  - **Visual**: A shimmering, heavy cardstock invitation with intricate gold leaf patterns and a small, glowing RFID chip embedded near the crest.
  - **Hidden**: false

- **Façade Security Schematic** (`item_2`)
  - **Description**: A detailed layout of the museum's exterior surveillance system.
  - **Visual**: A rolled-up blueprint, slightly faded, showing detailed architectural plans with hand-drawn camera icons and coverage arcs.
  - **Hidden**: false

- **The Stellar Key** (`item_11`)
  - **Description**: An ancient, otherworldly artifact rumored to unlock any vault, transcending conventional security.
  - **Visual**: An ornate, glowing key forged from unknown iridescent metal, constantly shifting with cosmic patterns and emitting a faint, ethereal hum.
  - **Hidden**: true
  - **Unlock**:
    - Task `H2`

- **Vault Door Access Log** (`item_12`)
  - **Description**: A digital record of all recent entries and attempts on the Cosmic Strongroom's vault door.
  - **Visual**: A robust, military-grade tablet displaying a chronological list of access times, user IDs, and biometric scan results, highlighted in green and red.
  - **Hidden**: false

### Nebula Ballroom
- **Nebula Server Keycard** (`item_3`)
  - **Description**: An access card for the Nebula Ballroom's network server room.
  - **Visual**: A sleek, black plastic keycard with a magnetic stripe and a subtle 'Server Room 7' etched on its surface.
  - **Hidden**: false

### Sub-Basement Service Tunnels
- **Utility Tunnel Map** (`item_7`)
  - **Description**: A grimy, folded map detailing the labyrinthine sub-basement service tunnels.
  - **Visual**: A well-used, water-stained paper map, folded repeatedly, with handwritten annotations and arrows marking various conduits and access points.
  - **Hidden**: false

- **Obsolete Override Panel** (`item_8`)
  - **Description**: A hidden, manual control panel for the vault's auxiliary ventilation system.
  - **Visual**: A rusty, forgotten metal panel tucked behind a pipe, with a few flickering indicator lights and a dusty, unlabeled toggle switch.
  - **Hidden**: true
  - **Unlock**:
    - Task `MM1`

## NPCs

### curator - Dr. Elias Thorne
- **ID**: `curator`
- **Role**: curator
- **Location**: `sub_basement_tunnels`
- **Age**: 35
- **Gender**: person
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: neutral
- **Attitude**: casual
- **Details**: Standard appearance
- **Personality**: Knowledgeable and proud
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `curator_info_1` LOW: Information from Curator
  - `curator_info_2` MEDIUM: Information from Curator
- **Actions Available**:
  - `curator_action_1` LOW: Action performed by Curator
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### guard - Officer Miller
- **ID**: `security_guard`
- **Role**: guard
- **Location**: `cosmic_strongroom`
- **Age**: 35
- **Gender**: man
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: neutral
- **Attitude**: professional
- **Details**: Standard appearance
- **Personality**: Cautious and rule-following
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `security_guard_info_1` LOW: Information from Security Guard
- **Actions Available**:
  - `security_guard_action_1` LOW: Action performed by Security Guard
  - `security_guard_action_2` HIGH: Action performed by Security Guard
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### manager - Ms. Anya Sharma
- **ID**: `manager`
- **Role**: manager
- **Location**: `curators_private_study`
- **Age**: 35
- **Gender**: person
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: friendly
- **Attitude**: suspicious
- **Details**: Standard appearance
- **Personality**: Busy and authoritative
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `manager_info_1` MEDIUM: Information from Manager
  - `manager_info_2` HIGH: Information from Manager
- **Actions Available**:
  - `manager_action_1` MEDIUM: Action performed by Manager
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### IT - Kevin Lee
- **ID**: `it_specialist`
- **Role**: IT
- **Location**: `nebula_ballroom`
- **Age**: 35
- **Gender**: woman
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: stern
- **Attitude**: professional
- **Details**: Standard appearance
- **Personality**: Technical and distracted
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `it_specialist_info_1` MEDIUM: Information from IT Specialist
- **Actions Available**:
  - `it_specialist_action_1` LOW: Action performed by IT Specialist
  - `it_specialist_action_2` MEDIUM: Action performed by IT Specialist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

## Roles & Tasks

### Hacker

**Tasks:**

1. **H1. 🎮 fingerprint_matching** - Jam façade's external comms.
   - *Location:* `grand_facade`
   - *Prerequisites:* None (starting task)

2. **H2. 🔍 SEARCH** - Find server room access keycard.
   - *Search Items:* `item_3`
   - *Location:* `nebula_ballroom`
   - *Prerequisites:*
      - Task `MM2`
      - Task `MM1`

3. **H3. 🎮 lock_picking** - Overload main gate's power grid.
   - *Location:* `grand_facade`
   - *Prerequisites:*
      - Task `H2`

4. **H4. 🎮 alarm_disable** - Reroute tunnel surveillance feeds.
   - *Location:* `sub_basement_tunnels`
   - *Prerequisites:*
      - Task `H1`

5. **H5. 💬 NPC_LLM** - Extract vault access codes from manager.
   - *NPC:* `manager`
   - *Target Outcomes:* `manager_info_1`
   - *Location:* `curators_private_study`
   - *Prerequisites:*
      - Task `H4`


### Mastermind

**Tasks:**

1. **MM1. 🔍 SEARCH** - Locate security camera weak points.
   - *Search Items:* `item_1`, `item_2`
   - *Location:* `grand_facade`
   - *Prerequisites:* None (starting task)

2. **MM2. 🎮 wire_connecting** - Bypass ventilation system controls.
   - *Location:* `sub_basement_tunnels`
   - *Prerequisites:*
      - Task `MM1`

3. **MM3. 🎮 safe_cracking** - Disable sub-basement motion sensors.
   - *Location:* `sub_basement_tunnels`
   - *Prerequisites:*
      - Task `MM1`


