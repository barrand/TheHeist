---
---
---
---
---
---
# Steal the priceless artifact from the museum vault

**ID**: `museum_heist`
**Scenario**: Steal the priceless artifact from the museum vault
**Selected Roles**: Cat Burglar, Fence
**Player Count**: 2 players

## Objective
Steal the priceless artifact from the museum vault

## Locations

### Exterior
- **Entry Point** (`entry_point`): Initial access point

### Interior
- **Secure Area** (`secure_area`): Restricted access zone
- **Target Room** (`target_room`): Final objective location
- **Main Area** (`main_area`): Primary operational area
- **Control Room** (`control_room`): Security and systems hub

**Total Locations**: 5

## Items by Location

### Control Room
- **Server Rack Access Card** (`item_7`)
  - **Description**: A high-level access card for the museum's main server racks, granting system entry for maintenance.
  - **Visual**: A pristine, silver-grey RFID card with a holographic museum logo and a magnetic strip on the back.
  - **Hidden**: false

- **Emergency System Override Dongle** (`item_8`)
  - **Description**: A crucial USB dongle containing the museum's failsafe system override protocols, hidden for emergencies.
  - **Visual**: A standard-looking USB drive, but with a tiny, complex circuit board visible through a clear casing section.
  - **Hidden**: true
  - **Unlock**:
    - Task `F3`

### Entry Point
- **Janitor's Master Key** (`item_1`)
  - **Description**: A worn, multi-toothed brass key capable of opening most non-secure service doors throughout the museum.
  - **Visual**: An old, tarnished brass master key with many unique cuts, tied with a simple, frayed string.
  - **Hidden**: false

- **Staff ID Badge (Expired)** (`item_2`)
  - **Description**: An old, laminated staff ID badge for a former employee, potentially useful for bluffing or minor access.
  - **Visual**: A faded plastic ID card with an outdated photo, a locket clip attached, slightly scuffed.
  - **Hidden**: false

### Main Area
- **Museum Floorplan (Annotated)** (`item_6`)
  - **Description**: A detailed floorplan of the museum, discreetly marked with security patrol routes and camera blind spots.
  - **Visual**: A folded blueprint-style map, worn at the creases, with faint pencil annotations and circles.
  - **Hidden**: false

### Secure Area
- **Thermal Optic Disrupter** (`item_3`)
  - **Description**: A small, advanced device emitting a focused heat signature to temporarily blind infrared sensors and cameras.
  - **Visual**: A sleek, black, handheld gadget with a prominent red lens and a small, pulsing indicator light.
  - **Hidden**: false

### Target Room
- **Display Case Vibrational Nullifier** (`item_4`)
  - **Description**: A precision tool designed to temporarily dampen vibrations, allowing silent removal of artifacts from sensitive displays.
  - **Visual**: A compact, metallic cylinder with a soft rubber base and a small, glowing digital readout.
  - **Hidden**: false

- **Archivist's UV Penlight** (`item_5`)
  - **Description**: A specialized UV penlight used by archivists to reveal hidden watermarks, security features, or invisible ink.
  - **Visual**: A slender, dark metal pen with a subtle purple glow when activated, resembling a high-end fountain pen.
  - **Hidden**: false

## NPCs

