---
# Bypass the museum's cutting-edge security to liberate the legendary 'Eye of Amun-Ra' from its vault.

**ID**: `museum_heist`
**Scenario**: Bypass the museum's cutting-edge security to liberate the legendary 'Eye of Amun-Ra' from its vault.
**Selected Roles**: Hacker, Mastermind
**Player Count**: 2 players

## Objective
Bypass the museum's cutting-edge security to liberate the legendary 'Eye of Amun-Ra' from its vault.

## Locations

### Exterior/Interior
- **The Nocturnal Loading Bay** (`loading_bay`): A sprawling, dimly lit concrete cavern at the rear of the museum, where deliveries hum throughout the night, thick with the scent of cardboard and exhaust fumes.

### Interior
- **The Labyrinthine Staff Corridors** (`staff_corridors`): A sterile, echoing network of cream-colored hallways and locked utility doors, leading deeper into the museum's unseen operational heart.
- **Curatorial Offices Annex** (`curatorial_annex`): A hushed wing of private offices and conservation labs, where the museum's intellectual elite meticulously prepare exhibits behind frosted glass.
- **The Pulsating Server Room** (`server_room`): A high-security, climate-controlled chamber pulsating with the hum of servers and the frantic blink of indicator lights, the digital fortress of the museum's network.
- **The Pharaoh's Inner Vault** (`treasure_vault`): The museum's ultimate safeguard, a multi-layered steel vault bathed in soft, laser-grid light, protecting the mythical 'Eye of Amun-Ra' on its illuminated plinth.

**Total Locations**: 5

## Items by Location

### Curatorial Offices Annex
- **Curator's Data Stick** (`item_6`)
  - **Description**: A USB drive containing partial security schedules and email correspondence, hinting at vault access codes.
  - **Visual**: A sleek, metallic USB flash drive with a small, glowing blue indicator light, slightly warm to the touch.
  - **Hidden**: false

- **Scrawled Memo** (`item_7`)
  - **Description**: A hastily scrawled note containing a fragment of the vault's access sequence, hidden in plain sight.
  - **Visual**: A small, torn piece of yellow legal pad paper with a series of numbers and symbols scribbled in pencil, tucked under a blotter.
  - **Hidden**: true
  - **Unlock**:
    - Task `H5`

### The Nocturnal Loading Bay
- **Utility Forklift Key** (`item_1`)
  - **Description**: A standard key for operating the museum's industrial forklifts, essential for moving heavy crates.
  - **Visual**: A simple, tarnished metal key with a large, rectangular head, hanging on a worn red plastic tag.
  - **Hidden**: false

- **Museum Guard Vest** (`item_2`)
  - **Description**: A reflective vest worn by museum staff, granting a brief, low-profile disguise in authorized areas.
  - **Visual**: A bright yellow, slightly worn reflective safety vest with 'MUSEUM STAFF' printed on the back in black letters.
  - **Hidden**: false

- **Smuggled Manifest** (`item_3`)
  - **Description**: A hidden shipping manifest detailing incoming and outgoing crates, revealing crucial vulnerabilities and timings.
  - **Visual**: A crumpled, coffee-stained paper manifest tucked beneath a stack of old pallets, with handwritten annotations.
  - **Hidden**: true
  - **Unlock**:
    - Task `MM2`

### The Pulsating Server Room
- **Server Room Interface** (`item_8`)
  - **Description**: A custom-built device for bypassing network authentication and granting backdoor access to the museum's systems.
  - **Visual**: A compact, black electronic device with several blinking LED lights and a tangle of specialized ethernet cables.
  - **Hidden**: false

### The Labyrinthine Staff Corridors
- **Janitor's Keycard** (`item_4`)
  - **Description**: A low-level access card, granting entry to service tunnels and less-restricted staff zones.
  - **Visual**: A generic white plastic ID card with a faded photo of a middle-aged man, clipped to a retractable lanyard.
  - **Hidden**: false

- **Obscure Floor Plans** (`item_5`)
  - **Description**: Outdated but still useful blueprints of the museum's lower levels, revealing forgotten passages and maintenance shafts.
  - **Visual**: Large, rolled-up parchment blueprints, yellowed with age, showing intricate ventilation shafts and utility lines.
  - **Hidden**: false

### The Pharaoh's Inner Vault
- **The Eye of Osiris** (`item_9`)
  - **Description**: A legendary sapphire, rumored to grant foresight, mounted in an ancient golden hawk effigy. The primary target.
  - **Visual**: A fist-sized, deep blue sapphire, perfectly cut, set within the eye socket of an ornate, solid gold hawk statue with intricate hieroglyphs.
  - **Hidden**: false

- **The Scroll of Thoth** (`item_10`)
  - **Description**: An ancient papyrus scroll believed to contain forgotten knowledge. A valuable secondary target, highly fragile.
  - **Visual**: A brittle, rolled papyrus scroll, sealed with an ancient clay stamp depicting an ibis-headed deity, radiating an aura of antiquity.
  - **Hidden**: false

