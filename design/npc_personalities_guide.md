# NPC Personalities Guide

## Purpose

NPCs (Non-Player Characters) are the heart of the social interaction gameplay. Each NPC should have a memorable personality, quirky speech patterns, and relatable motivations that make interactions fun and replayable.

---

## Core Principles

### 1. Every NPC is a Character
- Give them a name, personality trait, and speech pattern
- Make them memorable and distinct from other NPCs
- Base personality on scenario context (museum guard vs. train conductor)

### 2. Humor + Humanity
- Add quirky details that make them feel real
- Use humor to keep tone light and fun
- Give them relatable motivations (bored at work, excited about hobby, worried about rent)

### 3. Replay Value Through Randomness
- Generate random personality combinations each playthrough
- Mix and match traits, speech patterns, and motivations
- Keep core role function same, but change how they express it

---

## NPC Personality Template

Each NPC should have:

```json
{
  "name": "Generated or role-based name",
  "role": "Guard / Curator / Vendor / etc.",
  "personality_trait": "One dominant trait",
  "speech_pattern": "How they talk",
  "motivation": "What they care about",
  "interaction_style": "How they engage",
  "location": "Where they are found"
}
```

---

## Personality Traits (Pick One Primary)

### Social Traits
- **Chatty**: Loves to talk, hard to escape conversation
- **Suspicious**: Questions everything, needs convincing
- **Helpful**: Eager to assist, maybe too eager
- **Nervous**: Anxious, fidgety, worried about rules
- **Overconfident**: Thinks they know everything
- **Gossipy**: Loves drama, shares secrets easily
- **Grumpy**: Annoyed, wants to be left alone
- **Friendly**: Warm, trusting, accommodating

### Professional Traits
- **By-the-book**: Follows rules strictly
- **Lazy**: Cutting corners, wants easy way out
- **Ambitious**: Trying to impress boss
- **Distracted**: Mind elsewhere, not paying attention
- **Corrupt**: Open to bribes or deals
- **Incompetent**: Doesn't understand their job
- **Dedicated**: Takes job very seriously
- **Burned out**: Hates their job, counting down to retirement

### Quirky Traits
- **Narcissistic**: Only talks about themselves
- **Conspiracy theorist**: Sees patterns everywhere
- **Oversharer**: TMI about personal life
- **Pedantic**: Corrects grammar, fixates on details
- **Superstitious**: Believes in omens, lucky charms
- **Obsessed with hobby**: Brings everything back to their interest
- **Hypochondriac**: Constantly worried about health
- **Drama queen**: Everything is the biggest deal

---

## Speech Patterns (Mix and Match)

### Language Style
- **Broken English**: ESL speaker, funny grammar ("I no see you before, where you coming from?")
- **Formal**: Overly proper ("Indeed, one must acquire the appropriate credentials")
- **Slang-heavy**: Modern slang ("That's cap bro, no way you work here")
- **Old-timey**: Dated expressions ("Well I'll be, ain't that something!")
- **Technical jargon**: Industry-specific terms ("Per protocol 7B, I need to verify your credentials")
- **Valley girl**: Like, totally, literally everywhere
- **Mumbler**: Hard to understand, trails off
- **Loud**: TALKS IN ALL CAPS

### Quirks
- Repeats last word word
- Always interrupts themselves - wait, no - never mind
- Asks rhetorical questions, doesn't wait for answers
- Refers to themselves in third person
- Uses wrong idioms ("It's not rocket surgery!")
- Adds filler words constantly (um, like, you know, right?)
- Speaks in questions? Everything sounds uncertain?

---

## Motivations (What They Care About)

### Personal Needs
- Getting home on time
- Impressing a crush
- Paying rent / medical bills
- Getting promoted
- Avoiding their boss
- Finding a restroom
- Not getting fired
- Taking a break

### Interests
- Sports team obsession
- Upcoming vacation
- New hobby they just started
- Celebrity gossip
- Online drama
- Their pet
- Their kids/family
- Their retirement plans

### Situational
- Something broken they need to fix
- Recent argument with coworker
- Excited about event later
- Worried about weather
- Dealing with personal crisis
- Celebrating something
- Nursing a hangover
- First day on the job

---

## Scenario-Specific NPC Archetypes

### Museum Gala Setting

**Security Guard (Day Shift)**
- Traits: Burned out, lazy, counting hours
- Speech: "Look, I just need to make it to 6pm without incident, alright?"
- Motivation: Fantasy football draft tonight

