---
---
---
---
---
---
# Infiltrate the bank and access the vault

**ID**: `bank_vault`
**Scenario**: Infiltrate the bank and access the vault
**Selected Roles**: Driver, Hacker, Safe Cracker
**Player Count**: 3 players

## Objective
Infiltrate the bank and access the vault

## Locations

### Bank Interior
- **Teller Area** (`teller_area`): Transaction stations
- **Server Room** (`server_room`): IT infrastructure
- **Vault** (`vault`): Main vault
- **Bank Lobby** (`lobby`): Main customer area
- **Manager Office** (`manager_office`): Bank manager workspace

**Total Locations**: 5

## Items by Location

### Bank Lobby
- **Item 7** (`item_7`)
  - **Description**: A useful item found at Bank Lobby
  - **Visual**: generic item 7
  - **Hidden**: true
  - **Unlock**:
    - Task `H3`
    - Task `D3`

- **Item 8** (`item_8`)
  - **Description**: A useful item found at Bank Lobby
  - **Visual**: generic item 8
  - **Hidden**: false

### Manager Office
- **Item 9** (`item_9`)
  - **Description**: A useful item found at Manager Office
  - **Visual**: generic item 9
  - **Hidden**: false

- **Item 10** (`item_10`)
  - **Description**: A useful item found at Manager Office
  - **Visual**: generic item 10
  - **Hidden**: false

### Server Room
- **Item 4** (`item_4`)
  - **Description**: A useful item found at Server Room
  - **Visual**: generic item 4
  - **Hidden**: true
  - **Unlock**:
    - Task `SC1`

### Teller Area
- **Item 1** (`item_1`)
  - **Description**: A useful item found at Teller Area
  - **Visual**: generic item 1
  - **Hidden**: false

- **Item 2** (`item_2`)
  - **Description**: A useful item found at Teller Area
  - **Visual**: generic item 2
  - **Hidden**: true
  - **Unlock**:
    - Task `D5`

- **Item 3** (`item_3`)
  - **Description**: A useful item found at Teller Area
  - **Visual**: generic item 3
  - **Hidden**: false

### Vault
- **Item 5** (`item_5`)
  - **Description**: A useful item found at Vault
  - **Visual**: generic item 5
  - **Hidden**: false

- **Item 6** (`item_6`)
  - **Description**: A useful item found at Vault
  - **Visual**: generic item 6
  - **Hidden**: true
  - **Unlock**:
    - Task `SC1`
    - Task `D3`

## NPCs

### curator - Curator
- **ID**: `curator`
- **Role**: curator
- **Location**: `manager_office`
- **Age**: 35
- **Gender**: woman
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: stern
- **Attitude**: casual
- **Details**: Standard appearance
- **Personality**: Knowledgeable and proud
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `curator_info_1` HIGH: Information from Curator
  - `curator_info_2` HIGH: Information from Curator
- **Actions Available**:
  - `curator_action_1` MEDIUM: Action performed by Curator
  - `curator_action_2` LOW: Action performed by Curator
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### IT - IT Specialist
- **ID**: `it_specialist`
- **Role**: IT
- **Location**: `lobby`
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
  - `it_specialist_action_2` MEDIUM: Action performed by IT Specialist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

## Roles & Tasks

### Driver

**Tasks:**

1. **D1. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `lobby`
   - *Prerequisites:* None (starting task)

2. **D2. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_1`
   - *Location:* `lobby`
   - *Prerequisites:*
      - Task `H2`

3. **D3. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `manager_office`
   - *Prerequisites:*
      - Task `SC3`
      - Task `H2`

4. **D4. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `vault`
   - *Prerequisites:*
      - Task `D1`

5. **D5. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `lobby`
   - *Prerequisites:*
      - Task `H1`

6. **D6. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `server_room`
   - *Prerequisites:*
      - Task `H2`


### Hacker

**Tasks:**

1. **H1. 🎮 alarm_disable** - Complete alarm disable
   - *Location:* `teller_area`
   - *Prerequisites:* None (starting task)

2. **H2. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `teller_area`
   - *Prerequisites:*
      - Task `H1`

3. **H3. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `server_room`
   - *Prerequisites:*
      - Task `H2`
      - Task `H1`


### Safe Cracker

**Tasks:**

1. **SC1. 🎮 camera_bypass** - Complete camera bypass
   - *Location:* `server_room`
   - *Prerequisites:* None (starting task)

2. **SC2. 🎮 camera_bypass** - Complete camera bypass
   - *Location:* `teller_area`
   - *Prerequisites:*
      - Task `SC1`

3. **SC3. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `teller_area`
   - *Prerequisites:*
      - Task `H3`
      - Task `SC2`


