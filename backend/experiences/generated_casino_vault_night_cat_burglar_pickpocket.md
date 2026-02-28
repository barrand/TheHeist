---
---
---
---
---
---
# Infiltrate the high-roller casino, navigate its labyrinthine security, and extract the legendary 'Midnight Star' diamond from its impenetrable vault before dawn.

**ID**: `casino_vault_night`
**Scenario**: Infiltrate the high-roller casino, navigate its labyrinthine security, and extract the legendary 'Midnight Star' diamond from its impenetrable vault before dawn.
**Selected Roles**: Cat Burglar, Pickpocket
**Player Count**: 2 players

## Objective
Infiltrate the high-roller casino, navigate its labyrinthine security, and extract the legendary 'Midnight Star' diamond from its impenetrable vault before dawn.

## Locations

### Exterior
- **Neon Alley Rooftop** (`rooftop_access`): The humid night air buzzes with the distant hum of city life and the flickering glow of a hundred neon signs reflecting in grimy puddles below.

### Interior
- **Crawlspace Labyrinth** (`ventilation_shafts`): A claustrophobic maze of dust-coated metal ducts and exposed wiring, echoing with the faint whir of the casino's massive AC units.
- **Velvet Rope Lounge** (`private_game_lounge`): Opulent, deserted private game lounge, still reeking faintly of stale cigars and desperation, with plush, overturned chairs and discarded champagne flutes.
- **Hawk-Eye Hallway** (`surveillance_corridor`): A sterile, brightly lit corridor lined with an intimidating array of constantly panning security cameras and pressure plates embedded in the polished floor.
- **Prestige Vault Antechamber** (`vault_lobby`): A heavily fortified antechamber, sparse but imposing, with a reinforced steel door dominating one wall and biometric scanners glinting ominously.
- **Heart of Gold Vault** (`fortune_vault`): Shelves piled high with stacks of crisp cash, glittering rows of rare chips, and an overwhelming aura of concentrated wealth guarded by a single, priceless artifact.

**Total Locations**: 6

## Items by Location

### Heart of Gold Vault
- **The Golden Scarab** (`item_11`)
  - **Description**: Ancient artifact, solid gold, encrusted with rubies.
  - **Visual**: Intricately carved golden scarab beetle, shimmering with embedded red rubies, resting on a plush velvet cushion inside a display case.
  - **Hidden**: true
  - **Unlock**:
    - Task `CB2`

### Velvet Rope Lounge
- **RFID Skimmer** (`item_4`)
  - **Description**: Wirelessly copies card data from pockets.
  - **Visual**: Slim, credit card-sized device with a small, barely visible antenna, held subtly in a hand.
  - **Hidden**: false

- **VIP Guest List** (`item_5`)
  - **Description**: Names and room numbers of high-rollers.
  - **Visual**: Leather-bound notebook with elegant script, open to a page showing multiple names and numbers.
  - **Hidden**: true
  - **Unlock**:
    - Task `CB3`
    - Task `CB1`

### Neon Alley Rooftop
- **Grappling Hook Launcher** (`item_1`)
  - **Description**: Compact device for rapid vertical ascent.
  - **Visual**: Sleek, black, pistol-grip device with a coiled rope and a clawed hook attached, ready to fire.
  - **Hidden**: false

- **Thermal Goggles** (`item_2`)
  - **Description**: See heat signatures through smoke or darkness.
  - **Visual**: Dark, tactical goggles with a glowing red and orange thermal overlay display, ready to be worn.
  - **Hidden**: false

### Hawk-Eye Hallway
- **Security Override Dongle** (`item_6`)
  - **Description**: Temporarily disables specific camera feeds.
  - **Visual**: USB-like device with a blinking red light, attached to a short, flexible cable.
  - **Hidden**: true
  - **Unlock**:
    - Task `CB2`

- **Nano-Fiber Lockpicks** (`item_7`)
  - **Description**: Ultra-thin picks for high-security locks.
  - **Visual**: Set of extremely fine, metallic lockpicks, glinting under ambient light, held delicately.
  - **Hidden**: false

