---
---
---
---
---
---
# Steal the priceless artifact from the museum vault

**ID**: `museum_heist`
**Scenario**: Steal the priceless artifact from the museum vault
**Selected Roles**: Hacker, Mastermind
**Player Count**: 2 players

## Objective
Steal the priceless artifact from the museum vault

## Locations

### Exterior
- **Entry Point** (`entry_point`): Initial access point

### Interior
- **Main Area** (`main_area`): Primary operational area
- **Control Room** (`control_room`): Security and systems hub
- **Secure Area** (`secure_area`): Restricted access zone
- **Target Room** (`target_room`): Final objective location

**Total Locations**: 5

## Items by Location

### Control Room
- **Security Console Access Card** (`item_2`)
  - **Description**: A laminated card granting physical access to the main security console in the control room.
  - **Visual**: A glossy, black RFID access card with a silver chip, embossed with the museum's logo and 'AUTHORIZED PERSONNEL ONLY'.
  - **Hidden**: false

- **Surveillance System Override Key** (`item_3`)
  - **Description**: A specialized USB key containing a firmware patch to temporarily disable surveillance cameras.
  - **Visual**: A small, metallic USB drive with a unique, glowing red LED indicator and a stylized 'O' symbol engraved on its casing.
  - **Hidden**: false

### Entry Point
- **Visitor Logbook** (`item_4`)
  - **Description**: A physical logbook detailing recent visitor entries, sometimes revealing staff patterns.
  - **Visual**: A worn, leather-bound register book open to a page with handwritten entries, resting on a small, ornate reception desk.
  - **Hidden**: false

### Main Area
- **The Curator's Tablet** (`item_1`)
  - **Description**: A high-tech tablet displaying the museum's floor plan and staff schedules. Crucial for navigation.
  - **Visual**: Sleek, black tablet with a glowing blue screen, displaying a detailed museum map, held in a polished display stand.
  - **Hidden**: false

### Secure Area
- **Laser Grid Schematic** (`item_5`)
  - **Description**: A detailed blueprint of the laser grid's layout and pressure plate triggers within the secure area.
  - **Visual**: A rolled-up architectural blueprint, partially unfurled to show a complex diagram of red laser lines and floor sensors.
  - **Hidden**: false

- **Thermal Camera Jammer** (`item_6`)
  - **Description**: A compact device emitting electromagnetic interference to blind thermal imaging systems.
  - **Visual**: A small, rectangular metallic device with a retractable antenna and a blinking green light, designed for covert operation.
  - **Hidden**: false

- **Emergency Power Conduit Map** (`item_7`)
  - **Description**: A hidden map showing the emergency power lines and their vulnerabilities in the secure area.
  - **Visual**: A folded, aged paper map tucked inside a maintenance panel, depicting intricate electrical wiring diagrams.
  - **Hidden**: true
  - **Unlock**:
    - Task `H2`

### Target Room
- **Vault Combination Cipher** (`item_8`)
  - **Description**: A cryptic note containing a partial combination to the main vault, requiring deciphering.
  - **Visual**: A small, crumpled piece of parchment with seemingly random numbers and symbols, tucked under a loose floorboard.
  - **Hidden**: true
  - **Unlock**:
    - Task `MM2`

- **Gemstone Authenticator** (`item_9`)
  - **Description**: A specialized jeweler's loupe for quickly identifying genuine artifacts within the target room.
  - **Visual**: A polished brass jeweler's loupe with multiple lenses, reflecting a faint glint, hidden behind a display case.
  - **Hidden**: true
  - **Unlock**:
    - Task `MM6`

- **The Serpent's Eye Diamond** (`item_10`)
  - **Description**: A legendary, flawless blue diamond, the ultimate prize of the heist, gleaming intensely.
  - **Visual**: A magnificent, large blue diamond, cut into an intricate serpent's eye shape, shimmering intensely within a reinforced glass display.
  - **Hidden**: true
  - **Unlock**:
    - Task `MM3`

## NPCs

### IT - Lena Petrova
- **ID**: `it_specialist`
- **Role**: IT
- **Location**: `secure_area`
- **Age**: 32
- **Gender**: female
- **Ethnicity**: Eastern European
- **Clothing**: A slightly rumpled band t-shirt under a black hoodie, cargo pants, and worn sneakers.
- **Expression**: Tired, a bit bored, but focused on her dual monitors.
- **Attitude**: Cynical, slightly overwhelmed, but competent.
- **Details**: Constantly sips from a large, generic coffee mug.
- **Personality**: Lena is usually reserved and prefers the company of her systems to people. Tonight, she's particularly grumpy and stressed due to a recent system update that's causing minor glitches, making her short-tempered with interruptions. She just wants to get through her shift and go home.
- **Relationships**: She has a distant, professional relationship with the manager, mostly dealing with their IT requests. She occasionally exchanges curt nods with the security_guard during her rounds but finds them generally unobservant.
- **Story Context**: She is the primary gatekeeper for the museum's digital security infrastructure this evening.
- **Information Known**:
  - `network_admin_credentials_known` HIGH: Lena knows the current admin credentials for the museum's internal security network, as she just updated them.
  - `server_room_layout_known` HIGH: She designed the current server room layout and knows the exact location of the main security server in the Secure Area, including its physical access protocols.
  - `security_system_vulnerability_known` MEDIUM: She's aware of a minor, undocumented back-door access point in the legacy surveillance system software, which she uses for quick troubleshooting but hasn't patched yet.