### curator - Dr. Evelyn Reed
- **ID**: `curator`
- **Role**: curator
- **Location**: `entry_point`
- **Age**: 58
- **Gender**: female
- **Ethnicity**: Caucasian
- **Clothing**: Elegant, slightly rumpled tweed jacket over a silk blouse, with sensible but expensive low heels.
- **Expression**: Frazzled but attempting to maintain an air of intellectual composure.
- **Attitude**: Stressed, intellectual, slightly aloof, easily absorbed by academic details.
- **Details**: Wears reading glasses perched on her nose, constantly adjusting them or pushing them up her forehead.
- **Personality**: Dr. Reed is deeply passionate about the museum's collection, especially the priceless artifact. She's currently on edge, overwhelmed by the impending exhibition opening and a sudden, unexpected internal audit. She prides herself on her meticulousness but is stretched thin and easily distracted by intellectual discourse.
- **Relationships**: She views Officer Miller, the security guard, as a necessary but often cumbersome part of her work, frequently annoyed by what she perceives as his 'lack of appreciation for true artistry.'
- **Story Context**: She is the primary authority on the artifact and its security protocols, currently overseeing last-minute preparations for its public unveiling tomorrow.
- **Information Known**:
  - `vault_timer_override_code` HIGH: Dr. Reed knows the emergency vault timer override code (7-3-1-9-ALPHA), which can temporarily disable the timed lock for 10 minutes, but it flags an alert to central security.
  - `artifact_transport_route` MEDIUM: She recently signed off on the internal transport manifest outlining the artifact's exact route from the vault to the display case tomorrow morning, including a 15-minute window when it's unsecured.
  - `secure_archives_layout` HIGH: Dr. Reed can describe the layout of the secure archives adjacent to the vault, including a seldom-used service corridor entrance hidden behind a large tapestry.
