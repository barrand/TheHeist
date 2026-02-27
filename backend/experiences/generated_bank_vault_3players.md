---
# Infiltrate the bank and access the vault

**ID**: `bank_vault`
**Scenario**: Infiltrate the bank and access the vault
**Selected Roles**: Driver, Mastermind, Safe Cracker
**Player Count**: 3 players

## Objective
Infiltrate the bank and access the vault

## Locations

### Bank Exterior
- **Parking Garage** (`parking_garage`): Underground parking

### Bank Interior
- **Server Room** (`server_room`): IT infrastructure
- **Bank Lobby** (`lobby`): Main customer area
- **Vault** (`vault`): Main vault
- **Manager Office** (`manager_office`): Bank manager workspace
- **Teller Area** (`teller_area`): Transaction stations

**Total Locations**: 6

## Items by Location

### Bank Lobby
- **ID**: `item_3`
  - **Name**: Item 3
  - **Description**: A useful item found at Bank Lobby
  - **Visual**: generic item 3
  - **Hidden**: false

- **ID**: `item_4`
  - **Name**: Item 4
  - **Description**: A useful item found at Bank Lobby
  - **Visual**: generic item 4
  - **Hidden**: false

- **ID**: `item_5`
  - **Name**: Item 5
  - **Description**: A useful item found at Bank Lobby
  - **Visual**: generic item 5
  - **Hidden**: true
  - **Unlock**:
    - Task `D6`

### Manager Office
- **ID**: `item_9`
  - **Name**: Item 9
  - **Description**: A useful item found at Manager Office
  - **Visual**: generic item 9
  - **Hidden**: true
  - **Unlock**:
    - Task `D5`
    - Task `SC2`

- **ID**: `item_10`
  - **Name**: Item 10
  - **Description**: A useful item found at Manager Office
  - **Visual**: generic item 10
  - **Hidden**: false

- **ID**: `item_11`
  - **Name**: Item 11
  - **Description**: A useful item found at Manager Office
  - **Visual**: generic item 11
  - **Hidden**: false

### Parking Garage
- **ID**: `item_13`
  - **Name**: Item 13
  - **Description**: A useful item found at Parking Garage
  - **Visual**: generic item 13
  - **Hidden**: false

- **ID**: `item_14`
  - **Name**: Item 14
  - **Description**: A useful item found at Parking Garage
  - **Visual**: generic item 14
  - **Hidden**: true
  - **Unlock**:
    - Task `MM2`
    - Task `MM3`

### Server Room
- **ID**: `item_1`
  - **Name**: Item 1
  - **Description**: A useful item found at Server Room
  - **Visual**: generic item 1
  - **Hidden**: true
  - **Unlock**:
    - Task `D5`

- **ID**: `item_2`
  - **Name**: Item 2
  - **Description**: A useful item found at Server Room
  - **Visual**: generic item 2
  - **Hidden**: false

### Teller Area
- **ID**: `item_12`
  - **Name**: Item 12
  - **Description**: A useful item found at Teller Area
  - **Visual**: generic item 12
  - **Hidden**: true
  - **Unlock**:
    - Task `D3`

### Vault
- **ID**: `item_6`
  - **Name**: Item 6
  - **Description**: A useful item found at Vault
  - **Visual**: generic item 6
  - **Hidden**: false

- **ID**: `item_7`
  - **Name**: Item 7
  - **Description**: A useful item found at Vault
  - **Visual**: generic item 7
  - **Hidden**: false

- **ID**: `item_8`
  - **Name**: Item 8
  - **Description**: A useful item found at Vault
  - **Visual**: generic item 8
  - **Hidden**: false

## NPCs

### guard - Security Guard
- **ID**: `security_guard`
- **Role**: guard
- **Location**: `server_room`
- **Age**: 35
- **Gender**: person
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: neutral
- **Attitude**: suspicious
- **Details**: Standard appearance
- **Personality**: Cautious and rule-following
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `security_guard_info_1` LOW: Information from Security Guard
- **Actions Available**:
  - `security_guard_action_1` HIGH: Action performed by Security Guard
  - `security_guard_action_2` MEDIUM: Action performed by Security Guard
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### IT - IT Specialist
- **ID**: `it_specialist`
- **Role**: IT
- **Location**: `manager_office`
- **Age**: 35
- **Gender**: man
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: friendly
- **Attitude**: suspicious
- **Details**: Standard appearance
- **Personality**: Technical and distracted
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `it_specialist_info_1` HIGH: Information from IT Specialist
  - `it_specialist_info_2` MEDIUM: Information from IT Specialist
- **Actions Available**:
  - `it_specialist_action_1` MEDIUM: Action performed by IT Specialist
  - `it_specialist_action_2` LOW: Action performed by IT Specialist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

## Roles & Tasks

### Driver

**Tasks:**

1. **D1. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `manager_office`
   - *Prerequisites:* None (starting task)

2. **D3. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `lobby`
   - *Prerequisites:*
      - Task `MM1`
      - Outcome `security_guard_action_2`

3. **D5. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `manager_office`
   - *Prerequisites:*
      - Outcome `it_specialist_action_1`
      - Task `MM3`

4. **D6. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_2`, `it_specialist_info_1`, `it_specialist_action_1`
   - *Location:* `manager_office`
   - *Prerequisites:*
      # Removed: Outcome `it_specialist_action_1`

5. **D7. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `vault`
   - *Prerequisites:*
      - Task `D5`


### Mastermind

**Tasks:**

1. **MM1. 🎮 lock_picking** - Complete lock picking
   - *Location:* `vault`
   - *Prerequisites:* None (starting task)

2. **MM2. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `parking_garage`
   - *Prerequisites:*
      - Task `MM1`

3. **MM3. 🎮 alarm_disable** - Complete alarm disable
   - *Location:* `server_room`
   - *Prerequisites:*
      - Task `MM2`

4. **MM4. 💬 NPC_LLM** - Talk to Security Guard
   - *NPC:* `security_guard`
   - *Target Outcomes:* `security_guard_action_2`, `security_guard_info_1`
   - *Location:* `server_room`
   - *Prerequisites:*
      - Task `MM3`
      - Task `MM2`

5. **MM6. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_1`
   - *Location:* `manager_office`
   - *Prerequisites:*
      - Task `MM3`


### Safe Cracker

**Tasks:**

1. **SC1. 🔍 SEARCH** - Search for items at Manager Office
   - *Search Items:* `item_10`
   - *Location:* `manager_office`
   - *Prerequisites:* None (starting task)

2. **SC2. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_1`, `it_specialist_action_2`
   - *Location:* `manager_office`
   - *Prerequisites:*
      - Task `MM3`
      - Task `MM2`

3. **SC3. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_action_2`
   - *Location:* `manager_office`
   - *Prerequisites:*
      - Outcome `it_specialist_info_1`

4. **SC4. 💬 NPC_LLM** - Talk to Security Guard
   - *NPC:* `security_guard`
   - *Target Outcomes:* `security_guard_action_1`
   - *Location:* `server_room`
   - *Prerequisites:*
      - Task `SC3`

5. **SC5. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `parking_garage`
   - *Prerequisites:*
      - Task `MM3`

6. **SC6. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `vault`
   - *Prerequisites:*
      - Task `MM6`