- **Actions Available**:
  - `grant_remote_access` MEDIUM: Lena can be persuaded to grant temporary, remote administrator access to the museum's security network, citing an 'emergency patch' or 'remote diagnostics'.
- **Cover Story Options**:
  - `tech_support_auditor`: "I'm a third-party IT auditor here to verify the recent security update's integrity." -- Lena would be initially wary and defensive, but professionalism might compel her to cooperate, albeit grudgingly.
  - `deliver_late_food`: "Just delivering your late-night order, Lena, from 'Byte Bites'?" -- She'd be confused, stating she didn't order anything, but might lower her guard slightly if offered free food.
  - `museum_archivist_helper`: "I'm a new assistant archivist, tasked with cross-referencing digital records in the Secure Area." -- Lena would be highly suspicious, as archivists don't typically access her domain without prior notice and specific authorization.

### manager - Arthur Finch
- **ID**: `manager`
- **Role**: manager
- **Location**: `main_area`
- **Age**: 58
- **Gender**: male
- **Ethnicity**: Caucasian
- **Clothing**: A well-tailored but slightly worn suit, a tie loosened around his neck.
- **Expression**: Harried and anxious, frequently checking his watch.
- **Attitude**: Overwhelmed, prone to minor panic, but tries to maintain a facade of control.
- **Details**: Carries a heavily organized, slightly overflowing binder under his arm.
- **Personality**: Arthur is a meticulous but easily flustered man, prone to anxiety about the museum's reputation and security. Tonight, he's particularly on edge due to a last-minute audit scheduled for tomorrow morning, making him stressed and eager to ensure everything is perfect. He's trying his best to look calm, but his nerves are showing.
- **Relationships**: He often relies on the it_specialist for technical issues, finding her indispensable but also a bit intimidating. He sees the security_guard as a necessary but often slow extension of his authority, frequently giving them instructions.
- **Story Context**: Arthur is the most senior staff member on-site and holds keys to several critical areas, but his attention is divided.
- **Information Known**:
  - `emergency_power_panel_location_known` HIGH: Arthur knows the exact location of the emergency power panel in the basement, as he had to oversee its last inspection.
  - `master_keycard_schedule_known` MEDIUM: He knows the general schedule for when the master keycard for the Secure Area is typically stored in the office safe, usually after closing rounds.
  - `private_collection_alarm_code_known` LOW: He vaguely remembers a simplified alarm override code for the *private* collection within the Target Room, used for quick curator access, but he's not entirely sure if it's still active.
- **Actions Available**:
  - `grant_restricted_access_temporary` MEDIUM: Arthur can be convinced to grant temporary access to restricted areas (e.g., the Control Room or Secure Area entrance) under the guise of urgent pre-audit checks.
  - `reveal_emergency_power_location` MEDIUM: Arthur can be persuaded to reveal the location of the emergency power panel, especially if convinced there's an urgent, low-priority issue he can delegate.
- **Cover Story Options**:
  - `audit_inspector`: "Good evening, Mr. Finch. I'm an external auditor here for the early pre-check of tomorrow's museum audit." -- Arthur would be instantly cooperative but highly stressed, eager to please and deflect potential issues.
  - `artifact_courier`: "I'm the courier for the late-arriving 'Lunar Shard' exhibit, Mr. Finch, need to get it secured." -- He'd be confused and suspicious, as no such delivery is scheduled, but he might be distracted by the perceived logistical error.
  - `charity_gala_organizer`: "Hello, Mr. Finch. I'm organizing the upcoming charity gala and need a quick walkthrough of the event spaces." -- He'd be polite and professionally engaged, viewing it as a potential PR opportunity, but would stick to public areas unless convinced otherwise.

