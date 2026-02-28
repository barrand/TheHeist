---
---
---
---
---
---
# Retrieve the 'Celestial Shard' from the Cinderbrook Museum's newly unveiled 'Cosmic Relics' exhibit before its public debut.

**ID**: `museum_heist`
**Scenario**: Retrieve the 'Celestial Shard' from the Cinderbrook Museum's newly unveiled 'Cosmic Relics' exhibit before its public debut.
**Selected Roles**: Hacker, Mastermind
**Player Count**: 2 players

## Objective
Retrieve the 'Celestial Shard' from the Cinderbrook Museum's newly unveiled 'Cosmic Relics' exhibit before its public debut.

## Locations

### Exterior
- **Whispering Alley Service Dock** (`service_dock`): Tucked away behind the grand museum, this grimy loading dock hums with the low thrum of industrial chillers and the scent of forgotten rain, an unsung entry point into the museum's underbelly.

### Interior
- **Curatorial & Archives Hub** (`admin_hub`): A bustling, labyrinthine administrative floor where curators' offices spill into dusty archives, filled with the hushed rustle of papers and the clatter of keyboards.
- **Digital Core Server Room** (`server_room`): The frigid heart of the museum's digital security, filled with the loud, rhythmic hum of countless servers and blinking lights reflecting off polished raised floor panels.
- **The Cosmic Relics Gallery** (`cosmic_gallery`): A dramatically lit, cavernous gallery where rare meteoric fragments and ancient astronomical instruments are displayed under reinforced glass, shrouded in an artificial twilight.
- **Orbital Pedestal Chamber** (`shard_pedestal`): The centerpiece of the gallery, a circular, heavily secured chamber housing the Celestial Shard on a rotating pedestal, bathed in a single, intense beam of light.

**Total Locations**: 5

## Items by Location

### Curatorial & Archives Hub
- **Curator's Digital Tablet** (`item_4`)
  - **Description**: Contains access schedules, inventory manifests, and potentially crucial staff login details.
  - **Visual**: A high-end, silver tablet with a cracked screen protector, displaying a complex floor plan.
  - **Hidden**: false

- **Archival Access Log** (`item_5`)
  - **Description**: A physical record book detailing who accessed what artifact and when.
  - **Visual**: A thick, leather-bound ledger, slightly dusty, with handwritten entries in neat cursive.
  - **Hidden**: false

### The Cosmic Relics Gallery
- **Reflective Display Shard** (`item_8`)
  - **Description**: A fragment of the gallery's unique display material, useful for diverting laser grids.
  - **Visual**: A small, irregular piece of dark, iridescent glass, reflecting light in a rainbow spectrum.
  - **Hidden**: false

### Digital Core Server Room
- **Redundant Power Cell** (`item_6`)
  - **Description**: A backup power unit for critical systems, surprisingly portable if disconnected.
  - **Visual**: A rectangular, heavy-duty battery pack with exposed wiring ports and a warning sticker.
  - **Hidden**: false

- **Server Room Schematics** (`item_7`)
  - **Description**: Detailed blueprints of the server room's layout, wiring, and cooling systems.
  - **Visual**: A rolled-up bundle of aged, blue-line architectural drawings, slightly frayed at the edges.
  - **Hidden**: true
  - **Unlock**:
    - Task `H1`

### Whispering Alley Service Dock
- **Rusty Maintenance Keycard** (`item_1`)
  - **Description**: Grants basic access to lower service areas, often found misplaced by staff.
  - **Visual**: A standard, grey plastic keycard, slightly scuffed, with a faded 'Maintenance' label.
  - **Hidden**: false

- **Empty Janitor's Cart** (`item_2`)
  - **Description**: A standard cleaning cart, surprisingly useful for discreetly moving equipment or personnel.
  - **Visual**: A utilitarian chrome-plated cart with yellow plastic bins, a mop bucket, and a 'Wet Floor' sign hanging off it.
  - **Hidden**: false

- **Overridden Security Bypass** (`item_3`)
  - **Description**: A small, custom-built device capable of temporarily jamming local security sensors.
  - **Visual**: A sleek, black, palm-sized device with a single blinking red LED and a retractable antenna.
  - **Hidden**: true
  - **Unlock**:
    - Task `MM3`

