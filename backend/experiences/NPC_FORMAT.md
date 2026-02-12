# NPC Format in Experience Files

## Overview

NPCs are defined in a structured section of experience files with all information needed for:
- **Image Generation** (`backend/scripts/generate_npc_image.py`)
- **AI Conversations** (`backend/app/services/npc_conversation_service.py`)
- **Game Display** (WHO'S HERE section, conversations)

## Format

```markdown
## NPCs

### [Role] - [Full Name]
- **ID**: `npc_id` (snake_case identifier for reference in tasks)
- **Role**: [Job/Position]
- **Location**: [Starting location]
- **Age**: [Number]
- **Gender**: male | female | person
- **Ethnicity**: [Ethnicity descriptor]
- **Clothing**: [What they wear]
- **Expression**: [Facial expression: friendly, bored, suspicious, etc.]
- **Attitude**: [Overall demeanor]
- **Details**: [Additional visual details]
- **Personality**: [Full personality description for AI conversations]
- **Relationships**: [How this NPC relates to other NPCs — who they know, what they think of them]
- **Story Context**: [Ground-truth world facts this NPC must never contradict — where key objects are, what's public vs secret, what the NPC would/wouldn't do]
- **Information Known**:
  - `info_id` HIGH: [The ONE tagged info item this NPC provides]
  - LOW: [Flavor text, no ID]
- **Actions Available**:
  - (none) OR `action_id` HIGH: [The ONE tagged action this NPC can perform]
- **Cover Story Options**:
  - `cover_id`: "Cover description" -- (NPC's instinct about this person)
  - `another_cover`: "Another cover" -- (NPC's reaction)
  - `funny_cover`: "Silly/funny cover" -- (NPC's bewildered reaction)
```

## Example

```markdown
### Security Guard - Marcus Romano
- **ID**: `security_guard`
- **Role**: Museum Security Guard
- **Location**: Grand Hall
- **Age**: 45
- **Gender**: male
- **Ethnicity**: White
- **Clothing**: Navy security uniform with badge and radio
- **Expression**: bored
- **Attitude**: lonely, chatty
- **Details**: Holding clipboard, wearing glasses
- **Personality**: Bored and lonely on the night shift. Loves sports and misses the excitement of his old job. Gets chatty when someone shows interest in his stories. Genuinely believes nothing interesting ever happens at the museum.
- **Information Known**:
  - HIGH: The Eye of Orion jewels are in the new vault exhibit in the basement, east wing
  - HIGH: He's been assigned to guard the vault exhibit all week
  - MEDIUM: His patrol schedule - he leaves the vault area around 9 PM for his break
  - LOW: The museum director is paranoid about security since the last incident
- **Conversation Hints**: 
  - Bring up sports to get him talking
  - Show sympathy about his boring shift
  - Ask casual questions about the museum exhibits
```

## Task References

When referencing NPCs in tasks, use the ID:

```markdown
1. **MM1. 💬 NPC** - Chat with Security Guard
   - *Description:* Engage the museum guard in conversation...
   - *NPC:* `security_guard` (Marcus Romano)
   - *Objectives to Learn:*
     - Vault location (basement, east wing)
     - Guard's patrol schedule
   - *Location:* Grand Hall
   - *Dependencies:* None
```

## Field Usage

### Image Generation Fields
Used by `generate_npc_image.py`:
- name
- role
- gender
- ethnicity
- clothing
- expression
- details
- attitude

### AI Conversation Fields
Used by `npc_conversation_service.py`:
- name
- role
- personality
- location
- relationships
- story_context (injected as immutable world facts to prevent LLM contradictions)
- Information Known (target outcomes + background flavor)
- Actions Available (target actions)
- Cover Story Options (player cover choices)

### Game Display Fields
Used by frontend:
- ID (for reference)
- name
- role
- location (for WHO'S HERE section)

## Information Confidence Levels

- **HIGH**: Information the NPC definitely knows and will share if asked properly
- **MEDIUM**: Information the NPC might know or remember if prompted
- **LOW**: Background information that's harder to extract

## Conversation Hints

Provide guidance for players on how to approach the NPC:
- Topics to build rapport
- Questions to ask
- Approaches to avoid
- What makes them comfortable/uncomfortable

These hints help players understand the NPC's personality and how to interact effectively.
