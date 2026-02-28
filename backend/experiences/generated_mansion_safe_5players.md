---
---
---
---
---
---
# Complete the heist successfully

**ID**: `mansion_safe`
**Scenario**: Complete the heist successfully
**Selected Roles**: Cat Burglar, Grifter, Lookout, Mastermind, Safe Cracker
**Player Count**: 5 players

## Objective
Complete the heist successfully

## Locations

### Exterior
- **Entry Point** (`entry_point`): Initial access point

### Interior
- **Secure Area** (`secure_area`): Restricted zone
- **Target Room** (`target_room`): Final objective room
- **Main Area** (`main_area`): Primary area

### interior
- **Extra Location 1** (`extra_location_1`): Additional location for scenario
- **Extra Location 2** (`extra_location_2`): Additional location for scenario

**Total Locations**: 6

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

- **Item 7** (`item_7`)
  - **Description**: A useful item found at Entry Point
  - **Visual**: generic item 7
  - **Hidden**: true
  - **Unlock**:
    - Task `MM2`

### Main Area
- **Item 8** (`item_8`)
  - **Description**: A useful item found at Main Area
  - **Visual**: generic item 8
  - **Hidden**: true
  - **Unlock**:
    - Task `SC5`

- **Item 9** (`item_9`)
  - **Description**: A useful item found at Main Area
  - **Visual**: generic item 9
  - **Hidden**: false

### Secure Area
- **Item 1** (`item_1`)
  - **Description**: A useful item found at Secure Area
  - **Visual**: generic item 1
  - **Hidden**: true
  - **Unlock**:
    - Task `CB3`
    - Task `G1`

- **Item 2** (`item_2`)
  - **Description**: A useful item found at Secure Area
  - **Visual**: generic item 2
  - **Hidden**: true
  - **Unlock**:
    - Task `CB1`

### Target Room
- **Item 3** (`item_3`)
  - **Description**: A useful item found at Target Room
  - **Visual**: generic item 3
  - **Hidden**: false

- **Item 4** (`item_4`)
  - **Description**: A useful item found at Target Room
  - **Visual**: generic item 4
  - **Hidden**: false

## NPCs

### IT - IT Specialist
- **ID**: `it_specialist`
- **Role**: IT
- **Location**: `entry_point`
- **Age**: 35
- **Gender**: woman
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
  - `it_specialist_info_2` HIGH: Information from IT Specialist
- **Actions Available**:
  - `it_specialist_action_1` MEDIUM: Action performed by IT Specialist
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
- **Attitude**: casual
- **Details**: Standard appearance
- **Personality**: Cautious and rule-following
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `security_guard_info_1` HIGH: Information from Security Guard
- **Actions Available**:
  - `security_guard_action_1` HIGH: Action performed by Security Guard
  - `security_guard_action_2` HIGH: Action performed by Security Guard
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

## Roles & Tasks

### Cat Burglar

**Tasks:**

1. **CB1. 🎮 lock_picking** - Complete lock picking
   - *Location:* `secure_area`
   - *Prerequisites:* None (starting task)

2. **CB2. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Outcome `it_specialist_info_1`

3. **CB3. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_1`, `it_specialist_info_2`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `G3`

4. **CB4. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `target_room`
   - *Prerequisites:*
      - Outcome `it_specialist_info_1`

5. **CB5. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `MM1`
      - Task `CB1`


### Grifter

**Tasks:**

1. **G1. 🔍 SEARCH** - Search for items at Entry Point
   - *Search Items:* `item_6`
   - *Location:* `entry_point`
   - *Prerequisites:* None (starting task)

2. **G2. 🔍 SEARCH** - Search Entry Point
   - *Search Items:* `item_7`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `MM2`
      - Outcome `security_guard_info_1`

3. **G3. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_1`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `SC5`

4. **G4. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Outcome `it_specialist_info_2`

5. **G5. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Outcome `it_specialist_info_1`
      - Task `MM1`

6. **G6. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_1`, `it_specialist_info_2`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Outcome `it_specialist_info_2`


### Lookout

**Tasks:**

1. **L1. 🔍 SEARCH** - Search for items at Main Area
   - *Search Items:* `item_9`
   - *Location:* `main_area`
   - *Prerequisites:* None (starting task)

2. **L2. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `target_room`
   - *Prerequisites:*
      - Task `MM3`

3. **L3. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `G1`
      - Outcome `it_specialist_info_2`

4. **L4. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_2`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `SC3`
      - Outcome `security_guard_info_1`

5. **L5. 🔍 SEARCH** - Search Main Area
   - *Search Items:* `item_8`
   - *Location:* `main_area`
   - *Prerequisites:* None (starting task)

6. **L6. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_1`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `G6`


### Mastermind

**Tasks:**

1. **MM1. 🎮 lock_picking** - Complete lock picking
   - *Location:* `main_area`
   - *Prerequisites:* None (starting task)

2. **MM2. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_2`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `MM1`

3. **MM3. 💬 NPC_LLM** - Talk to Security Guard
   - *NPC:* `security_guard`
   - *Target Outcomes:* `security_guard_info_1`
   - *Location:* `main_area`
   - *Prerequisites:*
      - Task `MM2`
      - Outcome `it_specialist_info_2`

4. **MM4. 🎮 camera_bypass** - Complete camera bypass
   - *Location:* `secure_area`
   - *Prerequisites:* None (starting task)

5. **MM5. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `secure_area`
   - *Prerequisites:*
      - Outcome `it_specialist_info_2`
      - Task `MM3`


### Safe Cracker

**Tasks:**

1. **SC1. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `entry_point`
   - *Prerequisites:* None (starting task)

2. **SC2. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `secure_area`
   - *Prerequisites:*
      - Task `MM5`

3. **SC3. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_1`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Outcome `it_specialist_info_2`

4. **SC4. 🔍 SEARCH** - Search Secure Area
   - *Search Items:* `item_1`, `item_2`
   - *Location:* `secure_area`
   - *Prerequisites:*
      - Task `SC1`

5. **SC5. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_1`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `SC4`
      - Task `MM3`

6. **SC6. 🔍 SEARCH** - Search Entry Point
   - *Search Items:* `item_5`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Outcome `security_guard_info_1`


