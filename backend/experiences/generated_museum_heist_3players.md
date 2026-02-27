# Steal the priceless artifact from the museum vault

**ID**: `museum_heist`
**Scenario**: Steal the priceless artifact from the museum vault
**Selected Roles**: Driver, Mastermind, Safe Cracker
**Player Count**: 3 players

## Objective
Steal the priceless artifact from the museum vault

## Locations

- **Rooftop Access** (`rooftop`): Rooftop entrance point
- **Loading Dock** (`loading_dock`): Service entrance
- **Security Office** (`security_office`): Security monitoring room
- **Exhibit Floor** (`exhibit_floor`): Main gallery with displays
- **Vault Chamber** (`vault_chamber`): The secure vault holding the artifact

**Total Locations**: 5

## Items by Location

### Exhibit Floor
- **ID**: `item_5`
  - **Name**: Exhibit Floor Item 5
  - **Description**: A useful item found at Exhibit Floor
  - **Visual**: generic item 5
  - **Required For**: []
  - **Hidden**: false

- **ID**: `item_6`
  - **Name**: Exhibit Floor Item 6
  - **Description**: A useful item found at Exhibit Floor
  - **Visual**: generic item 6
  - **Required For**: []
  - **Hidden**: false

### Loading Dock
- **ID**: `item_7`
  - **Name**: Loading Dock Item 7
  - **Description**: A useful item found at Loading Dock
  - **Visual**: generic item 7
  - **Required For**: []
  - **Hidden**: true
  - **Unlock**:
    - Task `D2`

- **ID**: `item_8`
  - **Name**: Loading Dock Item 8
  - **Description**: A useful item found at Loading Dock
  - **Visual**: generic item 8
  - **Required For**: []
  - **Hidden**: false

- **ID**: `item_9`
  - **Name**: Loading Dock Item 9
  - **Description**: A useful item found at Loading Dock
  - **Visual**: generic item 9
  - **Required For**: []
  - **Hidden**: true
  - **Unlock**:
    - Task `SC2`
    - Task `MM3`

### Rooftop Access
- **ID**: `item_2`
  - **Name**: Rooftop Access Item 2
  - **Description**: A useful item found at Rooftop Access
  - **Visual**: generic item 2
  - **Required For**: []
  - **Hidden**: false

### Security Office
- **ID**: `item_3`
  - **Name**: Security Office Item 3
  - **Description**: A useful item found at Security Office
  - **Visual**: generic item 3
  - **Required For**: []
  - **Hidden**: true
  - **Unlock**:
    - Task `D1`
    - Task `SC2`

### Vault Chamber
- **ID**: `item_10`
  - **Name**: Vault Chamber Item 10
  - **Description**: A useful item found at Vault Chamber
  - **Visual**: generic item 10
  - **Required For**: []
  - **Hidden**: true
  - **Unlock**:
    - Task `D3`

- **ID**: `item_11`
  - **Name**: Vault Chamber Item 11
  - **Description**: A useful item found at Vault Chamber
  - **Visual**: generic item 11
  - **Required For**: []
  - **Hidden**: false

## NPCs

### manager - Manager
- **ID**: `manager`
- **Role**: manager
- **Location**: `security_office`
- **Age**: 35
- **Gender**: man
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: friendly
- **Attitude**: suspicious
- **Details**: Standard appearance
- **Personality**: Busy and authoritative
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - **ID**: `manager_info_1`
    **Level**: LOW
    **Description**: Information from Manager
  - **ID**: `manager_info_2`
    **Level**: LOW
    **Description**: Information from Manager
  - **ID**: `manager_action_1`
    **Level**: MEDIUM
    **Description**: Action performed by Manager
- **Actions Available**:
  - **ID**: `manager_action_2`
    **Level**: MEDIUM
    **Description**: Action performed by Manager
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### maintenance - Janitor
- **ID**: `janitor`
- **Role**: maintenance
- **Location**: `loading_dock`
- **Age**: 35
- **Gender**: woman
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: stern
- **Attitude**: professional
- **Details**: Standard appearance
- **Personality**: Friendly but observant
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - **ID**: `janitor_info_1`
    **Level**: LOW
    **Description**: Information from Janitor
  - **ID**: `janitor_info_2`
    **Level**: LOW
    **Description**: Information from Janitor
- **Actions Available**:
  - **ID**: `janitor_action_1`
    **Level**: LOW
    **Description**: Action performed by Janitor
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

## Roles & Tasks

### Driver

**Tasks:**

1. **D1. 🔍 SEARCH** - Search for items at Vault Chamber
   - *Search Items:* `item_11`
   - *Location:* `vault_chamber`
   - *Prerequisites:* None (starting task)

2. **D2. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `security_office`
   - *Prerequisites:*
      - Task `SC3`

3. **D3. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `exhibit_floor`
   - *Prerequisites:*
      - Task `SC1`
      - Task `MM1`


### Mastermind

**Tasks:**

1. **MM1. 🎮 camera_bypass** - Complete camera bypass
   - *Location:* `security_office`
   - *Prerequisites:* None (starting task)

2. **MM2. 🎮 lock_picking** - Complete lock picking
   - *Location:* `rooftop`
   - *Prerequisites:*
      - Task `MM1`

3. **MM3. 🎮 camera_bypass** - Complete camera bypass
   - *Location:* `exhibit_floor`
   - *Prerequisites:*
      - Task `MM2`
      - Task `MM1`


### Safe Cracker

**Tasks:**

1. **SC1. 🔍 SEARCH** - Search for items at Exhibit Floor
   - *Search Items:* `item_6`, `item_5`
   - *Location:* `exhibit_floor`
   - *Prerequisites:* None (starting task)

2. **SC2. 💬 NPC_LLM** - Talk to Janitor
   - *NPC:* `janitor`
   - *Target Outcomes:* `janitor_info_1`
   - *Location:* `loading_dock`
   - *Prerequisites:*
      - Task `MM2`
      - Task `SC1`

3. **SC3. 🔍 SEARCH** - Search Loading Dock
   - *Search Items:* `item_7`
   - *Location:* `loading_dock`
   - *Prerequisites:*
      - Task `SC1`