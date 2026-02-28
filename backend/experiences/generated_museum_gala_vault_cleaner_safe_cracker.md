---
---
---
---
---
---
# Infiltrate the prestigious 'Museum of Antiquities' during its annual gala to steal the legendary 'Serpent's Eye' diamond from the impenetrable Obsidian Vault.

**ID**: `museum_gala_vault`
**Scenario**: Infiltrate the prestigious 'Museum of Antiquities' during its annual gala to steal the legendary 'Serpent's Eye' diamond from the impenetrable Obsidian Vault.
**Selected Roles**: Cleaner, Safe Cracker
**Player Count**: 2 players

## Objective
Infiltrate the prestigious 'Museum of Antiquities' during its annual gala to steal the legendary 'Serpent's Eye' diamond from the impenetrable Obsidian Vault.

## Locations

### Exterior
- **The Velvet Gauntlet** (`gala_red_carpet`): A dazzling gauntlet of paparazzi flashes and velvet ropes guards the opulent entrance, leading into the glittering main hall where elite guests arrive.

### Interior
- **The Celestial Rotunda** (`celestial_rotunda`): Beneath a massive, ornate dome depicting constellations, hundreds of masked guests mingle, their whispers echoing softly in the vast, marble-floored space.
- **The Whispering Exhibits** (`curator_private_gallery`): Dimly lit corridors lined with ancient, priceless artifacts lead away from the main gala, less frequented by revelers but rich in history.
- **The Eye of Argus** (`security_hub`): A sterile, modern security control room where vigilant guards monitor dozens of screens displaying every angle of the museum's interior and exterior.
- **The Obsidian Gateway** (`vault_antechamber`): A fortified antechamber, sparse and cold, precedes the vault door, its thick, reinforced steel glowing faintly under emergency lights.
- **The Serpent's Heart** (`serpents_heart_vault`): Inside the vault, the air is still and heavy, with the legendary Serpent's Eye diamond gleaming ominously on a central, laser-guarded pedestal.

**Total Locations**: 6

## Items by Location

### The Celestial Rotunda
- **Star-Chart Cipher** (`item_4`)
  - **Description**: An ancient parchment depicting constellations, with cryptic notations.
  - **Visual**: A brittle, rolled-up parchment scroll, yellowed with age, covered in hand-drawn star charts and faint, swirling script, hidden behind a loose stone in a display pedestal.
  - **Hidden**: true
  - **Unlock**:
    - Task `SC1`

- **Astral Compass** (`item_5`)
  - **Description**: A small, intricate device used for celestial navigation.
  - **Visual**: A palm-sized antique brass compass, its glass cover slightly fogged, with tiny, detailed planetary engravings on its casing, tucked inside a velvet-lined drawer beneath a telescope display.
  - **Hidden**: true
  - **Unlock**:
    - Task `CL4`
    - Task `SC3`

### The Whispering Exhibits
- **The Silent Bell** (`item_6`)
  - **Description**: A small, tarnished bell rumored to open secret passages.
  - **Visual**: A diminutive, bronze hand-bell, verdigris covering its surface, with a worn leather handle, concealed within a dusty, forgotten display case of ancient artifacts.
  - **Hidden**: true
  - **Unlock**:
    - Task `SC5`
    - Task `SC1`

### The Velvet Gauntlet
- **The Curator's Hidden Key** (`item_1`)
  - **Description**: A master key, discreetly tucked away for emergencies.
  - **Visual**: An ornate, antique brass key, dull with age, hanging on a small, almost invisible hook behind a heavy velvet curtain.
  - **Hidden**: true
  - **Unlock**:
    - Task `SC6`
    - Task `SC1`

- **The Gala Guest List** (`item_2`)
  - **Description**: The official list of attendees, detailing their names and VIP status.
  - **Visual**: A thick, leather-bound guest book with gold-embossed lettering, open on a polished mahogany podium, a silver pen resting beside it.
  - **Hidden**: false

- **Security Monitor Log** (`item_3`)
  - **Description**: A digital tablet displaying the current security camera feeds.
  - **Visual**: A sleek, modern tablet screen glowing faintly, showing multiple monochrome camera views of the museum's entrance and hallways, resting on a small, unobtrusive table near a reception desk.
  - **Hidden**: false

### The Eye of Argus
- **Argus's Gaze Camera** (`item_7`)
  - **Description**: A high-resolution security camera, centrally positioned.
  - **Visual**: A modern, sleek black dome camera mounted prominently on the ceiling, with a single red light indicating it's active, surveying a wide exhibition hall.
  - **Hidden**: false

- **The Sapphire Sentinel** (`item_8`)
  - **Description**: A large sapphire crystal, the centerpiece of the security system.
  - **Visual**: A massive, uncut sapphire gem, glowing with an internal blue light, encased in a reinforced glass pedestal, surrounded by laser grids.
  - **Hidden**: false

### The Serpent's Heart
- **The Serpent's Eye Diamond** (`item_12`)
  - **Description**: The legendary, priceless diamond kept deep within the vault.
  - **Visual**: A colossal, perfectly cut diamond, shimmering with an ethereal green light, resting on a black velvet cushion inside a reinforced, bulletproof glass display case within a high-security vault.
  - **Hidden**: false