## NPCs

### manager - Arthur Finch
- **ID**: `manager`
- **Role**: manager
- **Location**: `curatorial_annex`
- **Age**: 55
- **Gender**: male
- **Ethnicity**: Caucasian
- **Clothing**: A slightly rumpled grey suit, loosened tie, and spectacles perched on his nose.
- **Expression**: Harried, with a perpetual slight frown etched between his brows.
- **Attitude**: Overworked and stressed, but deeply committed to the museum's reputation and security.
- **Details**: A well-used pen perpetually tucked behind his right ear.
- **Personality**: Arthur is a man drowning in administrative duties, always on the verge of a minor panic attack about budgets and deadlines. He prides himself on the museum's impeccable record, making him extra vigilant tonight due to the 'Eye of Amun-Ra' exhibit, but also easily flustered by unexpected disruptions.
- **Relationships**: He sees the 'receptionist' Chloe Davies as generally competent but often distracted, a necessary cog in the administrative machine he oversees.
- **Story Context**: He is the primary gatekeeper of administrative access and critical digital information within the Curatorial Offices Annex.
- **Information Known**:
  - `vault_access_protocol_change` HIGH: The vault's digital access protocol was updated last week, now requiring dual-factor authentication for anyone accessing it, even senior staff.
  - `server_room_keycard_override` MEDIUM: He has a master keycard override for the server room, but it requires a biometric scan from the Head of Security to activate.
  - `curatorial_office_layout` HIGH: He knows the exact layout of the Curatorial Offices Annex, including a rarely used maintenance duct leading towards the staff corridors.
- **Actions Available**:
  - `reveal_network_credentials` HIGH: If convinced that IT is performing an urgent system check, he might reveal his network credentials for 'troubleshooting'.
- **Cover Story Options**:
  - `it_support_specialist`: "I'm a new IT support specialist here to perform an urgent, unscheduled system diagnostic." -- He'd be annoyed by the lack of prior notice but would likely cooperate if the tone is authoritative and emphasizes security, demanding to see official ID.
  - `archivist_consultant`: "I'm an external archivist consultant here for a late-night review of the 'Eye of Amun-Ra' exhibit's documentation." -- He would demand official paperwork and an appointment, highly suspicious of unscheduled visits and unauthorized access to sensitive documents.
  - `hvac_technician`: "I'm the lead HVAC technician, responding to an emergency temperature fluctuation report from the server room." -- He would be immediately concerned about the server room and direct the player to relevant areas, but would want to verify the report and request proof of identity.

### receptionist - Chloe Davies
- **ID**: `receptionist`
- **Role**: receptionist
- **Location**: `curatorial_annex`
- **Age**: 28
- **Gender**: female
- **Ethnicity**: Mixed-race
- **Clothing**: A smart but comfortable navy blouse and tailored trousers, with a museum-branded lanyard.
- **Expression**: Generally pleasant, but a little bored and occasionally checking her phone under the desk.
- **Attitude**: Friendly and helpful, but also a stickler for rules when she's paying attention.
- **Details**: A small, intricate tattoo of a hieroglyph on her left wrist, peeking out from her sleeve.
- **Personality**: Chloe is usually cheerful and efficient, but tonight she's a bit bored and restless, wishing her shift was over. She enjoys a good chat to pass the time, but she's also acutely aware of her responsibilities, especially with the high-profile exhibit currently on display.
- **Relationships**: She views 'manager' Arthur Finch as a typical, perpetually stressed boss, a bit of a stick-in-the-mud but generally fair.
- **Story Context**: She controls immediate access to certain restricted staff areas and is a valuable source of real-time information about staff movements.
- **Information Known**:
  - `staff_rotation_schedule` HIGH: She knows the current night shift security rotation schedule for the staff corridors, including when specific guards take their breaks and patrol routes.
  - `delivery_bay_code_hearsay` LOW: She overheard the new temporary code for the Nocturnal Loading Bay being discussed earlier, though she can't recall it perfectly, only that it changed from the usual.
  - `curatorial_keycard_levels` MEDIUM: She knows that only senior curatorial staff and specific security personnel have level-4 keycard access to the Pharaoh's Inner Vault approaches.
- **Actions Available**:
  - `divert_attention` HIGH: She can be easily engaged in conversation, making her less attentive to CCTV monitors or peripheral activity for a short period.
  - `grant_temporary_access` MEDIUM: She might grant temporary access to a restricted area (e.g., a specific office) if a convincing, low-risk emergency is fabricated, provided it doesn't involve the vault itself.