### Orbital Pedestal Chamber
- **Gravity Stabilizer Remote** (`item_9`)
  - **Description**: Controls the delicate anti-gravity field suspending the main exhibit.
  - **Visual**: A futuristic, ergonomic remote control with a glowing blue touchscreen interface and a single red override button.
  - **Hidden**: false

- **Temporal Anomaly Core** (`item_10`)
  - **Description**: The museum's most prized artifact, a pulsating sphere of unknown origin.
  - **Visual**: A softball-sized, obsidian-smooth sphere emitting a faint, purple-blue light, subtly vibrating.
  - **Hidden**: false

## NPCs

### manager - Arthur Finch
- **ID**: `manager`
- **Role**: manager
- **Location**: `admin_hub`
- **Age**: 58
- **Gender**: male
- **Ethnicity**: Caucasian
- **Clothing**: Slightly rumpled but expensive tweed jacket, a tie loosened at the collar, and sensible loafers.
- **Expression**: Harried, perpetually concerned, a slight furrow in his brow.
- **Attitude**: Stressed, authoritative but easily flustered under pressure, obsessed with protocol.
- **Details**: Constantly adjusts his spectacles, which are perched precariously on his nose.
- **Personality**: Arthur is a stickler for rules and order, a trait amplified by the immense pressure of the 'Cosmic Relics' exhibit's impending debut. He's overwhelmed by the last-minute preparations and the sheer value of the artifacts, making him both meticulous and prone to anxiety-induced forgetfulness when pushed.
- **Relationships**: He views the receptionist, Brenda, as a diligent but somewhat naive subordinate who needs constant supervision, often micromanaging her desk duties.
- **Story Context**: Arthur holds the key to critical security protocols and access information for the newly installed systems, making him a prime target for interrogation.
- **Information Known**:
  - `master_security_code_sequence` HIGH: The new master security code sequence for the 'Cosmic Relics' exhibit, changed just this morning, is "ALPHA-CENTAURI-7-GALAXY".
  - `pedestal_chamber_access` MEDIUM: The Orbital Pedestal Chamber requires dual-keycard authentication, with one keycard held by himself and the other by the lead curator (who is currently off-site).
  - `shard_transport_logs` LOW: He vaguely recalls that the initial transport logs for the Celestial Shard mentioned a specific handling team, "Gemini Logistics," but the details are in a secure digital folder on his office terminal.
- **Actions Available**:
  - `reveal_security_code` HIGH: Can be convinced to reveal the master security code sequence if under enough duress or given a convincing reason relating to urgent safety.
  - `grant_archives_access` MEDIUM: Could be persuaded to grant temporary, supervised access to the Curatorial & Archives Hub's restricted sections if an emergency or official-looking request is presented.
- **Cover Story Options**:
  - `security_inspector`: "I'm here for a final, unscheduled pre-debut security audit of the new systems." -- Arthur would be highly defensive and immediately try to demonstrate his compliance, but also visibly nervous about being scrutinized.
  - `exhibit_sponsor`: "I'm a representative from 'Starlight Corporations,' one of your key exhibit sponsors, here for a last-minute media walk-through." -- Arthur would be obsequious and eager to please, trying to facilitate any reasonable request to maintain good relations, but might still be wary of protocol breaches.
  - `federal_agent`: "I'm Agent Miller from the Federal Bureau, investigating a credible threat against the 'Cosmic Relics' exhibit." -- Arthur would be terrified and cooperative, but also extremely anxious and prone to panicking or attempting to verify credentials through official channels.

### receptionist - Brenda Hayes
- **ID**: `receptionist`
- **Role**: receptionist
- **Location**: `admin_hub`
- **Age**: 24
- **Gender**: female
- **Ethnicity**: African American
- **Clothing**: Smart, tailored museum uniform blazer, a crisp blouse, and comfortable, low heels.
- **Expression**: Bright and professional, but with an underlying weariness from the long hours.
- **Attitude**: Friendly and helpful on the surface, but easily overwhelmed and quite gossipy when comfortable.
- **Details**: Wears a small, intricate nebula-themed pendant, a gift from her sister.
- **Personality**: Brenda is generally cheerful and tries her best to be efficient, but she's also a bit of a people-pleaser and easily distracted by social interactions. She's new to the museum's high-stress environment and finds the manager's constant micromanagement irritating.
- **Relationships**: She finds Arthur, the manager, overbearing and a bit of a bore, often rolling her eyes when he's not looking. She secretly enjoys chatting with the night security guards because they're less demanding.
- **Story Context**: Brenda controls the physical access log and possesses knowledge of daily staff movements and basic security procedures, making her a gatekeeper for initial infiltration.
- **Information Known**:
  - `janitorial_schedule` HIGH: The night janitorial crew begins their rounds through the Curatorial & Archives Hub at precisely 11:30 PM, using the Whispering Alley Service Dock entrance.
  - `curator_absence` HIGH: The lead curator, Dr. Vivian Thorne, is away at a conference until tomorrow morning and holds one of the two keycards for the Orbital Pedestal Chamber.
  - `security_camera_blind_spot` MEDIUM: She's noticed a specific security camera in the main hall of the Curatorial & Archives Hub sometimes glitches and creates a momentary blind spot near the large fossil display, especially after a power flicker.