### guard - Gary 'Mac' McMillan
- **ID**: `security_guard`
- **Role**: guard
- **Location**: `main_area`
- **Age**: 48
- **Gender**: male
- **Ethnicity**: Caucasian
- **Clothing**: Standard, slightly too-tight museum security uniform, polished shoes.
- **Expression**: Alert but easily bored, trying to appear diligent.
- **Attitude**: Professional on the surface, but a bit jaded and looking for distraction.
- **Details**: Fiddles with his walkie-talkie, occasionally adjusting his earpiece.
- **Personality**: Gary is a seasoned but somewhat complacent security guard. He takes his job seriously enough not to cause trouble, but he's also easily distracted by conversation or anything that breaks the monotony of his patrol. Tonight, he's counting down the hours until his shift ends, making him a bit more susceptible to diversion.
- **Relationships**: He has a respectful, if slightly distant, relationship with the manager, often receiving instructions he sometimes finds tedious. He barely interacts with the it_specialist, seeing her as 'the techie'.
- **Story Context**: Gary is a primary visible deterrent and patrol presence in the Main Area, controlling the flow of information and access.
- **Information Known**:
  - `patrol_route_and_timing_known` HIGH: Gary knows his exact patrol route and the approximate timing of each leg through the Main Area, as it's his standard shift.
  - `camera_blind_spots_known` MEDIUM: He's vaguely aware of a few minor camera blind spots near the main entrance due to recent exhibit changes, but he doesn't consider them critical.
  - `control_room_access_code_known` LOW: He knows the basic numeric code to the Control Room, which is shared among all guards for emergencies, but it changes weekly, and he's not sure if it's been updated yet.
- **Actions Available**:
  - `divert_patrol_route` MEDIUM: Gary can be engaged in conversation or led on a false lead, causing him to deviate from his standard patrol route for a short period.
  - `disable_camera_temporarily` MEDIUM: Gary can be convinced to temporarily disable or 're-angle' a specific surveillance camera, believing it's due to a faulty sensor or a temporary 'no-look' zone for a sensitive delivery.
- **Cover Story Options**:
  - `late_visitor`: "Oh my goodness, I'm so sorry, I must have lost track of time admiring the exhibits! Am I in terrible trouble?" -- Gary would be annoyed but bound by protocol, escorting the 'visitor' out while keeping a close eye.
  - `maintenance_crew`: "Evening, officer. Just here to check a flickering light in the west wing, part of the overnight maintenance run." -- He'd be initially suspicious, as he wasn't informed, but might be convinced with a credible-looking uniform or work order.
  - `local_police_liaison`: "Officer McMillan, I'm Detective Reynolds, city liaison. Just following up on a minor incident report from last week." -- Gary would become more formal and respectful, feeling obligated to cooperate with a perceived higher authority, potentially diverting his attention.

## Roles & Tasks

### Hacker

**Tasks:**

1. **H1. 🎮 cipher_wheel_alignment** - Bypass the laser grid's defense systems using a complex remote override minigame.
   - *Location:* `secure_area`
   - *Prerequisites:* None (starting task)

2. **H2. 🗣️ INFO_SHARE** - Share critical security vulnerabilities and system schematics with the Mastermind.
   - *Info:* Information about manager_info_1
   - *Location:* `secure_area`
   - *Prerequisites:*
      - Task `H1`

3. **H3. 🗣️ INFO_SHARE** - Share intelligence with the team
   - *Info:* Information about emergency_power_panel_location_known
   - *Location:* `main_area`
   - *Prerequisites:*
      - Task `H2`
      - Outcome `emergency_power_panel_location_known`


### Mastermind

**Tasks:**

1. **MM1. 💬 NPC_LLM** - Distract the museum manager to gain temporary access to restricted areas.
   - *NPC:* `manager`
   - *Target Outcomes:* `emergency_power_panel_location_known`, `master_keycard_schedule_known`
   - *Location:* `main_area`
   - *Prerequisites:* None (starting task)

2. **MM2. 🔍 SEARCH** - Search the entry point for hidden security bypass codes or keycards.
   - *Search Items:* `item_4`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `MM1`

3. **MM3. 🤝 HANDOFF** - Hand off to hacker
   - *Handoff Item:* `item_4`
   - *Handoff To:* Hacker
   - *Location:* `main_area`
   - *Prerequisites:*
      - Task `MM2`

4. **MM4. 💬 NPC_LLM** - Engage the security guard in conversation to divert their patrol route.
   - *NPC:* `security_guard`
   - *Target Outcomes:* `patrol_route_and_timing_known`, `camera_blind_spots_known`
   - *Location:* `main_area`
   - *Prerequisites:*
      - Task `MM3`

5. **MM5. 🤝 HANDOFF** - Hand off to hacker
   - *Handoff Item:* `item_1`
   - *Handoff To:* Hacker
   - *Location:* `main_area`
   - *Prerequisites:*
      - Task `MM4`

6. **MM6. 🤝 HANDOFF** - Hand off to hacker
   - *Handoff Item:* `item_6`
   - *Handoff To:* Hacker
   - *Location:* `secure_area`
   - *Prerequisites:*
      - Task `MM5`