**Museum Curator**
- Traits: Narcissistic, pedantic, gossipy
- Speech: "As I was telling the Met director—we went to Yale together—this exhibit is simply revolutionary"
- Motivation: Wants credit for exhibit, jealous of rival curator

**Gala Guest (Socialite)**
- Traits: Narcissistic, chatty, oversharer
- Speech: "This dress is vintage Chanel—do you know how long I searched for it? Three months in Paris!"
- Motivation: Being photographed, being seen, networking

**Caterer**
- Traits: Stressed, nervous, distracted
- Speech: "Did you see which way the kitchen is? The shrimp are getting warm and chef is going to kill me"
- Motivation: Not screwing up this high-profile event

**Security Supervisor**
- Traits: By-the-book, ambitious, overconfident
- Speech: "Nothing gets past me. I've been doing this for 15 years. 15. Years."
- Motivation: Wants to be head of security someday

**Museum Janitor**
- Traits: Gossipy, helpful, conspiracy theorist
- Speech: "You didn't hear it from me, but I heard the curator and the director arguing about the insurance on that diamond"
- Motivation: Just wants drama, bored with job

**Coat Check Attendant**
- Traits: Friendly, oblivious, obsessed with hobby
- Speech: "Oh you're here for the gala! Did you know the marble in this hall is from the same quarry as—"
- Motivation: Loves architecture, wants to share knowledge

**Wealthy Donor**
- Traits: Grumpy, suspicious, pedantic
- Speech: "Young person, do you have proper clearance to be in this section? Show me your credentials."
- Motivation: Donated money, feels entitled to police the event

### Train Setting

**Train Conductor**
- Traits: By-the-book, nervous, helpful
- Speech: "Tickets please! We're running 7 minutes behind schedule and I need everyone seated by car 4"
- Motivation: Perfect safety record, doesn't want incident

**Sleeping Car Attendant**
- Traits: Gossipy, chatty, oversharer
- Speech: "Oh honey, you would NOT believe what I found in cabin 7 last week. I can't even repeat it!"
- Motivation: Bored, long shift, loves drama

**Food Service Worker**
- Traits: Burned out, lazy, distracted
- Speech: "Coffee? Yeah, sure, just... give me a minute. I'm trying to remember if I turned off my stove at home"
- Motivation: Wants shift to end, worried about home stuff

**Security Guard (Train)**
- Traits: Overconfident, ambitious, suspicious
- Speech: "Ex-military. I can spot trouble from 50 yards. You're not trouble, are you?"
- Motivation: Wants to be hero, catch bad guys

**Passenger (Business Person)**
- Traits: Stressed, impatient, important
- Speech: "Can you NOT see I'm on a call? This deal is worth millions—MILLIONS—and you're asking about pretzels?"
- Motivation: Closing big deal, distracted by work

**Passenger (Tourist)**
- Traits: Friendly, chatty, oblivious
- Speech: "This is our first train ride! Can you believe it? We're from Kansas. Do you know Kansas? Beautiful state!"
- Motivation: Excited about vacation, wants to share joy

**Janitor**
- Traits: Conspiracy theorist, helpful, gossipy
- Speech: "You ask me, they're hiding something in that armored car. Government doesn't move 'artifacts' in the middle of the night"
- Motivation: Bored, wants to feel special with inside knowledge

---

## Generating NPCs

### Random Generation Template

For each NPC interaction, generate:

```
Name: [Random appropriate name]
Role: [Functional role in scenario]
Primary Trait: [Pick from personality traits]
Speech Pattern: [Pick from speech patterns]
Motivation: [Pick from motivations]
Location: [Where they appear]
Opening Line: [First thing they say]
Easy/Hard Buttons: [What player can say to succeed/fail]
```

### Example: Museum Guard

```json
{
  "name": "Frank Delgado",
  "role": "Day Shift Security Guard",
  "personality_trait": "Burned out, fantasy football obsessed",
  "speech_pattern": "Casual, distracted, mumbles",
  "motivation": "Draft starts at 6pm, just needs to survive shift",
  "location": "Security checkpoint near staff entrance",
  "opening_line": "Yeah yeah, credentials... listen, you seen the injury report for the Patriots? My RB1 might be out.",
  "easy_approach": "Pretend to care about fantasy football, distract him",
  "hard_approach": "Be formal and demanding, he'll get annoyed"
}
```

