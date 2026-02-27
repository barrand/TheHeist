---
---
---
---
---
---
# Steal confidential documents from the executive suite

**ID**: `office_infiltration`
**Scenario**: Steal confidential documents from the executive suite
**Selected Roles**: Hacker, Insider
**Player Count**: 2 players

## Objective
Steal confidential documents from the executive suite

## Locations

### Office Exterior
- **Rooftop** (`rooftop`): Roof access

### Office Interior
- **Archive Room** (`archive_room`): Document storage
- **Server Room** (`server_room`): Data center
- **Cubicle Farm** (`cubicle_farm`): Open workspace
- **Executive Suite** (`executive_suite`): C-level offices
- **Reception Area** (`reception`): Front desk

**Total Locations**: 6

## Items by Location

### Archive Room
- **Item 1** (`item_1`)
  - **Description**: A useful item found at Archive Room
  - **Visual**: generic item 1
  - **Hidden**: false

### Cubicle Farm
- **Item 6** (`item_6`)
  - **Description**: A useful item found at Cubicle Farm
  - **Visual**: generic item 6
  - **Hidden**: true
  - **Unlock**:
    - Task `H4`
    - Task `I1`

- **Item 7** (`item_7`)
  - **Description**: A useful item found at Cubicle Farm
  - **Visual**: generic item 7
  - **Hidden**: false

### Executive Suite
- **Item 8** (`item_8`)
  - **Description**: A useful item found at Executive Suite
  - **Visual**: generic item 8
  - **Hidden**: false

- **Item 9** (`item_9`)
  - **Description**: A useful item found at Executive Suite
  - **Visual**: generic item 9
  - **Hidden**: false

### Reception Area
- **Item 10** (`item_10`)
  - **Description**: A useful item found at Reception Area
  - **Visual**: generic item 10
  - **Hidden**: false

### Rooftop
- **Item 2** (`item_2`)
  - **Description**: A useful item found at Rooftop
  - **Visual**: generic item 2
  - **Hidden**: false

- **Item 3** (`item_3`)
  - **Description**: A useful item found at Rooftop
  - **Visual**: generic item 3
  - **Hidden**: true
  - **Unlock**:
    - Task `I2`
    - Task `H5`

- **Item 4** (`item_4`)
  - **Description**: A useful item found at Rooftop
  - **Visual**: generic item 4
  - **Hidden**: true
  - **Unlock**:
    - Task `I4`
    - Task `I1`

### Server Room
- **Item 5** (`item_5`)
  - **Description**: A useful item found at Server Room
  - **Visual**: generic item 5
  - **Hidden**: false

## NPCs

### curator - Curator
- **ID**: `curator`
- **Role**: curator
- **Location**: `rooftop`
- **Age**: 35
- **Gender**: man
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: stern
- **Attitude**: professional
- **Details**: Standard appearance
- **Personality**: Knowledgeable and proud
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `curator_info_1` MEDIUM: Information from Curator
  - `curator_info_2` MEDIUM: Information from Curator
- **Actions Available**:
  - `curator_action_1` HIGH: Action performed by Curator
  - `curator_action_2` LOW: Action performed by Curator
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### IT - IT Specialist
- **ID**: `it_specialist`
- **Role**: IT
- **Location**: `rooftop`
- **Age**: 35
- **Gender**: person
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: friendly
- **Attitude**: suspicious
- **Details**: Standard appearance
- **Personality**: Technical and distracted
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `it_specialist_info_1` LOW: Information from IT Specialist
  - `it_specialist_info_2` HIGH: Information from IT Specialist
- **Actions Available**:
  - `it_specialist_action_1` LOW: Action performed by IT Specialist
  - `it_specialist_action_2` MEDIUM: Action performed by IT Specialist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

## Roles & Tasks

### Hacker

**Tasks:**

1. **H1. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `server_room`
   - *Prerequisites:* None (starting task)

2. **H2. 💬 NPC_LLM** - Talk to Curator
   - *NPC:* `curator`
   - *Target Outcomes:* `curator_info_1`
   - *Location:* `rooftop`
   - *Prerequisites:*
      - Outcome `curator_action_1`
      - Task `I2`

3. **H3. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_2`, `it_specialist_action_2`
   - *Location:* `rooftop`
   - *Prerequisites:*
      - Task `I4`

4. **H4. 🎮 alarm_disable** - Complete alarm disable
   - *Location:* `executive_suite`
   - *Prerequisites:*
      - Task `I3`
      - Task `H2`

5. **H5. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_action_1`, `it_specialist_info_2`
   - *Location:* `rooftop`
   - *Prerequisites:*
      - Task `I2`


### Insider

**Tasks:**

1. **I1. 🎮 camera_bypass** - Complete camera bypass
   - *Location:* `reception`
   - *Prerequisites:* None (starting task)

2. **I2. 💬 NPC_LLM** - Talk to Curator
   - *NPC:* `curator`
   - *Target Outcomes:* `curator_action_1`, `curator_info_2`
   - *Location:* `rooftop`
   - *Prerequisites:*
      - Task `I1`

3. **I3. 🔍 SEARCH** - Search Server Room
   - *Search Items:* `item_5`
   - *Location:* `server_room`
   - *Prerequisites:*
      - Task `I2`
      - Outcome `curator_info_2`

4. **I4. 💬 NPC_LLM** - Talk to IT Specialist
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_1`, `it_specialist_action_2`
   - *Location:* `rooftop`
   - *Prerequisites:*
      - Outcome `curator_action_1`
      - Task `I2`

5. **I5. 🎮 camera_bypass** - Complete camera bypass
   - *Location:* `archive_room`
   - *Prerequisites:*
      - Outcome `it_specialist_action_2`

6. **I6. 🎮 alarm_disable** - Complete alarm disable
   - *Location:* `cubicle_farm`
   - *Prerequisites:*
      - Task `I3`