### The Obsidian Gateway
- **Guardian Stone Tablet** (`item_9`)
  - **Description**: An ancient stone tablet depicting mythical guardians.
  - **Visual**: A heavy, dark grey stone tablet, intricately carved with figures of winged beasts and ancient script, mounted on a wall near a grand archway.
  - **Hidden**: false

- **Ceremonial Torch Sconce** (`item_10`)
  - **Description**: An elaborate iron sconce, once holding a perpetual flame.
  - **Visual**: A large, wrought-iron torch sconce, designed with intertwining serpent motifs, fixed to a column beside a grand entrance, soot stains visible around its opening.
  - **Hidden**: false

- **The Unseen Pressure Plate** (`item_11`)
  - **Description**: A subtle floor panel triggering an alarm if stepped on.
  - **Visual**: A section of the polished stone floor, indistinguishable from its surroundings, with faint, almost imperceptible lines indicating a hidden pressure plate, located in a narrow corridor.
  - **Hidden**: false

## NPCs

### maintenance - Bartholomew
- **ID**: `janitor`
- **Role**: maintenance
- **Location**: `vault_antechamber`
- **Age**: 35
- **Gender**: person
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: neutral
- **Attitude**: professional
- **Details**: Standard appearance
- **Personality**: Friendly but observant
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `janitor_info_1` MEDIUM: Information from Janitor
- **Actions Available**:
  - `janitor_action_1` MEDIUM: Action performed by Janitor
  - `janitor_action_2` HIGH: Action performed by Janitor
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### IT - Penelope
- **ID**: `it_specialist`
- **Role**: IT
- **Location**: `gala_red_carpet`
- **Age**: 35
- **Gender**: man
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: friendly
- **Attitude**: casual
- **Details**: Standard appearance
- **Personality**: Technical and distracted
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `it_specialist_info_1` LOW: Information from IT Specialist
- **Actions Available**:
  - `it_specialist_action_1` HIGH: Action performed by IT Specialist
  - `it_specialist_action_2` LOW: Action performed by IT Specialist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### manager - Eleanor
- **ID**: `manager`
- **Role**: manager
- **Location**: `serpents_heart_vault`
- **Age**: 35
- **Gender**: person
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: stern
- **Attitude**: casual
- **Details**: Standard appearance
- **Personality**: Busy and authoritative
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `manager_info_1` MEDIUM: Information from Manager
  - `manager_info_2` MEDIUM: Information from Manager
- **Actions Available**:
  - `manager_action_1` HIGH: Action performed by Manager
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

## Roles & Tasks

### Cleaner

**Tasks:**

1. **CL1. 🎮 alarm_disable** - Polish celestial display, avoid laser grids.
   - *Location:* `celestial_rotunda`
   - *Prerequisites:* None (starting task)

2. **CL2. 💬 NPC_LLM** - Distract manager, secure vault access.
   - *NPC:* `manager`
   - *Target Outcomes:* `manager_info_1`
   - *Location:* `serpents_heart_vault`
   - *Prerequisites:*
      - Task `CL1`

3. **CL3. 💬 NPC_LLM** - Obtain manager's keycard, disable surveillance.
   - *NPC:* `manager`
   - *Target Outcomes:* `manager_info_1`
   - *Location:* `serpents_heart_vault`
   - *Prerequisites:*
      - Task `CL2`
      - Task `CL1`

4. **CL4. 💬 NPC_LLM** - Get janitor's override code, unlock service panel.
   - *NPC:* `janitor`
   - *Target Outcomes:* `janitor_info_1`
   - *Location:* `vault_antechamber`
   - *Prerequisites:*
      - Task `CL1`

5. **CL5. 💬 NPC_LLM** - Swap maintenance cart, block security cameras.
   - *NPC:* `janitor`
   - *Target Outcomes:* `janitor_info_1`
   - *Location:* `vault_antechamber`
   - *Prerequisites:*
      - Task `CL3`


### Safe Cracker

**Tasks:**

1. **SC1. 🎮 safe_cracking** - Decipher ancient star-chart, reveal hidden mechanism.
   - *Location:* `celestial_rotunda`
   - *Prerequisites:* None (starting task)

2. **SC2. 🔍 SEARCH** - Locate hidden panel, retrieve security schematics.
   - *Search Items:* `item_4`
   - *Location:* `celestial_rotunda`
   - *Prerequisites:*
      - Task `CL5`

3. **SC3. 💬 NPC_LLM** - Convince IT specialist, access server room.
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_1`
   - *Location:* `gala_red_carpet`
   - *Prerequisites:*
      - Task `CL1`

4. **SC4. 🎮 fingerprint_matching** - Bypass vault lock, secure the diamond.
   - *Location:* `serpents_heart_vault`
   - *Prerequisites:*
      - Task `CL4`

5. **SC5. 🎮 safe_cracking** - Disable pressure plate, avoid floor alarm.
   - *Location:* `celestial_rotunda`
   - *Prerequisites:*
      - Task `CL3`
      - Task `CL5`

6. **SC6. 🎮 alarm_disable** - Reroute surveillance feed, create blind spot.
   - *Location:* `celestial_rotunda`
   - *Prerequisites:*
      - Task `CL4`
      - Task `SC5`


