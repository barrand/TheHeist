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

### Bank Exterior
- **Parking Garage** (`parking_garage`): Underground parking

### Bank Interior
- **Server Room** (`server_room`): IT infrastructure
- **Vault** (`vault`): Main vault
- **Manager Office** (`manager_office`): Bank manager workspace
- **Bank Lobby** (`lobby`): Main customer area
- **Teller Area** (`teller_area`): Transaction stations

**Total Locations**: 6

## Items by Location

### Bank Lobby
- **Item 6** (`item_6`)
  - **Description**: A useful item found at Bank Lobby
  - **Visual**: generic item 6
  - **Hidden**: false

- **Item 7** (`item_7`)
  - **Description**: A useful item found at Bank Lobby
  - **Visual**: generic item 7
  - **Hidden**: false

- **Item 8** (`item_8`)
  - **Description**: A useful item found at Bank Lobby
  - **Visual**: generic item 8
  - **Hidden**: false

### Manager Office
- **Item 4** (`item_4`)
  - **Description**: A useful item found at Manager Office
  - **Visual**: generic item 4
  - **Hidden**: false

- **Item 5** (`item_5`)
  - **Description**: A useful item found at Manager Office
  - **Visual**: generic item 5
  - **Hidden**: false

### Parking Garage
- **Item 1** (`item_1`)
  - **Description**: A useful item found at Parking Garage
  - **Visual**: generic item 1
  - **Hidden**: false

### Server Room
- **Item 2** (`item_2`)
  - **Description**: A useful item found at Server Room
  - **Visual**: generic item 2
  - **Hidden**: false

### Teller Area
- **Item 9** (`item_9`)
  - **Description**: A useful item found at Teller Area
  - **Visual**: generic item 9
  - **Hidden**: true
  - **Unlock**:
    - Task `SC4`

- **Item 10** (`item_10`)
  - **Description**: A useful item found at Teller Area
  - **Visual**: generic item 10
  - **Hidden**: false

- **Item 11** (`item_11`)
  - **Description**: A useful item found at Teller Area
  - **Visual**: generic item 11
  - **Hidden**: false

### Vault
- **Item 3** (`item_3`)
  - **Description**: A useful item found at Vault
  - **Visual**: generic item 3
  - **Hidden**: true
  - **Unlock**:
    - Task `H6`

## NPCs

### maintenance - Janitor
- **ID**: `janitor`
- **Role**: maintenance
- **Location**: `parking_garage`
- **Age**: 35
- **Gender**: man
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: friendly
- **Attitude**: professional
- **Details**: Standard appearance
- **Personality**: Friendly but observant
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `janitor_info_1` MEDIUM: Information from Janitor
- **Actions Available**:
  - `janitor_action_1` MEDIUM: Action performed by Janitor
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
- **Attitude**: professional
- **Details**: Standard appearance
- **Personality**: Technical and distracted
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `it_specialist_info_1` HIGH: Information from IT Specialist
- **Actions Available**:
  - `it_specialist_action_1` HIGH: Action performed by IT Specialist
  - `it_specialist_action_2` MEDIUM: Action performed by IT Specialist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### receptionist - Receptionist
- **ID**: `receptionist`
- **Role**: receptionist
- **Location**: `parking_garage`
- **Age**: 35
- **Gender**: person
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: neutral
- **Attitude**: casual
- **Details**: Standard appearance
- **Personality**: Professional and helpful
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `receptionist_info_1` MEDIUM: Information from Receptionist
  - `receptionist_info_2` HIGH: Information from Receptionist
- **Actions Available**:
  - `receptionist_action_1` LOW: Action performed by Receptionist
  - `receptionist_action_2` HIGH: Action performed by Receptionist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

## Roles & Tasks

### Driver

**Tasks:**

1. **D1. 🔍 SEARCH** - Search for items at Parking Garage
   - *Search Items:* `item_1`
   - *Location:* `parking_garage`
   - *Prerequisites:* None (starting task)

2. **D2. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `parking_garage`
   - *Prerequisites:*
      - Task `D1`

3. **D3. 🎮 alarm_disable** - Complete alarm disable
   - *Location:* `manager_office`
   - *Prerequisites:*
      - Task `SC3`
      - Task `H4`

4. **D4. 🔍 SEARCH** - Search Vault
   - *Search Items:* `item_3`
   - *Location:* `vault`
   - *Prerequisites:*
      - Task `SC2`

5. **D5. 🎮 alarm_disable** - Complete alarm disable
   - *Location:* `lobby`
   - *Prerequisites:*
      - Task `H6`

6. **D6. 🗣️ INFO_SHARE** - Share information with team
   - *Info:* Information about it_specialist_action_2
   - *Location:* `parking_garage`
   - *Prerequisites:*
      - Task `SC2`
      - Task `SC5`


### Hacker

**Tasks:**

1. **H1. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `lobby`
   - *Prerequisites:* None (starting task)

2. **H2. 💬 NPC_LLM** - Talk to Receptionist
   - *NPC:* `receptionist`
   - *Target Outcomes:* `receptionist_info_2`
   - *Location:* `parking_garage`
   - *Prerequisites:*
      - Task `H1`

3. **H3. 🎮 wire_connecting** - Complete safe cracking
   - *Location:* `manager_office`
   - *Prerequisites:*
      - Task `H2`

4. **H4. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `teller_area`
   - *Prerequisites:*
      - Task `H3`

5. **H5. 🎮 camera_bypass** - Complete camera bypass
   - *Location:* `vault`
   - *Prerequisites:*
      - Task `H4`
      - Task `H1`

6. **H6. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_action_1`
   - *Location:* `lobby`
   - *Prerequisites:*
      - Task `H3`


### Safe Cracker

**Tasks:**

1. **SC1. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `vault`
   - *Prerequisites:* None (starting task)

2. **SC2. 🎮 alarm_disable** - Complete alarm disable
   - *Location:* `server_room`
   - *Prerequisites:*
      - Task `H4`

3. **SC3. 💬 NPC_LLM** - Talk to Janitor
   - *NPC:* `janitor`
   - *Target Outcomes:* `janitor_info_1`, `janitor_action_1`
   - *Location:* `parking_garage`
   - *Prerequisites:*
      - Task `H1`

4. **SC4. 🗣️ INFO_SHARE** - Share information with team
   - *Info:* Information about janitor_action_1
   - *Location:* `lobby`
   - *Prerequisites:*
      - Task `H2`
      - Task `H5`

5. **SC5. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_action_2`
   - *Location:* `lobby`
   - *Prerequisites:*
      - Task `SC2`
      - Task `SC4`


