---
---
---
---
---
---
# Steal the priceless artifact from the museum vault

**ID**: `museum_heist`
**Scenario**: Steal the priceless artifact from the museum vault
**Selected Roles**: Hacker, Mastermind, Safe Cracker
**Player Count**: 3 players

## Objective
Steal the priceless artifact from the museum vault

## Locations

### Museum Exterior
- **Loading Dock** (`loading_dock`): Service entrance
- **Rooftop Access** (`rooftop`): Rooftop entrance point

### Museum Interior
- **Storage Room** (`storage_room`): Back storage area
- **Entrance Hall** (`entrance_hall`): Grand entrance with security
- **Security Office** (`security_office`): Security monitoring room
- **Exhibit Floor** (`exhibit_floor`): Main gallery with displays
- **Vault Chamber** (`vault_chamber`): Secure vault room

**Total Locations**: 7

## Items by Location

### Entrance Hall
- **Item 4** (`item_4`)
  - **Description**: A useful item found at Entrance Hall
  - **Visual**: generic item 4
  - **Hidden**: false

### Exhibit Floor
- **Item 8** (`item_8`)
  - **Description**: A useful item found at Exhibit Floor
  - **Visual**: generic item 8
  - **Hidden**: true
  - **Unlock**:
    - Task `SC4`

- **Item 9** (`item_9`)
  - **Description**: A useful item found at Exhibit Floor
  - **Visual**: generic item 9
  - **Hidden**: true
  - **Unlock**:
    - Task `H1`

- **Item 10** (`item_10`)
  - **Description**: A useful item found at Exhibit Floor
  - **Visual**: generic item 10
  - **Hidden**: false

### Loading Dock
- **Item 2** (`item_2`)
  - **Description**: A useful item found at Loading Dock
  - **Visual**: generic item 2
  - **Hidden**: false

- **Item 3** (`item_3`)
  - **Description**: A useful item found at Loading Dock
  - **Visual**: generic item 3
  - **Hidden**: true
  - **Unlock**:
    - Task `MM5`
    - Task `H3`

### Rooftop Access
- **Item 11** (`item_11`)
  - **Description**: A useful item found at Rooftop Access
  - **Visual**: generic item 11
  - **Hidden**: false

### Security Office
- **Item 5** (`item_5`)
  - **Description**: A useful item found at Security Office
  - **Visual**: generic item 5
  - **Hidden**: false

- **Item 6** (`item_6`)
  - **Description**: A useful item found at Security Office
  - **Visual**: generic item 6
  - **Hidden**: false

- **Item 7** (`item_7`)
  - **Description**: A useful item found at Security Office
  - **Visual**: generic item 7
  - **Hidden**: false

### Storage Room
- **Item 1** (`item_1`)
  - **Description**: A useful item found at Storage Room
  - **Visual**: generic item 1
  - **Hidden**: true
  - **Unlock**:
    - Task `H5`
    - Task `MM6`

### Vault Chamber
- **Item 12** (`item_12`)
  - **Description**: A useful item found at Vault Chamber
  - **Visual**: generic item 12
  - **Hidden**: false

- **Item 13** (`item_13`)
  - **Description**: A useful item found at Vault Chamber
  - **Visual**: generic item 13
  - **Hidden**: true
  - **Unlock**:
    - Task `SC3`

## NPCs

### IT - IT Specialist
- **ID**: `it_specialist`
- **Role**: IT
- **Location**: `vault_chamber`
- **Age**: 35
- **Gender**: person
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: friendly
- **Attitude**: casual
- **Details**: Standard appearance
- **Personality**: Technical and distracted
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `it_specialist_info_1` HIGH: Information from IT Specialist
  - `it_specialist_info_2` LOW: Information from IT Specialist
- **Actions Available**:
  - `it_specialist_action_1` HIGH: Action performed by IT Specialist
  - `it_specialist_action_2` HIGH: Action performed by IT Specialist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### maintenance - Janitor
- **ID**: `janitor`
- **Role**: maintenance
- **Location**: `storage_room`
- **Age**: 35
- **Gender**: woman
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: neutral
- **Attitude**: suspicious
- **Details**: Standard appearance
- **Personality**: Friendly but observant
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `janitor_info_1` LOW: Information from Janitor
  - `janitor_info_2` LOW: Information from Janitor
- **Actions Available**:
  - `janitor_action_1` LOW: Action performed by Janitor
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

## Roles & Tasks

### Hacker

**Tasks:**

1. **H1. 🔍 SEARCH** - Search for items at Rooftop Access
   - *Search Items:* `item_11`
   - *Location:* `rooftop`
   - *Prerequisites:* None (starting task)

2. **H2. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_action_2`
   - *Location:* `vault_chamber`
   - *Prerequisites:*
      - Task `MM2`
      - Task `H1`

3. **H3. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `storage_room`
   - *Prerequisites:*
      - Task `H1`

4. **H4. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `storage_room`
   - *Prerequisites:*
      - Task `H2`
      - Task `MM6`

5. **H5. 💬 NPC_LLM** - Talk to Janitor
   - *NPC:* `janitor`
   - *Target Outcomes:* `janitor_action_1`, `janitor_info_1`
   - *Location:* `storage_room`
   - *Prerequisites:*
      - Task `MM1`
      - Task `MM5`


### Mastermind

**Tasks:**

1. **MM1. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `vault_chamber`
   - *Prerequisites:* None (starting task)

2. **MM2. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `exhibit_floor`
   - *Prerequisites:*
      - Task `MM1`

3. **MM3. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `vault_chamber`
   - *Prerequisites:*
      - Task `MM2`
      - Task `MM1`

4. **MM4. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `security_office`
   - *Prerequisites:*
      - Task `MM1`

5. **MM5. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `entrance_hall`
   - *Prerequisites:*
      - Task `MM3`

6. **MM6. 🎮 lock_picking** - Complete camera bypass
   - *Location:* `loading_dock`
   - *Prerequisites:*
      - Task `MM5`


### Safe Cracker

**Tasks:**

1. **SC1. 🔍 SEARCH** - Search for items at Entrance Hall
   - *Search Items:* `item_4`
   - *Location:* `entrance_hall`
   - *Prerequisites:* None (starting task)

2. **SC2. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `loading_dock`
   - *Prerequisites:*
      - Task `H2`
      - Task `MM4`

3. **SC3. 🔍 SEARCH** - Search Loading Dock
   - *Search Items:* `item_3`
   - *Location:* `loading_dock`
   - *Prerequisites:*
      - Task `H4`

4. **SC4. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_action_1`, `it_specialist_info_1`
   - *Location:* `vault_chamber`
   - *Prerequisites:*
      - Task `MM6`
      - Task `H4`


