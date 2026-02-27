---
---
---
---
---
---
# Complete the heist successfully

**ID**: `art_gallery`
**Scenario**: Complete the heist successfully
**Selected Roles**: Insider, Mastermind
**Player Count**: 2 players

## Objective
Complete the heist successfully

## Locations

### Exterior
- **Entry Point** (`entry_point`): Initial access point

### Interior
- **Main Area** (`main_area`): Primary area
- **Target Room** (`target_room`): Final objective room
- **Secure Area** (`secure_area`): Restricted zone

**Total Locations**: 4

## Items by Location

### Entry Point
- **Item 5** (`item_5`)
  - **Description**: A useful item found at Entry Point
  - **Visual**: generic item 5
  - **Hidden**: false

- **Item 6** (`item_6`)
  - **Description**: A useful item found at Entry Point
  - **Visual**: generic item 6
  - **Hidden**: false

### Main Area
- **Item 1** (`item_1`)
  - **Description**: A useful item found at Main Area
  - **Visual**: generic item 1
  - **Hidden**: false

### Secure Area
- **Item 7** (`item_7`)
  - **Description**: A useful item found at Secure Area
  - **Visual**: generic item 7
  - **Hidden**: false

### Target Room
- **Item 2** (`item_2`)
  - **Description**: A useful item found at Target Room
  - **Visual**: generic item 2
  - **Hidden**: true
  - **Unlock**:
    - Task `I2`

- **Item 3** (`item_3`)
  - **Description**: A useful item found at Target Room
  - **Visual**: generic item 3
  - **Hidden**: true
  - **Unlock**:
    - Task `MM5`
    - Task `I1`

- **Item 4** (`item_4`)
  - **Description**: A useful item found at Target Room
  - **Visual**: generic item 4
  - **Hidden**: true
  - **Unlock**:
    - Task `MM4`
    - Task `I2`

## NPCs

### curator - Curator
- **ID**: `curator`
- **Role**: curator
- **Location**: `secure_area`
- **Age**: 35
- **Gender**: man
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: friendly
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

### manager - Manager
- **ID**: `manager`
- **Role**: manager
- **Location**: `secure_area`
- **Age**: 35
- **Gender**: person
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: neutral
- **Attitude**: professional
- **Details**: Standard appearance
- **Personality**: Busy and authoritative
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `manager_info_1` HIGH: Information from Manager
- **Actions Available**:
  - `manager_action_1` MEDIUM: Action performed by Manager
  - `manager_action_2` LOW: Action performed by Manager
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### IT - IT Specialist
- **ID**: `it_specialist`
- **Role**: IT
- **Location**: `secure_area`
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
- **Actions Available**:
  - `it_specialist_action_1` LOW: Action performed by IT Specialist
  - `it_specialist_action_2` MEDIUM: Action performed by IT Specialist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### receptionist - Receptionist
- **ID**: `receptionist`
- **Role**: receptionist
- **Location**: `entry_point`
- **Age**: 35
- **Gender**: person
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: friendly
- **Attitude**: casual
- **Details**: Standard appearance
- **Personality**: Professional and helpful
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `receptionist_info_1` LOW: Information from Receptionist
  - `receptionist_info_2` HIGH: Information from Receptionist
- **Actions Available**:
  - `receptionist_action_1` LOW: Action performed by Receptionist
  - `receptionist_action_2` MEDIUM: Action performed by Receptionist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

## Roles & Tasks

### Insider

**Tasks:**

1. **I1. 🎮 lock_picking** - Complete lock picking
   - *Location:* `secure_area`
   - *Prerequisites:* None (starting task)

2. **I2. 💬 NPC_LLM** - Talk to Receptionist
   - *NPC:* `receptionist`
   - *Target Outcomes:* `receptionist_info_1`, `receptionist_action_1`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `I1`

3. **I3. 🎮 lock_picking** - Complete lock picking
   - *Location:* `secure_area`
   - *Prerequisites:*
      - Task `I2`
      - Outcome `receptionist_action_1`

4. **I4. 💬 NPC_LLM** - Talk to Receptionist
   - *NPC:* `receptionist`
   - *Target Outcomes:* `receptionist_action_1`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `I1`


### Mastermind

**Tasks:**

1. **MM1. 🎮 lock_picking** - Complete lock picking
   - *Location:* `target_room`
   - *Prerequisites:* None (starting task)

2. **MM2. 🔍 SEARCH** - Search Entry Point
   - *Search Items:* `item_6`, `item_5`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `MM1`

3. **MM3. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_action_1`
   - *Location:* `secure_area`
   - *Prerequisites:*
      - Outcome `receptionist_action_1`

4. **MM4. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `secure_area`
   - *Prerequisites:*
      - Task `I2`
      - Outcome `receptionist_info_1`

5. **MM5. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `secure_area`
   - *Prerequisites:*
      - Task `MM1`

6. **MM6. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Outcome `receptionist_info_1`


