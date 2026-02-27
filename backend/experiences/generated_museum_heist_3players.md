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
- **Rooftop Access** (`rooftop`): Rooftop entrance point
- **Loading Dock** (`loading_dock`): Service entrance

### Museum Interior
- **Exhibit Floor** (`exhibit_floor`): Main gallery with displays
- **Entrance Hall** (`entrance_hall`): Grand entrance with security

**Total Locations**: 4

## Items by Location

### Entrance Hall
- **Item 9** (`item_9`)
  - **Description**: A useful item found at Entrance Hall
  - **Visual**: generic item 9
  - **Hidden**: true
  - **Unlock**:
    - Task `H5`

- **Item 10** (`item_10`)
  - **Description**: A useful item found at Entrance Hall
  - **Visual**: generic item 10
  - **Hidden**: false

- **Item 11** (`item_11`)
  - **Description**: A useful item found at Entrance Hall
  - **Visual**: generic item 11
  - **Hidden**: false

### Exhibit Floor
- **Item 1** (`item_1`)
  - **Description**: A useful item found at Exhibit Floor
  - **Visual**: generic item 1
  - **Hidden**: false

- **Item 2** (`item_2`)
  - **Description**: A useful item found at Exhibit Floor
  - **Visual**: generic item 2
  - **Hidden**: true
  - **Unlock**:
    - Task `H4`
    - Task `H2`

- **Item 3** (`item_3`)
  - **Description**: A useful item found at Exhibit Floor
  - **Visual**: generic item 3
  - **Hidden**: false

### Loading Dock
- **Item 6** (`item_6`)
  - **Description**: A useful item found at Loading Dock
  - **Visual**: generic item 6
  - **Hidden**: false

- **Item 7** (`item_7`)
  - **Description**: A useful item found at Loading Dock
  - **Visual**: generic item 7
  - **Hidden**: true
  - **Unlock**:
    - Task `H2`

- **Item 8** (`item_8`)
  - **Description**: A useful item found at Loading Dock
  - **Visual**: generic item 8
  - **Hidden**: false

### Rooftop Access
- **Item 4** (`item_4`)
  - **Description**: A useful item found at Rooftop Access
  - **Visual**: generic item 4
  - **Hidden**: true
  - **Unlock**:
    - Task `SC1`
    - Task `MM5`

- **Item 5** (`item_5`)
  - **Description**: A useful item found at Rooftop Access
  - **Visual**: generic item 5
  - **Hidden**: false

## NPCs

### receptionist - Receptionist
- **ID**: `receptionist`
- **Role**: receptionist
- **Location**: `exhibit_floor`
- **Age**: 35
- **Gender**: woman
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: neutral
- **Attitude**: professional
- **Details**: Standard appearance
- **Personality**: Professional and helpful
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `receptionist_info_1` LOW: Information from Receptionist
  - `receptionist_info_2` HIGH: Information from Receptionist
- **Actions Available**:
  - `receptionist_action_1` HIGH: Action performed by Receptionist
  - `receptionist_action_2` HIGH: Action performed by Receptionist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### curator - Curator
- **ID**: `curator`
- **Role**: curator
- **Location**: `rooftop`
- **Age**: 35
- **Gender**: person
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: stern
- **Attitude**: suspicious
- **Details**: Standard appearance
- **Personality**: Knowledgeable and proud
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `curator_info_1` LOW: Information from Curator
  - `curator_info_2` HIGH: Information from Curator
- **Actions Available**:
  - `curator_action_1` LOW: Action performed by Curator
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

## Roles & Tasks

### Hacker

**Tasks:**

1. **H1. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `rooftop`
   - *Prerequisites:* None (starting task)

2. **H2. 🎮 camera_bypass** - Complete camera bypass
   - *Location:* `exhibit_floor`
   - *Prerequisites:*
      - Task `H1`

3. **H3. 💬 NPC_LLM** - Talk to Receptionist
   - *NPC:* `receptionist`
   - *Target Outcomes:* `receptionist_info_1`, `receptionist_info_2`
   - *Location:* `exhibit_floor`
   - *Prerequisites:*
      - Task `H1`
      - Task `MM5`

4. **H4. 🔍 SEARCH** - Search Rooftop Access
   - *Search Items:* `item_5`
   - *Location:* `rooftop`
   - *Prerequisites:*
      - Outcome `receptionist_info_1`

5. **H5. 💬 NPC_LLM** - Talk to Curator
   - *NPC:* `curator`
   - *Target Outcomes:* `curator_action_1`, `curator_info_2`
   - *Location:* `rooftop`
   - *Prerequisites:*
      - Task `MM3`


### Mastermind

**Tasks:**

1. **MM1. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `exhibit_floor`
   - *Prerequisites:* None (starting task)

2. **MM2. 🔍 SEARCH** - Search Loading Dock
   - *Search Items:* `item_8`
   - *Location:* `loading_dock`
   - *Prerequisites:*
      - Task `MM1`

3. **MM3. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `rooftop`
   - *Prerequisites:*
      - Task `MM1`

4. **MM4. 🎮 camera_bypass** - Complete camera bypass
   - *Location:* `entrance_hall`
   - *Prerequisites:*
      - Task `MM2`

5. **MM5. 💬 NPC_LLM** - Talk to Curator
   - *NPC:* `curator`
   - *Target Outcomes:* `curator_info_1`
   - *Location:* `rooftop`
   - *Prerequisites:*
      - Task `MM1`


### Safe Cracker

**Tasks:**

1. **SC1. 🎮 alarm_disable** - Complete alarm disable
   - *Location:* `entrance_hall`
   - *Prerequisites:* None (starting task)

2. **SC2. 💬 NPC_LLM** - Talk to Receptionist
   - *NPC:* `receptionist`
   - *Target Outcomes:* `receptionist_action_2`
   - *Location:* `exhibit_floor`
   - *Prerequisites:*
      - Outcome `curator_info_2`
      - Task `H4`

3. **SC3. 🎮 camera_bypass** - Complete camera bypass
   - *Location:* `rooftop`
   - *Prerequisites:*
      - Outcome `curator_action_1`
      - Outcome `receptionist_info_1`

4. **SC4. 💬 NPC_LLM** - Talk to Curator
   - *NPC:* `curator`
   - *Target Outcomes:* `curator_action_1`, `curator_info_2`
   - *Location:* `rooftop`
   - *Prerequisites:*
      - Task `SC1`

5. **SC5. 💬 NPC_LLM** - Talk to Receptionist
   - *NPC:* `receptionist`
   - *Target Outcomes:* `receptionist_info_2`, `receptionist_action_2`
   - *Location:* `exhibit_floor`
   - *Prerequisites:*
      - Outcome `receptionist_info_2`
      - Task `H4`


