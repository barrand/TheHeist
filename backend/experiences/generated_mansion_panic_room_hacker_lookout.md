---
---
---
---
---
---
# Break into the panic room and retrieve the hidden assets

**ID**: `mansion_panic_room`
**Scenario**: Break into the panic room and retrieve the hidden assets
**Selected Roles**: Hacker, Lookout
**Player Count**: 2 players

## Objective
Break into the panic room and retrieve the hidden assets

## Locations

### Exterior
- **Entry Point** (`entry_point`): Initial access point

### Interior
- **Control Room** (`control_room`): Security and systems hub
- **Secure Area** (`secure_area`): Restricted access zone
- **Target Room** (`target_room`): Final objective location

**Total Locations**: 4

## Items by Location

### Control Room
- **Network Analyzer Tablet** (`item_4`)
  - **Description**: Displays network traffic and identifies vulnerabilities in real-time.
  - **Visual**: A ruggedized tablet with a glowing green interface showing complex data streams and a multi-port adapter.
  - **Hidden**: false

- **Security Chief's Keycard** (`item_5`)
  - **Description**: Grants high-level access to restricted control systems.
  - **Visual**: A thick, black RFID card with a shimmering holographic security emblem and a magnetic stripe.
  - **Hidden**: true
  - **Unlock**:
    - Task `H1`
    - Task `H3`

- **Sonic Emitter Device** (`item_6`)
  - **Description**: Emits high-frequency sound to disrupt electronics and guard focus.
  - **Visual**: A small, cylindrical device with a perforated speaker grill and a single red activation button.
  - **Hidden**: false

### Entry Point
- **Electro-Bypass Shunt** (`item_1`)
  - **Description**: Temporarily disables low-level security panels.
  - **Visual**: A sleek, black, handheld device with a retractable antenna and glowing blue LEDs.
  - **Hidden**: false

- **Micro-Surveillance Drone** (`item_2`)
  - **Description**: Remote-controlled drone for discreet aerial recon.
  - **Visual**: A palm-sized, metallic grey quadcopter with four tiny, silent propellers and a pinhole camera.
  - **Hidden**: false

- **Universal Lock Pick Set** (`item_3`)
  - **Description**: A professional set for manipulating complex mechanical locks.
  - **Visual**: A compact, leather-bound case opening to reveal an array of polished steel picks, tension wrenches, and rakes.
  - **Hidden**: false

### Secure Area
- **Quantum Decryptor Dongle** (`item_7`)
  - **Description**: Breaks advanced encryption protocols with rapid processing.
  - **Visual**: A metallic, futuristic-looking USB drive with a pulsing purple light and intricate circuitry visible through a transparent casing.
  - **Hidden**: false

- **Encrypted Data Stick** (`item_8`)
  - **Description**: Contains critical access codes for the panic room vault.
  - **Visual**: A standard-looking USB stick, but with a small, almost invisible etched symbol and a heavy, cold feel.
  - **Hidden**: true
  - **Unlock**:
    - Task `L1`
    - Task `H1`

### Target Room
- **The Obsidian Heart** (`item_9`)
  - **Description**: A legendary, priceless black diamond with a unique, captivating luster.
  - **Visual**: A perfectly cut, deep black diamond, roughly the size of a pigeon's egg, mounted on a minimalist silver stand.
  - **Hidden**: false

## NPCs

### receptionist - Eleanor
- **ID**: `receptionist`
- **Role**: receptionist
- **Location**: `control_room`
- **Age**: 35
- **Gender**: man
- **Ethnicity**: Unknown
- **Clothing**: Professional attire
- **Expression**: neutral
- **Attitude**: professional
- **Details**: Standard appearance
- **Personality**: Professional and helpful
- **Relationships**: Interacts professionally with colleagues
- **Story Context**: Works at this location
- **Information Known**:
  - `receptionist_info_1` MEDIUM: Information from Receptionist
- **Actions Available**:
  - `receptionist_action_1` HIGH: Action performed by Receptionist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

### IT - Marcus
- **ID**: `it_specialist`
- **Role**: IT
- **Location**: `secure_area`
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
  - `it_specialist_info_1` MEDIUM: Information from IT Specialist
- **Actions Available**:
  - `it_specialist_action_1` LOW: Action performed by IT Specialist
  - `it_specialist_action_2` HIGH: Action performed by IT Specialist
- **Cover Story Options**:
  - `direct`: "Be direct and honest" -- Suspicious but may help if convinced
  - `lie`: "Use a false cover story" -- May believe or may see through it

## Roles & Tasks

### Hacker

**Tasks:**

1. **H1. 🔍 SEARCH** - Locate hidden console to bypass network.
   - *Search Items:* `item_4`
   - *Location:* `control_room`
   - *Prerequisites:* None (starting task)

2. **H2. 🔍 SEARCH** - Find secure server access point.
   - *Search Items:* `item_7`, `item_8`
   - *Location:* `secure_area`
   - *Prerequisites:*
      - Task `H1`

3. **H3. 💬 NPC_LLM** - Extract security protocols from IT specialist.
   - *NPC:* `it_specialist`
   - *Target Outcomes:* `it_specialist_info_1`
   - *Location:* `secure_area`
   - *Prerequisites:*
      - Task `H1`
      - Task `H2`

4. **H4. 🎮 lock_picking** - Hack the main vault's biometric scanner.
   - *Location:* `secure_area`
   - *Prerequisites:*
      - Outcome `it_specialist_info_1`
      - Task `H3`


### Lookout

**Tasks:**

1. **L1. 🎮 alarm_disable** - Disable exterior cameras stealthily.
   - *Location:* `entry_point`
   - *Prerequisites:* None (starting task)

2. **L2. 🎮 safe_cracking** - Redirect security feeds from main monitors.
   - *Location:* `control_room`
   - *Prerequisites:*
      - Task `L1`
      - Task `H1`

3. **L3. 🎮 fingerprint_matching** - Divert patrolling guards, clear hallway.
   - *Location:* `secure_area`
   - *Prerequisites:* None (starting task)

4. **L4. 💬 NPC_LLM** - Distract receptionist, buy hacker time.
   - *NPC:* `receptionist`
   - *Target Outcomes:* `receptionist_info_1`
   - *Location:* `control_room`
   - *Prerequisites:*
      - Task `H4`


