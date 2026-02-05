# Museum Gala Vault Heist - Dependency Tree

> **Generated Heist Scenario**  
> **Scenario ID**: `museum_gala_vault`  
> **Objective**: Steal the jewels from the museum vault during a black-tie event.  
> **Summary**: Infiltrate a gala, secure access, crack the vault, and escape unnoticed.  
> **Selected Roles**: Mastermind, Hacker, Safe Cracker  
> **Player Count**: 3 players  

---

## Objective
Steal the Grand Jewel from the museum vault during the annual black-tie gala and escape unnoticed.

## Scenario Overview
The city's prestigious Natural History Museum is hosting its annual black-tie gala, showcasing the legendary Grand Jewel in a heavily secured vault in the basement. The crew must infiltrate the high-society event, bypass sophisticated electronic and physical security, crack the vault, and make a clean getaway. This requires careful coordination, technical expertise, and precision physical manipulation.

## Locations

This scenario takes place across the following locations:

### Off-Site Preparation
- **Safe House** - Crew meeting, briefing, equipment storage
- **Getaway Vehicle (Initial)** - Staging area for the escape car

### Museum Exterior
- **Museum Front Steps** - Main gala entrance, public arrival
- **Museum Side Entrance** - Staff/service entrance (restricted)
- **Rooftop Across Street** - Potential surveillance point (not used by these roles)

### Museum Interior - Public Areas
- **Grand Hall** - Main gala space, guest mingling, exhibits
- **Coat Check Room** - Guest storage, lost & found

### Museum Interior - Staff/Restricted Areas
- **Security Checkpoint** - Entry to restricted staff areas
- **Service Corridor (Catering)** - Staff passages, catering station, supplies
- **Janitorial Closet** - Cleaning supplies, potential hiding spots for keys
- **Maintenance Room** - Building systems, tools, equipment
- **Curator's Office** - Administrative office, contains curator's computer
- **Security Room** - Camera feeds, guard station, main security systems

### Vault Area
- **Vault Corridor** - Approach to the vault, often monitored
- **Vault Room** - Target location, jewel display

### Escape
- **Getaway Vehicle (Final)** - Vehicle positioned for quick extraction

**Total Locations**: 15

---

## Task Types

Every task in this heist is one of five types:

- **🎮 Minigame**: Player-controlled action from `roles.json`
- **💬 NPC/LLM**: Dialogue or interaction with AI-controlled character
- **🔍 Search/Hunt**: Player searches a location for hidden items
- **🤝 Item Handoff**: Physical item transfer between players (tracked in inventory)
- **🗣️ Info Share**: Verbal information exchange between players (real-life conversation)

---

## Roles & Dependencies

### Mastermind

**Tasks:**
1.  **🔍 Search** - Hunt for Gala Invitation
    -   Scour discarded event materials or old guest lists for a legitimate-looking invitation.
    -   *Find: Unused Gala Invitation (with a plausible name)*
    -   *Location:* Safe House
    -   *Dependencies:* None (starting task)
2.  **🔍 Search** - Hunt for Museum Blueprints
    -   Locate outdated or publicly available blueprints of the museum layout.
    -   *Find: Museum Floor Plans (digital copy)*
    -   *Location:* Safe House
    -   *Dependencies:* None (starting task)
3.  **💬 NPC** - Brief Crew in Safehouse
    -   Review gathered intel and blueprints, assign specific roles and entry points.
    -   *NPC: Crew Members (focused, eager) - "Alright, listen up. Here's the plan. We're going in clean."*
    -   *Location:* Safe House
    -   *Dependencies:* Gala Invitation found, Blueprints found
4.  **💬 NPC** - Infiltrate Gala
    -   Present the invitation at the main entrance, convincing security of legitimacy. This task is shared with Hacker and Safe Cracker, who enter with the Mastermind.
    -   *NPC: Bouncer Boris (by-the-book, suspicious) - "Invitation, please. Name on the list? Don't see you here often."*
    -   *Location:* Museum Front Steps
    -   *Dependencies:* Briefing complete
5.  **💬 NPC** - Coordinate Team via Radio
    -   Use encrypted comms to direct team movements, relay intel, and adapt to unforeseen complications.
    -   *NPC: Crew Members (various moods) - "Hacker, status report. Safe Cracker, clear the path."*
    -   *Location:* Grand Hall
    -   *Dependencies:* Team inside building
6.  **🗣️ EXTRACTION** → Signal Crew
    -   Give the "go" signal for extraction once the jewel is secured and the path is clear.
    -   *Location:* Grand Hall (via Radio)
    -   *Dependencies:* Jewel secured, Escape route confirmed clear

---

### Hacker

**Tasks:**
1.  **🔍 Search** - Hunt for Ethernet Cable
    -   Locate a specific type of cable needed to connect the hacking device to the team's remote laptop.
    -   *Find: CAT6 Ethernet Cable (10ft)*
    -   *Location:* Safe House
    -   *Dependencies:* None (parallel start)
2.  **🎮 wire_connecting** - Prep Hacking Device
    -   Assemble and configure the specialized hacking device, connecting colored wires to matching ports.
    -   *Location:* Safe House
    -   *Dependencies:* Ethernet Cable found
3.  **💬 NPC** - Infiltrate Gala
    -   Enter the museum alongside the Mastermind and Safe Cracker, blending in as a guest.
    -   *NPC: Bouncer Boris (observant, wary) - "Just the three of you? Enjoy the evening, but no funny business."*
    -   *Location:* Museum Front Steps
    -   *Dependencies:* Mastermind has invitation, Device prepped
4.  **🤝 DEVICE** → Deliver to Safe Cracker
    -   Pass the prepped hacking device discreetly to the Safe Cracker for physical planting.
    -   *Location:* Grand Hall
    -   *Dependencies:* Device prepped
5.  **🎮 cipher_wheel_alignment** - Disable Cameras
    -   Remotely access the museum's security network and loop camera feeds in the vault area.
    -   *Location:* Grand Hall (using hidden laptop)
    -   *Dependencies:* Hacking Device planted by Safe Cracker
6.  **💬 NPC** - Distract Curator (Remote)
    -   While the Safe Cracker physically distracts the Curator, Hacker remotely accesses the Curator's computer for the vault code.
    -   *NPC: Dr. Aris Thorne (pedantic, easily annoyed) - "My work is highly sensitive! Who is trying to access my files?!"*
    -   *Location:* Grand Hall (remote access to Curator's Office)
    -   *Dependencies:* Safe Cracker distracts Curator
7.  **🎮 simon_says_sequence** - Retrieve Vault Code
    -   