- **Stealth Smoke Pellets** (`item_8`)
  - **Description**: Creates a non-toxic, vision-obstructing cloud.
  - **Visual**: Small, dark, cylindrical pellets arranged neatly in a tactical pouch, ready for deployment.
  - **Hidden**: false

### Prestige Vault Antechamber
- **Biometric Scanner Bypass** (`item_9`)
  - **Description**: Emulates a valid fingerprint or retina scan.
  - **Visual**: Small, clear gel pad with intricate circuit patterns, next to a miniature screen displaying a fingerprint image.
  - **Hidden**: true
  - **Unlock**:
    - Task `CB2`
    - Task `PP2`

- **Sonic Drill Bit** (`item_10`)
  - **Description**: Pierces reinforced steel with minimal noise.
  - **Visual**: Specialized drill bit with a unique spiral pattern and a dull, non-reflective finish, designed for silence.
  - **Hidden**: false

### Crawlspace Labyrinth
- **Network Tap** (`item_3`)
  - **Description**: Discreet device to intercept network data.
  - **Visual**: Small, flat, black box with multiple RJ45 ports and blinking green activity lights.
  - **Hidden**: true
  - **Unlock**:
    - Task `CB2`
    - Task `PP2`

## NPCs

### manager - Arthur
- **ID**: `manager`
- **Role**: manager
- **Location**: `surveillance_corridor`
- **Age**: 35
- **Gender**: person
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: stern
- **Attitude**: suspicious
- **Details**: Standard appearance
- **Personality**: Busy and authoritative
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `manager_info_1` MEDIUM: Information from Manager
- **Actions Available**:
  - `manager_action_1` HIGH: Action performed by Manager
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### IT - Kevin
- **ID**: `it_specialist`
- **Role**: IT
- **Location**: `ventilation_shafts`
- **Age**: 35
- **Gender**: woman
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: friendly
- **Attitude**: suspicious
- **Details**: Standard appearance
- **Personality**: Technical and distracted
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `it_specialist_info_1` MEDIUM: Information from IT Specialist
  - `it_specialist_info_2` MEDIUM: Information from IT Specialist
- **Actions Available**:
  - `it_specialist_action_1` HIGH: Action performed by IT Specialist
  - `it_specialist_action_2` LOW: Action performed by IT Specialist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

## Roles & Tasks

### Cat Burglar

**Tasks:**

1. **CB1. 🔍 SEARCH** - Locate hidden security override in hallway.
   - *Search Items:* `item_8`, `item_7`
   - *Location:* `surveillance_corridor`
   - *Prerequisites:* None (starting task)

2. **CB2. 🔍 SEARCH** - Find vital equipment on the rooftop.
   - *Search Items:* `item_2`
   - *Location:* `rooftop_access`
   - *Prerequisites:*
      - Task `CB1`

3. **CB3. 🎮 lock_picking** - Navigate crawlspace, avoid motion sensors.
   - *Location:* `ventilation_shafts`
   - *Prerequisites:*
      - Task `CB1`


### Pickpocket

**Tasks:**

1. **PP1. 🎮 safe_cracking** - Disable vault antechamber laser grid.
   - *Location:* `vault_lobby`
   - *Prerequisites:* None (starting task)

2. **PP2. 🎮 fingerprint_matching** - Reroute surveillance feeds in crawlspace.
   - *Location:* `ventilation_shafts`
   - *Prerequisites:*
      - Task `CB1`
      - Task `CB2`

3. **PP3. 💬 NPC_LLM** - Distract IT specialist for network access.
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_1`
   - *Location:* `ventilation_shafts`
   - *Prerequisites:*
      - Task `PP1`

4. **PP4. 🎮 wire_connecting** - Bypass biometric scanner at vault door.
   - *Location:* `vault_lobby`
   - *Prerequisites:*
      - Task `CB2`

5. **PP5. 🎮 wire_connecting** - Extract VIP list from lounge manager.
   - *Location:* `private_game_lounge`
   - *Prerequisites:*
      - Task `CB1`
      - Task `PP3`