- **Actions Available**:
  - `create_distraction` MEDIUM: Can be convinced to create a minor distraction (e.g., call a colleague, go on a coffee run) if given a plausible, urgent-sounding reason.
  - `reveal_schedules` HIGH: Can be persuaded to reveal details about personnel schedules, including security and curatorial staff, if a friendly rapport is established.
- **Cover Story Options**:
  - `delivery_person`: "I'm here to deliver urgent, confidential exhibit materials from the 'Starlight Corporations' to Mr. Finch." -- Brenda would be helpful and direct the player, potentially offering to call Mr. Finch, but would insist on proper sign-off procedures.
  - `museum_donor`: "I'm Mrs. Caldwell, a significant museum donor, here for a private viewing of the new exhibit before the crowds." -- Brenda would be exceptionally polite and eager to impress, offering assistance and potentially bending minor rules to accommodate a VIP.
  - `tech_support`: "I'm from 'Nexus Systems,' here to perform a last-minute network diagnostic on the server room's connectivity." -- Brenda would be slightly confused as no appointment was logged, but would likely point them towards the Digital Core Server Room, perhaps attempting to verify with a supervisor first.

## Roles & Tasks

### Hacker

**Tasks:**

1. **H1. 🔍 SEARCH** - Find the hidden override panel for the chamber's security lockdown.
   - *Search Items:* `item_9`, `item_10`
   - *Location:* `shard_pedestal`
   - *Prerequisites:* None (starting task)

2. **H2. 🗣️ INFO_SHARE** - Share intelligence with the team
   - *Info:* Information about janitorial_schedule
   - *Location:* `cosmic_gallery`
   - *Prerequisites:*
      - Task `H1`
      - Outcome `janitorial_schedule`

3. **H3. 🗣️ INFO_SHARE** - Share intelligence with the team
   - *Info:* Information about pedestal_chamber_access
   - *Location:* `admin_hub`
   - *Prerequisites:*
      - Task `H2`

4. **H4. 🤝 HANDOFF** - Deliver the encrypted access key to the mastermind for system penetration.
   - *Handoff Item:* `item_7`
   - *Handoff To:* Mastermind
   - *Location:* `server_room`
   - *Prerequisites:*
      - Task `H3`

5. **H5. 🎮 card_swipe** - Neutralize the anti-gravity pedestal's security lock before the artifact floats away.
   - *Location:* `shard_pedestal`
   - *Prerequisites:*
      - Task `H4`


### Mastermind

**Tasks:**

1. **MM1. 💬 NPC_LLM** - Distract the receptionist to gain temporary access to restricted areas.
   - *NPC:* `receptionist`
   - *Target Outcomes:* `janitorial_schedule`, `curator_absence`
   - *Location:* `admin_hub`
   - *Prerequisites:* None (starting task)

2. **MM2. 🤝 HANDOFF** - Hand off to hacker
   - *Handoff Item:* `item_10`
   - *Handoff To:* Hacker
   - *Location:* `admin_hub`
   - *Prerequisites:*
      - Task `MM1`

3. **MM3. 🤝 HANDOFF** - Transfer the secured artifact to the escape team for extraction.
   - *Handoff Item:* `item_9`
   - *Handoff To:* Hacker
   - *Location:* `shard_pedestal`
   - *Prerequisites:*
      - Task `MM2`

4. **MM4. 🔍 SEARCH** - Locate and retrieve the server room schematics hidden amongst old backups.
   - *Search Items:* `item_6`, `item_7`
   - *Location:* `server_room`
   - *Prerequisites:*
      - Task `MM3`


