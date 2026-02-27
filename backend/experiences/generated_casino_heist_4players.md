---
---
---
---
---
---
# Complete the heist successfully

**ID**: `casino_heist`
**Scenario**: Complete the heist successfully
**Selected Roles**: Grifter, Hacker, Mastermind, Safe Cracker
**Player Count**: 4 players

## Objective
Complete the heist successfully

## Locations

### Exterior
- **Entry Point** (`entry_point`): Initial access point

### Interior
- **Target Room** (`target_room`): Final objective room
- **Secure Area** (`secure_area`): Restricted zone
- **Main Area** (`main_area`): Primary area

**Total Locations**: 4

## Items by Location

### Entry Point
- **Item 7** (`item_7`)
  - **Description**: A useful item found at Entry Point
  - **Visual**: generic item 7
  - **Hidden**: false

- **Item 8** (`item_8`)
  - **Description**: A useful item found at Entry Point
  - **Visual**: generic item 8
  - **Hidden**: true
  - **Unlock**:
    - Task `H2`

### Main Area
- **Item 4** (`item_4`)
  - **Description**: A useful item found at Main Area
  - **Visual**: generic item 4
  - **Hidden**: false

- **Item 5** (`item_5`)
  - **Description**: A useful item found at Main Area
  - **Visual**: generic item 5
  - **Hidden**: false

- **Item 6** (`item_6`)
  - **Description**: A useful item found at Main Area
  - **Visual**: generic item 6
  - **Hidden**: false

### Secure Area
- **Item 3** (`item_3`)
  - **Description**: A useful item found at Secure Area
  - **Visual**: generic item 3
  - **Hidden**: false

### Target Room
- **Item 1** (`item_1`)
  - **Description**: A useful item found at Target Room
  - **Visual**: generic item 1
  - **Hidden**: false

- **Item 2** (`item_2`)
  - **Description**: A useful item found at Target Room
  - **Visual**: generic item 2
  - **Hidden**: false

## NPCs

### IT - IT Specialist
- **ID**: `it_specialist`
- **Role**: IT
- **Location**: `main_area`
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
  - `it_specialist_info_1` HIGH: Information from IT Specialist
  - `it_specialist_info_2` LOW: Information from IT Specialist
- **Actions Available**:
  - `it_specialist_action_1` MEDIUM: Action performed by IT Specialist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### curator - Curator
- **ID**: `curator`
- **Role**: curator
- **Location**: `entry_point`
- **Age**: 35
- **Gender**: person
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: neutral
- **Attitude**: suspicious
- **Details**: Standard appearance
- **Personality**: Knowledgeable and proud
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `curator_info_1` LOW: Information from Curator
- **Actions Available**:
  - `curator_action_1` HIGH: Action performed by Curator
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### receptionist - Receptionist
- **ID**: `receptionist`
- **Role**: receptionist
- **Location**: `secure_area`
- **Age**: 35
- **Gender**: woman
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: friendly
- **Attitude**: suspicious
- **Details**: Standard appearance
- **Personality**: Professional and helpful
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `receptionist_info_1` HIGH: Information from Receptionist
  - `receptionist_info_2` LOW: Information from Receptionist
- **Actions Available**:
  - `receptionist_action_1` MEDIUM: Action performed by Receptionist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### guard - Security Guard
- **ID**: `security_guard`
- **Role**: guard
- **Location**: `main_area`
- **Age**: 35
- **Gender**: person
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
  - `security_guard_info_2` LOW: Information from Security Guard
- **Actions Available**:
  - `security_guard_action_1` LOW: Action performed by Security Guard
  - `security_guard_action_2` HIGH: Action performed by Security Guard
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

## Roles & Tasks

### Grifter

**Tasks:**

1. **G1. 🔍 SEARCH** - Search for items at Secure Area
   - *Search Items:* `item_3`
   - *Location:* `secure_area`
   - *Prerequisites:* None (starting task)

2. **G2. 🎮 alarm_disable** - Complete alarm disable
   - *Location:* `main_area`
   - *Prerequisites:*
      - Outcome `it_specialist_info_1`

3. **G3. 🔍 SEARCH** - Search Target Room
   - *Search Items:* `item_1`
   - *Location:* `target_room`
   - *Prerequisites:*
      - Task `MM3`

4. **G4. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `target_room`
   - *Prerequisites:*
      - Task `MM3`
      - Task `G2`

5. **G5. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `MM1`


### Hacker

**Tasks:**

1. **H1. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `secure_area`
   - *Prerequisites:* None (starting task)

2. **H2. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `G5`
      - Task `MM1`

3. **H3. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `main_area`
   - *Prerequisites:*
      - Task `G2`

4. **H4. 💬 NPC_LLM** - Talk to Curator
   - *NPC:* `curator`
   - *Target Outcomes:* `curator_info_1`, `curator_action_1`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `G3`
      - Task `SC4`

5. **H5. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `target_room`
   - *Prerequisites:*
      - Task `G4`
      - Task `MM3`


### Mastermind

**Tasks:**

1. **MM1. 🔍 SEARCH** - Search for items at Entry Point
   - *Search Items:* `item_7`
   - *Location:* `entry_point`
   - *Prerequisites:* None (starting task)

2. **MM2. 🔍 SEARCH** - Search Main Area
   - *Search Items:* `item_5`
   - *Location:* `main_area`
   - *Prerequisites:*
      - Task `MM1`

3. **MM3. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `MM1`

4. **MM4. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_1`
   - *Location:* `main_area`
   - *Prerequisites:*
      - Task `MM2`
      - Task `MM3`

5. **MM5. 🎮 alarm_disable** - Complete alarm disable
   - *Location:* `secure_area`
   - *Prerequisites:*
      - Task `MM4`
      - Task `MM1`


### Safe Cracker

**Tasks:**

1. **SC1. 🎮 alarm_disable** - Complete alarm disable
   - *Location:* `secure_area`
   - *Prerequisites:* None (starting task)

2. **SC2. 🔍 SEARCH** - Search Main Area
   - *Search Items:* `item_4`, `item_6`
   - *Location:* `main_area`
   - *Prerequisites:*
      - Task `MM4`

3. **SC3. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_1`, `it_specialist_action_1`
   - *Location:* `main_area`
   - *Prerequisites:*
      - Task `MM5`
      - Task `G5`

4. **SC4. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_2`
   - *Location:* `main_area`
   - *Prerequisites:*
      - Task `MM2`