### Example: Gala Guest

```json
{
  "name": "Vivienne St. Claire",
  "role": "Wealthy socialite",
  "personality_trait": "Narcissistic, fashionista",
  "speech_pattern": "Valley girl meets old money",
  "motivation": "Be seen, be photographed, outshine rivals",
  "location": "Grand Hall near champagne fountain",
  "opening_line": "Oh my GOD, you HAVE to tell me—does this dress photograph well? I literally cannot tell if the lighting is flattering.",
  "easy_approach": "Compliment her outfit, let her talk about herself",
  "hard_approach": "Ignore her or criticize fashion, she'll get defensive"
}
```

---

## Interaction Design

### Structure of NPC Conversations

Each NPC interaction should have:

1. **Setup**: Player approaches NPC with goal (get info, access, distraction)
2. **Opening**: NPC's personality-driven greeting
3. **Middle**: Player chooses dialogue approach based on personality
4. **Resolution**: Success/failure based on reading NPC correctly

### Dialogue Choice Design

Give players 3-4 options that play to different personalities:

**Example: Talking to Burned-Out Guard**

Options:
- A) "I need access immediately. This is urgent official business." (❌ Makes him annoyed)
- B) "Hey man, who you got in your fantasy lineup this week?" (✅ He loves this, gets distracted)
- C) "Look, I just want to get through without hassle. Can we skip the formalities?" (✅ He appreciates honesty)
- D) "I'm reporting your unprofessional behavior to your supervisor." (❌ Now he's paying attention)

### Success Variations

Even success can have personality flavor:

✅ **Enthusiastic Success**: "Oh yeah, TOTALLY! Go ahead! Hey, before you go, who do you like in the Packers game?"

✅ **Reluctant Success**: "Fine, fine, whatever. Just... make it quick. And don't tell anyone I let you through."

✅ **Oblivious Success**: "Hmm? Oh yeah sure, I guess that's fine. Wait, what were we talking about?"

---

## LLM Prompting Guidelines

When generating NPC dialogue with an LLM:

### System Prompt Template

```
You are [NPC Name], a [role] at [location]. 

Personality: [trait]
Speech pattern: [pattern]
Current mood: [motivation/distraction]

The player is trying to [goal]. You don't know they're criminals.

Respond in character with 2-3 sentences. Be [personality] and [speech pattern].
Show your [motivation] in your response.
```

### Example Prompt

```
You are Frank Delgado, a museum security guard. 

Personality: Burned out, distracted by fantasy football draft tonight
Speech pattern: Casual, mumbles, trails off mid-sentence
Current mood: Stressed about his RB1 injury, counting down hours until 6pm

The player is trying to get through your checkpoint without proper credentials. You don't know they're criminals.

Respond in character with 2-3 sentences. Be burned out and distracted.
Show your fantasy football obsession in your response.
```

**LLM Response:**
"Credentials? Yeah, uh... look, I gotta check on something. My running back just got listed as questionable and if he doesn't play tonight I'm—wait, what did you need again?"

---

## Replayability Through Variation

### Same Role, Different Person

**Guard Encounter 1:**
- Frank (burned out, fantasy football)
- Easy: Talk sports
- Hard: Be demanding

**Guard Encounter 2 (different playthrough):**
- Sarah (nervous, first day, by-the-book)
- Easy: Be confident and reassuring
- Hard: Rush her or be suspicious

**Guard Encounter 3:**
- Marcus (overconfident, ambitious, wants promotion)
- Easy: Appeal to his ego
- Hard: Undermine his authority

Same functional role, completely different interaction.

---

## Testing NPCs

### Good NPC Checklist

✅ Can you describe them in 3 words?
✅ Would players remember them after the game?
✅ Does their speech pattern feel distinct?
✅ Is their motivation relatable/funny?
✅ Do multiple dialogue approaches make sense?
✅ Is success/failure based on reading personality correctly?

### Bad NPC Antipatterns

❌ Generic "Guard #3" with no personality
❌ Personality that doesn't affect gameplay
❌ Only one way to succeed (no player choice)
❌ Offensive stereotypes or punching down
❌ So quirky they break immersion

---

## Future Enhancements

- Voice acting with personality-appropriate voices
- Visual character portraits matching personality
- NPCs that remember previous interactions
- NPCs that react to team's reputation/noise level
- Dynamic personality shifts based on player behavior
- Relationships between NPCs (rivalries, friendships)
