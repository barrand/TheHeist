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
- **Reception Area** (`reception`): Front desk
- **Executive Suite** (`executive_suite`): C-level offices

**Total Locations**: 6

## Items by Location

### Archive Room
- **Item 1** (`item_1`)
  - **Description**: A useful item found at Archive Room
  - **Visual**: generic item 1
  - **Hidden**: false

- **Item 2** (`item_2`)
  - **Description**: A useful item found at Archive Room
  - **Visual**: generic item 2
  - **Hidden**: false

### Cubicle Farm
- **Item 6** (`item_6`)
  - **Description**: A useful item found at Cubicle Farm
  - **Visual**: generic item 6
  - **Hidden**: true
  - **Unlock**:
    - Task `H6`

- **Item 7** (`item_7`)
  - **Description**: A useful item found at Cubicle Farm
  - **Visual**: generic item 7
  - **Hidden**: true
  - **Unlock**:
    - Task `I3`
    - Task `H3`

- **Item 8** (`item_8`)
  - **Description**: A useful item found at Cubicle Farm
  - **Visual**: generic item 8
  - **Hidden**: true
  - **Unlock**:
    - Task `H6`

### Executive Suite
- **Item 10** (`item_10`)
  - **Description**: A useful item found at Executive Suite
  - **Visual**: generic item 10
  - **Hidden**: true
  - **Unlock**:
    - Task `H2`

- **Item 11** (`item_11`)
  - **Description**: A useful item found at Executive Suite
  - **Visual**: generic item 11
  - **Hidden**: false

- **Item 12** (`item_12`)
  - **Description**: A useful item found at Executive Suite
  - **Visual**: generic item 12
  - **Hidden**: false

### Reception Area
- **Item 9** (`item_9`)
  - **Description**: A useful item found at Reception Area
  - **Visual**: generic item 9
  - **Hidden**: false

### Rooftop
- **Item 3** (`item_3`)
  - **Description**: A useful item found at Rooftop
  - **Visual**: generic item 3
  - **Hidden**: false

- **Item 4** (`item_4`)
  - **Description**: A useful item found at Rooftop
  - **Visual**: generic item 4
  - **Hidden**: false

### Server Room
- **Item 5** (`item_5`)
  - **Description**: A useful item found at Server Room
  - **Visual**: generic item 5
  - **Hidden**: false

## NPCs

### curator - Curator
- **ID**: `curator`
- **Role**: curator
- **Location**: `cubicle_farm`
- **Age**: 35
- **Gender**: man
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: friendly
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
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### IT - IT Specialist
- **ID**: `it_specialist`
- **Role**: IT
- **Location**: `rooftop`
- **Age**: 35
- **Gender**: man
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: neutral
- **Attitude**: professional
- **Details**: Standard appearance
- **Personality**: Technical and distracted
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `it_specialist_info_1` LOW: Information from IT Specialist
  - `it_specialist_info_2` HIGH: Information from IT Specialist
- **Actions Available**:
  - `it_specialist_action_1` HIGH: Action performed by IT Specialist
  - `it_specialist_action_2` HIGH: Action performed by IT Specialist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### receptionist - Receptionist
- **ID**: `receptionist`
- **Role**: receptionist
- **Location**: `cubicle_farm`
- **Age**: 35
- **Gender**: woman
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: neutral
- **Attitude**: casual
- **Details**: Standard appearance
- **Personality**: Professional and helpful
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `receptionist_info_1` LOW: Information from Receptionist
  - `receptionist_info_2` LOW: Information from Receptionist
- **Actions Available**:
  - `receptionist_action_1` LOW: Action performed by Receptionist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

## Roles & Tasks

### Hacker

**Tasks:**

1. **H1. 🔍 SEARCH** - Search for items at Rooftop
   - *Search Items:* `item_4`
   - *Location:* `rooftop`
   - *Prerequisites:* None (starting task)

2. **H2. 💬 NPC_LLM** - Talk to Curator
   - *NPC:* `curator`
   - *Target Outcomes:* `curator_info_2`, `curator_action_1`
   - *Location:* `cubicle_farm`
   - *Prerequisites:*
      - Outcome `receptionist_info_2`

3. **H3. 💬 NPC_LLM** - Talk to Receptionist
   - *NPC:* `receptionist`
   - *Target Outcomes:* `receptionist_action_1`, `receptionist_info_1`
   - *Location:* `cubicle_farm`
   - *Prerequisites:*
      - Task `H2`
      - Outcome `curator_action_1`

4. **H4. 🤝 HANDOFF** - Hand off item to insider
   - *Handoff Item:* `item_4`
   - *Handoff To:* Insider
   - *Location:* `reception`
   - *Prerequisites:*
      - Outcome `receptionist_action_1`

5. **H5. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `reception`
   - *Prerequisites:*
      - Outcome `curator_action_1`
      - Task `I1`

6. **H6. 💬 NPC_LLM** - Talk to Receptionist
   - *NPC:* `receptionist`
   - *Target Outcomes:* `receptionist_info_1`, `receptionist_action_1`
   - *Location:* `cubicle_farm`
   - *Prerequisites:*
      - Outcome `curator_info_2`


### Insider

**Tasks:**

1. **I1. 🔍 SEARCH** - Search for items at Rooftop
   - *Search Items:* `item_3`
   - *Location:* `rooftop`
   - *Prerequisites:* None (starting task)

2. **I2. 🎮 alarm_disable** - Complete alarm disable
   - *Location:* `rooftop`
   - *Prerequisites:*
      - Task `I1`

3. **I3. 💬 NPC_LLM** - Talk to Receptionist
   - *NPC:* `receptionist`
   - *Target Outcomes:* `receptionist_info_1`, `receptionist_info_2`
   - *Location:* `cubicle_farm`
   - *Prerequisites:*
      - Task `I1`


