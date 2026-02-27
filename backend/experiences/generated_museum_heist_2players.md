---
---
---
---
---
---
---
# Steal the priceless artifact from the museum vault

**ID**: `museum_heist`
**Scenario**: Steal the priceless artifact from the museum vault
**Selected Roles**: Mastermind, Safe Cracker
**Player Count**: 2 players

## Objective
Steal the priceless artifact from the museum vault

## Locations

### Museum Exterior
- **Loading Dock** (`loading_dock`): Service entrance

### Museum Interior
- **Security Office** (`security_office`): Security monitoring room
- **Exhibit Floor** (`exhibit_floor`): Main gallery with displays
- **Vault Chamber** (`vault_chamber`): Secure vault room

**Total Locations**: 4

## Items by Location

### Exhibit Floor
- **ID**: `item_4`
  - **Name**: Item 4
  - **Description**: A useful item found at Exhibit Floor
  - **Visual**: generic item 4
  - **Hidden**: false

### Loading Dock
- **ID**: `item_5`
  - **Name**: Item 5
  - **Description**: A useful item found at Loading Dock
  - **Visual**: generic item 5
  - **Hidden**: false

- **ID**: `item_6`
  - **Name**: Item 6
  - **Description**: A useful item found at Loading Dock
  - **Visual**: generic item 6
  - **Hidden**: false

- **ID**: `item_7`
  - **Name**: Item 7
  - **Description**: A useful item found at Loading Dock
  - **Visual**: generic item 7
  - **Hidden**: false

### Security Office
- **ID**: `item_1`
  - **Name**: Item 1
  - **Description**: A useful item found at Security Office
  - **Visual**: generic item 1
  - **Hidden**: true
  - **Unlock**:
    - Task `SC2`
    - Task `MM1`

- **ID**: `item_2`
  - **Name**: Item 2
  - **Description**: A useful item found at Security Office
  - **Visual**: generic item 2
  - **Hidden**: false

- **ID**: `item_3`
  - **Name**: Item 3
  - **Description**: A useful item found at Security Office
  - **Visual**: generic item 3
  - **Hidden**: true
  - **Unlock**:
    - Task `SC2`
    - Task `SC5`

### Vault Chamber
- **ID**: `item_8`
  - **Name**: Item 8
  - **Description**: A useful item found at Vault Chamber
  - **Visual**: generic item 8
  - **Hidden**: false

- **ID**: `item_9`
  - **Name**: Item 9
  - **Description**: A useful item found at Vault Chamber
  - **Visual**: generic item 9
  - **Hidden**: true
  - **Unlock**:
    - Task `SC4`

## NPCs

### maintenance - Janitor
- **ID**: `janitor`
- **Role**: maintenance
- **Location**: `loading_dock`
- **Age**: 35
- **Gender**: woman
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: friendly
- **Attitude**: professional
- **Details**: Standard appearance
- **Personality**: Friendly but observant
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `janitor_info_1` LOW: Information from Janitor
- **Actions Available**:
  - `janitor_action_1` LOW: Action performed by Janitor
  - `janitor_action_2` LOW: Action performed by Janitor
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### receptionist - Receptionist
- **ID**: `receptionist`
- **Role**: receptionist
- **Location**: `loading_dock`
- **Age**: 35
- **Gender**: person
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
  - `receptionist_info_2` MEDIUM: Information from Receptionist
- **Actions Available**:
  - `receptionist_action_1` LOW: Action performed by Receptionist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

## Roles & Tasks

### Mastermind

**Tasks:**

1. **MM1. 🎮 camera_bypass** - Complete camera bypass
   - *Location:* `loading_dock`
   - *Prerequisites:* None (starting task)

2. **MM2. 🔍 SEARCH** - Search Exhibit Floor
   - *Search Items:* `item_4`
   - *Location:* `exhibit_floor`
   - *Prerequisites:*
      - Task `MM1`

3. **MM3. 🔍 SEARCH** - Search Vault Chamber
   - *Search Items:* `item_8`, `item_9`
   - *Location:* `vault_chamber`
   - *Prerequisites:*
      - Task `MM2`
      - Task `MM1`

4. **MM4. 💬 NPC_LLM** - Talk to Janitor
   - *NPC:* `janitor`
   - *Target Outcomes:* `janitor_info_1`, `janitor_action_2`
   - *Location:* `loading_dock`
   - *Prerequisites:*
      - Task `MM1`
      - Task `MM3`

5. **MM5. 🎮 camera_bypass** - Complete camera bypass
   - *Location:* `security_office`
   - *Prerequisites:*
      - Task `MM3`


### Safe Cracker

**Tasks:**

1. **SC1. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `loading_dock`
   - *Prerequisites:* None (starting task)

2. **SC2. 🎮 safe_cracking** - Complete safe cracking
   - *Location:* `vault_chamber`
   - *Prerequisites:*
      - Task `MM3`

3. **SC3. 🎮 wire_connecting** - Complete wire connecting
   - *Location:* `loading_dock`
   - *Prerequisites:*
      - Task `MM2`

4. **SC4. 🎮 alarm_disable** - Complete alarm disable
   - *Location:* `vault_chamber`
   - *Prerequisites:*
      - Task `SC3`
      - Task `SC2`

5. **SC5. 💬 NPC_LLM** - Talk to Janitor
   - *NPC:* `janitor`
   - *Target Outcomes:* `janitor_action_2`, `janitor_info_1`
   - *Location:* `loading_dock`
   - *Prerequisites:*
      - Task `SC3`

6. **SC6. 🎮 fingerprint_matching** - Complete fingerprint matching
   - *Location:* `loading_dock`
   - *Prerequisites:*
      - Task `SC1`
      - Task `SC5`