- **Cover Story Options**:
  - `delivery_driver`: "I'm a late-night delivery driver with a special package for the 'Eye of Amun-Ra' curator." -- She'd be slightly annoyed by the late hour but would direct them to the Nocturnal Loading Bay or attempt to contact the curator, asking for a delivery manifest.
  - `museum_volunteer`: "I'm a new night-shift volunteer, reporting for my first shift to assist with exhibit setup." -- She'd be friendly and helpful, offering directions and basic instructions, but would verify their name on a roster and ask about their assigned tasks.
  - `visiting_scholar`: "I'm a visiting scholar here to collect some research materials I left in one of the curatorial offices." -- She would ask for identification and an appointment time, reluctant to grant unscheduled access to private offices without proper authorization.

## Roles & Tasks

### Hacker

**Tasks:**

1. **H1. 🔍 SEARCH** - Scan the vault's security systems for overlooked vulnerabilities and potential digital backdoors.
   - *Search Items:* `item_9`, `item_10`
   - *Location:* `treasure_vault`
   - *Prerequisites:* None (starting task)

2. **H2. 🤝 RECEIVE_HANDOFF** - Receive intelligence about the delivery bay code from the Mastermind.
   - *Receive Outcomes:* `delivery_bay_code_hearsay`
   - *Handoff From:* Mastermind
   - *Location:* `curatorial_annex`
   - *Prerequisites:*
      - Task `MM2`

3. **H3. 🤝 RECEIVE_HANDOFF** - Receive the staff rotation schedule from the Mastermind.
   - *Receive Outcomes:* `staff_rotation_schedule`
   - *Handoff From:* Mastermind
   - *Location:* `curatorial_annex`
   - *Prerequisites:*
      - Task `H2`

4. **H4. 🤝 RECEIVE_HANDOFF** - Receive the obscure floor plans from the Mastermind.
   - *Receive Item:* `item_5`
   - *Handoff From:* Mastermind
   - *Location:* `curatorial_annex`
   - *Prerequisites:*
      - Task `MM4`

5. **H5. 🎮 card_swipe** - Execute the final digital sequence to disarm the vault's laser grid and pressure plate sensors.
   - *Location:* `treasure_vault`
   - *Prerequisites:*
      - Task `H4`
      - Task `MM5`

6. **H6. 📦 GET_ITEM** - Acquire the Eye of Amun-Ra and the Scroll of Thoth from the vault.
   - *Items:* `item_9`, `item_10`
   - *Location:* `treasure_vault`
   - *Prerequisites:*
      - Task `H5`

7. **H7. 🤝 HANDOFF** - Transmit the Eye of Amun-Ra to the Mastermind for extraction.
   - *Handoff Item:* `item_9`
   - *Handoff To:* Mastermind
   - *Location:* `treasure_vault`
   - *Prerequisites:*
      - Task `H6`

8. **H8. 🔍 SEARCH** - Wipe all digital traces from the museum's servers and disable external tracking systems for a clean getaway.
   - *Location:* `loading_bay`
   - *Prerequisites:*
      - Task `H7`


### Mastermind

**Tasks:**

1. **MM1. 🎮 timed_dialogue_choices** - Engage the receptionist in casual conversation to divert attention and gather intel on staff movements.
   - *Minigame:* `timed_dialogue_choices`
   - *Location:* `curatorial_annex`
   - *Prerequisites:* None (starting task)

2. **MM2. 🤝 HANDOFF** - Hand off the acquired intelligence to the Hacker.
   - *Handoff Outcomes:* `staff_rotation_schedule`, `delivery_bay_code_hearsay`
   - *Handoff To:* Hacker
   - *Location:* `curatorial_annex`
   - *Prerequisites:*
      - Task `MM1`

3. **MM3. 🔍 SEARCH** - Locate the obscure floor plans in the staff corridors.
   - *Search Items:* `item_5`
   - *Location:* `staff_corridors`
   - *Prerequisites:*
      - Task `MM2`

4. **MM4. 🤝 HANDOFF** - Transmit the obscure floor plans to the Hacker.
   - *Handoff Item:* `item_5`
   - *Handoff To:* Hacker
   - *Location:* `curatorial_annex`
   - *Prerequisites:*
      - Task `MM3`

5. **MM5. 🔍 SEARCH** - Discreetly search the curator's office for the hidden memo containing critical vault fragments.
   - *Search Items:* `item_6`, `item_7`
   - *Location:* `curatorial_annex`
   - *Prerequisites:*
      - Task `MM4`

6. **MM6. 🤝 RECEIVE_HANDOFF** - Receive the Eye of Amun-Ra from the Hacker.
   - *Receive Item:* `item_9`
   - *Handoff From:* Hacker
   - *Location:* `treasure_vault`
   - *Prerequisites:*
      - Task `H7`

7. **MM7. 🔍 SEARCH** - Secure the getaway vehicle at the loading bay, ensuring a clear path for a swift extraction.
   - *Location:* `loading_bay`
   - *Prerequisites:*
      - Task `MM6`
---