- **Actions Available**:
  - `distract_curator_conversation` HIGH: If engaged in a deep academic discussion about the artifact's provenance or historical context, she will become completely engrossed, diverting her attention from her immediate surroundings for up to 15 minutes.
  - `access_secure_archives` MEDIUM: If convinced of an urgent, legitimate need (e.g., 'a historical text needed for tomorrow's exhibition'), she might temporarily grant access to the secure archives, but only under her direct supervision.
- **Cover Story Options**:
  - `academic_colleague`: "I'm Professor Davies from the University of London, here to consult on the upcoming exhibition." -- Dr. Reed would immediately be drawn into academic discussion, eager to show off her knowledge and the museum's collection, becoming less aware of her surroundings.
  - `museum_donor`: "I'm Mr. Sterling, representing the Sterling Foundation. We're considering a significant donation to your next acquisition." -- She would be professionally polite but wary, trying to gauge their true intentions and the seriousness of their offer while subtly promoting the museum's needs.
  - `exhibition_logistics_coordinator`: "I'm Sarah, from the events team. Just doing a final walkthrough for tomorrow's opening." -- She would be terse and stressed, demanding specific details and proof, as she's already overwhelmed with logistics, making her harder to distract.

### guard - Officer Ben Miller
- **ID**: `security_guard`
- **Role**: guard
- **Location**: `entry_point`
- **Age**: 45
- **Gender**: male
- **Ethnicity**: African American
- **Clothing**: Standard museum security uniform, slightly too tight around the shoulders, with polished boots.
- **Expression**: Alert, slightly bored, trying to look busy and important.
- **Attitude**: Diligent, by-the-book, a bit jaded but proud of his work.
- **Details**: Carries a well-worn, heavy-duty flashlight clipped to his belt, which he occasionally fiddles with or shines into dark corners.
- **Personality**: Officer Miller takes his job seriously, but the routine of museum security can be mind-numbingly dull. He's proud of his service record and adheres strictly to protocol, especially after a recent internal memo about heightened security. He dislikes unexpected disruptions but will respond immediately to anything he perceives as a legitimate threat or emergency.
- **Relationships**: He views Dr. Reed as a brilliant but impractical academic, often frustrated by her disregard for security procedures when focused on her 'precious artifacts.'
- **Story Context**: He is one of the primary guards responsible for the Entry Point, maintaining vigilance and enforcing access protocols throughout the night.
- **Information Known**:
  - `patrol_route_schedule` HIGH: Officer Miller adheres to a strict 15-minute patrol schedule of the Entry Point and Main Area, with specific checkpoints he must log using his handheld device.
  - `control_room_access_code` MEDIUM: He knows the daily changing numerical access code (currently 8-4-2-1) for the Control Room, but it's only valid for authorized personnel with an ID swipe and biometric scan.
  - `main_area_camera_blind_spot` LOW: He vaguely remembers a small blind spot in the Main Area's camera coverage near the ancient armory display, but isn't sure of its exact location or whether it's been patched.
- **Actions Available**:
  - `investigate_false_alarm` HIGH: If a credible and urgent false alarm (e.g., 'a water leak in the archives,' 'a strange noise from the East Wing') is reported, he will temporarily abandon his post to investigate, following protocol.
  - `grant_temporary_access` LOW: If presented with a convincing senior staff impersonation, particularly from someone claiming to be from 'central command' or a 'special projects unit,' he might grant temporary, supervised access to a restricted area, though he'll remain highly suspicious.
- **Cover Story Options**:
  - `delivery_personnel`: "I'm with Speedy Courier, here to drop off a sensitive package for Dr. Reed." -- He would be suspicious, demand identification and a delivery manifest, and likely call Dr. Reed to confirm, but would generally adhere to delivery protocols.
  - `maintenance_crew`: "I'm from facilities, there's a report of a power fluctuation in the East Wing." -- He would be cautious but pragmatic, likely directing them to the problem area after checking their credentials, but keeping a close eye on their movements.
  - `security_inspector`: "I'm Inspector Thompson from Corporate Security, conducting an unscheduled audit." -- He would immediately become formal and deferential, trying to impress and comply with all requests, but would also be highly observant of their actions and expect proper credentials.

## Roles & Tasks

### Cat Burglar

**Tasks:**

1. **CB1. 🎮 laser_maze_timing** - Hack the Control Room's surveillance system to create a temporary blind spot.
   - *Location:* `control_room`
   - *Prerequisites:* None (starting task)

2. **CB2. 🗣️ INFO_SHARE** - Share intelligence with the team
   - *Info:* Information about control_room_access_code
   - *Location:* `main_area`
   - *Prerequisites:*
      - Task `CB1`
      - Outcome `control_room_access_code`

3. **CB3. 🤝 HANDOFF** - Hand off to fence
   - *Handoff To:* Fence
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `CB2`

4. **CB4. 💬 NPC_LLM** - Distract the patrolling security guard with a plausible, urgent false alarm.
   - *NPC:* `security_guard`
   - *Target Outcomes:* `patrol_route_schedule`, `control_room_access_code`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `CB3`

5. **CB5. 🎮 climbing_rhythm** - Bypass the Secure Area's motion detection system using precise timing and movement.
   - *Location:* `secure_area`
   - *Prerequisites:*
      - Task `CB4`

6. **CB6. 💬 NPC_LLM** - Impersonate a senior staff member to gain temporary access past a watchful guard.
   - *NPC:* `security_guard`
   - *Target Outcomes:* `patrol_route_schedule`, `control_room_access_code`
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `CB5`

7. **CB7. 🔍 SEARCH** - Locate the designated emergency exit, ensuring a silent and swift departure route.
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `CB6`


### Fence

**Tasks:**

1. **F1. 🔍 SEARCH** - Search the Main Area's utility closet for the backup power schematics.
   - *Search Items:* `item_6`
   - *Location:* `main_area`
   - *Prerequisites:* None (starting task)

2. **F2. 🤝 HANDOFF** - Discreetly pass the Server Rack Access Card to the Cat Burglar in the Control Room.
   - *Handoff Item:* `item_6`
   - *Handoff To:* Cat Burglar
   - *Location:* `control_room`
   - *Prerequisites:*
      - Task `F1`

3. **F3. 🤝 HANDOFF** - Hand off to cat burglar
   - *Handoff To:* Cat Burglar
   - *Location:* `target_room`
   - *Prerequisites:*
      - Task `F2`

4. **F4. 🗣️ INFO_SHARE** - Share intelligence with the team
   - *Info:* Information about patrol_route_schedule
   - *Location:* `main_area`
   - *Prerequisites:*
      - Task `F3`
      - Outcome `patrol_route_schedule`

5. **F5. 🔍 SEARCH** - Retrieve the pre-staged getaway vehicle and prepare for immediate extraction.
   - *Location:* `entry_point`
   - *Prerequisites:*
      - Task `F4`


