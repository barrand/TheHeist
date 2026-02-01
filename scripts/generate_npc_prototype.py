#!/usr/bin/env python3
"""
Generate standalone NPC interaction prototype HTML files.

Creates interactive chat prototypes for testing NPC conversations with:
- The Heist's Neon Purple theme
- Free-form text input
- LLM-based information detection
- Difficulty settings
- Character portrait integration

Usage:
    python generate_npc_prototype.py --name "Vincent Cole" --role "Casino Manager" \
        --objective "Find the vault access code" --info "4-digit code: 7392"
        
    # With custom scenario
    python generate_npc_prototype.py --name "Sarah Chen" --role "Art Curator" \
        --objective "Learn the painting's location" --info "Third floor, east wing" \
        --scenario "Museum heist during charity gala" --difficulty medium
"""

import argparse
import sys
from pathlib import Path
from config import GEMINI_API_KEY

# Import the image generation function
from generate_npc_image import generate_npc_image

def generate_npc_prototype_html(
    npc_name: str,
    npc_role: str,
    objective: str,
    objective_info: str,
    scenario: str = "",
    difficulty: str = "medium",
    gender: str = "person",
    ethnicity: str = None,
    clothing: str = None,
    background: str = None,
    expression: str = "neutral",
    details: str = None,
    attitude: str = "neutral",
    output_file: str = None,
):
    """
    Generate a standalone NPC interaction prototype HTML file.
    
    Args:
        npc_name: Character name
        npc_role: Character's job/role
        objective: What the player needs to learn
        objective_info: The critical information to extract
        scenario: Context/scenario description
        difficulty: easy, medium, or hard
        gender: Character gender
        ethnicity: Character ethnicity
        clothing: What they wear
        background: Setting description
        expression: Facial expression
        details: Additional character details
        attitude: Overall personality vibe
        output_file: Output HTML file path (default: prototype/{name_safe}.html)
    """
    
    # Generate character image first
    print(f"\n🎨 Generating character portrait for {npc_name}...")
    name_safe = npc_name.lower().replace(' ', '_').replace("'", '')
    image_path = f"prototype/{name_safe}.png"
    
    try:
        generate_npc_image(
            name=npc_name,
            role=npc_role,
            gender=gender,
            ethnicity=ethnicity,
            clothing=clothing or f"{npc_role.lower()} attire",
            background=background or "appropriate setting",
            expression=expression,
            details=details,
            attitude=attitude,
            accent_colors="purple",  # Neon Purple theme
            output_file=image_path,
        )
        image_filename = f"{name_safe}.png"
    except Exception as e:
        print(f"⚠️  Warning: Could not generate image: {e}")
        print("   Prototype will use placeholder")
        image_filename = None
    
    # Build difficulty descriptions
    difficulty_prompts = {
        "easy": {
            "personality": "very friendly and helpful",
            "failure": "You'd have to be very rude or threatening to fail",
        },
        "medium": {
            "personality": "professional but cautious",
            "failure": "Being too direct or suspicious will make them clam up",
        },
        "hard": {
            "personality": "suspicious and protective of information",
            "failure": "Any misstep in conversation will end the interaction",
        },
    }
    
    diff_info = difficulty_prompts.get(difficulty, difficulty_prompts["medium"])
    
    # Create scenario context
    if not scenario:
        scenario = f"You encounter {npc_name} during your heist operation."
    
    # Determine output path
    if not output_file:
        output_file = f"prototype/{name_safe}_chat.html"
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Heist - {npc_name} Interaction</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: #0D0517;  /* Neon Purple bg-primary */
            color: #FFFFFF;
            padding: 20px;
            line-height: 1.5;
        }}
        
        .container {{
            max-width: 480px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 24px;
        }}
        
        .header h1 {{
            font-size: 24px;
            font-weight: bold;
            color: #B565FF;  /* accent-primary */
            margin-bottom: 8px;
        }}
        
        .header p {{
            font-size: 14px;
            color: #B0B0B0;  /* text-secondary */
        }}
        
        .card {{
            background: #1A0F2E;  /* bg-secondary */
            border: 1px solid #3A2550;  /* border-subtle */
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
        }}
        
        .card.selected {{
            border: 2px solid #B565FF;
            box-shadow: 0 4px 12px rgba(181, 101, 255, 0.3);
        }}
        
        .character-section {{
            text-align: center;
            margin-bottom: 24px;
        }}
        
        .character-image {{
            width: 280px;
            height: 280px;
            border-radius: 12px;
            border: 3px solid #B565FF;
            margin: 0 auto 16px;
            display: block;
        }}
        
        .character-name {{
            font-size: 20px;
            font-weight: bold;
            color: #FFFFFF;
            margin-bottom: 4px;
        }}
        
        .character-role {{
            font-size: 14px;
            color: #B0B0B0;
        }}
        
        .objective-section {{
            background: #2A1A45;  /* bg-tertiary */
            border: 2px solid #B565FF;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
        }}
        
        .objective-header {{
            font-size: 12px;
            font-weight: 600;
            color: #D199FF;  /* accent-light */
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        
        .objective-text {{
            font-size: 14px;
            color: #FFFFFF;
            line-height: 1.6;
        }}
        
        .chat-container {{
            background: #1A0F2E;
            border: 1px solid #3A2550;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            min-height: 300px;
            max-height: 400px;
            overflow-y: auto;
        }}
        
        .chat-message {{
            margin-bottom: 12px;
            animation: slideIn 0.3s ease-out;
        }}
        
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(10px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .chat-bubble {{
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 80%;
            word-wrap: break-word;
        }}
        
        .chat-bubble.npc {{
            background: #2A1A45;
            border: 1px solid #3A2550;
            border-radius: 12px 12px 12px 4px;
        }}
        
        .chat-bubble.player {{
            background: #B565FF;
            color: #0D0517;
            border-radius: 12px 12px 4px 12px;
            margin-left: auto;
        }}
        
        .chat-label {{
            font-size: 11px;
            font-weight: 600;
            color: #888888;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .chat-text {{
            font-size: 14px;
            line-height: 1.5;
        }}
        
        .input-section {{
            margin-bottom: 16px;
        }}
        
        .input-field {{
            width: 100%;
            background: #2A1A45;
            border: 1px solid #3A2550;
            border-radius: 8px;
            padding: 12px;
            color: #FFFFFF;
            font-size: 14px;
            font-family: inherit;
            resize: vertical;
            min-height: 60px;
        }}
        
        .input-field:focus {{
            outline: none;
            border: 2px solid #B565FF;
            box-shadow: 0 0 0 3px rgba(181, 101, 255, 0.1);
        }}
        
        .button {{
            width: 100%;
            background: #B565FF;
            color: #0D0517;
            border: none;
            border-radius: 8px;
            padding: 14px 24px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s;
            box-shadow: 0 2px 8px rgba(181, 101, 255, 0.3);
        }}
        
        .button:hover {{
            background: #D199FF;
            transform: translateY(-1px);
        }}
        
        .button:active {{
            background: #8B3FCC;
            transform: scale(0.98);
        }}
        
        .button:disabled {{
            background: #555555;
            color: #888888;
            cursor: not-allowed;
            transform: none;
        }}
        
        .button.secondary {{
            background: transparent;
            color: #FFFFFF;
            border: 2px solid #4A3560;
        }}
        
        .button.secondary:hover {{
            border-color: #B565FF;
            color: #B565FF;
        }}
        
        .status {{
            text-align: center;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 16px;
            font-weight: 600;
        }}
        
        .status.success {{
            background: #1E2A3A;
            border: 2px solid #00E5FF;
            color: #00E5FF;
        }}
        
        .status.failure {{
            background: #3A1E1E;
            border: 2px solid #E53935;
            color: #E53935;
        }}
        
        .difficulty-badge {{
            display: inline-block;
            background: #FF6B9D;
            color: #0D0517;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .loading {{
            text-align: center;
            color: #B0B0B0;
            font-size: 14px;
            padding: 12px;
        }}
        
        .info-text {{
            font-size: 12px;
            color: #888888;
            text-align: center;
            margin-top: 16px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎭 THE HEIST</h1>
            <p>NPC Interaction Prototype</p>
        </div>
        
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 14px; color: #B0B0B0;">Difficulty</span>
                <span class="difficulty-badge">{difficulty.upper()}</span>
            </div>
            <div style="font-size: 12px; color: #888888; line-height: 1.5;">
                {diff_info['failure']}
            </div>
        </div>
        
        <div class="character-section">
            {'<img src="' + image_filename + '" alt="' + npc_name + '" class="character-image">' if image_filename else '<div style="width: 280px; height: 280px; background: #2A1A45; border: 3px solid #B565FF; border-radius: 12px; margin: 0 auto 16px; display: flex; align-items: center; justify-content: center; color: #888888;">No image</div>'}
            <div class="character-name">{npc_name}</div>
            <div class="character-role">{npc_role}</div>
        </div>
        
        <div class="card">
            <div style="font-size: 12px; font-weight: 600; color: #888888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">
                Scenario
            </div>
            <div style="font-size: 14px; color: #FFFFFF; line-height: 1.6;">
                {scenario}
            </div>
        </div>
        
        <div class="objective-section">
            <div class="objective-header">🎯 Your Objective</div>
            <div class="objective-text">{objective}</div>
        </div>
        
        <div class="chat-container" id="chatContainer"></div>
        
        <div id="statusContainer"></div>
        
        <div class="input-section">
            <textarea 
                id="playerInput" 
                class="input-field" 
                placeholder="Type your response..."
                rows="2"
            ></textarea>
        </div>
        
        <button id="sendButton" class="button" onclick="sendMessage()">
            Send Message
        </button>
        
        <button class="button secondary" onclick="resetConversation()" style="margin-top: 12px;">
            Reset Conversation
        </button>
        
        <div class="info-text">
            Powered by Gemini 2.5 Flash • Neon Purple Theme
        </div>
    </div>
    
    <script>
        const NPC_NAME = "{npc_name}";
        const NPC_ROLE = "{npc_role}";
        const OBJECTIVE_INFO = "{objective_info}";
        const DIFFICULTY = "{difficulty}";
        
        // Pre-filled API key (prototype only - never commit with real key)
        const API_KEY = "{GEMINI_API_KEY}";
        
        let conversationHistory = [];
        let gameOver = false;
        
        // NPC personality based on difficulty
        const npcPrompts = {{
            easy: `You are {npc_name}, a {npc_role}. You are {diff_info['personality']}.
            
The player is trying to learn: {objective}
The answer is: {objective_info}

You will naturally reveal this information through friendly conversation. Be helpful and share details willingly. You enjoy chatting and helping people.`,
            
            medium: `You are {npc_name}, a {npc_role}. You are {diff_info['personality']}.
            
The player is trying to learn: {objective}
The answer is: {objective_info}

You will reveal this information if the player builds rapport and asks the right questions. You're not immediately suspicious, but you don't volunteer sensitive information to strangers. If they're polite and clever, you'll share what you know. If they're too direct or pushy, you become guarded.`,
            
            hard: `You are {npc_name}, a {npc_role}. You are {diff_info['personality']}.
            
The player is trying to learn: {objective}
The answer is: {objective_info}

You are VERY protective of this information. You will only reveal it if the player:
1. Builds significant trust over multiple exchanges
2. Has a convincing reason why they need to know
3. Never seems suspicious or threatening

If they ask too directly, seem suspicious, or make you uncomfortable, you will shut down the conversation. You might give subtle hints if they're very clever, but you never directly share sensitive information unless they've really earned your trust.`
        }};
        
        const systemPrompt = npcPrompts[DIFFICULTY];
        
        // Add initial greeting
        addNPCMessage(getGreeting());
        
        function getGreeting() {{
            const greetings = [
                "Hey there. Can I help you with something?",
                "Hello. What brings you here?",
                "Good to see you. What's up?",
            ];
            return greetings[Math.floor(Math.random() * greetings.length)];
        }}
        
        async function sendMessage() {{
            if (gameOver) return;
            
            const input = document.getElementById('playerInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add player message
            addPlayerMessage(message);
            input.value = '';
            
            // Disable input while processing
            toggleInput(false);
            showLoading();
            
            // Add to history
            conversationHistory.push({{
                role: 'user',
                parts: [{{ text: message }}]
            }});
            
            try {{
                // Get NPC response
                const npcResponse = await getNPCResponse(message);
                hideLoading();
                addNPCMessage(npcResponse);
                
                conversationHistory.push({{
                    role: 'model',
                    parts: [{{ text: npcResponse }}]
                }});
                
                // Check if information was revealed
                await checkIfInfoRevealed();
                
            }} catch (error) {{
                hideLoading();
                console.error('Error:', error);
                addNPCMessage("Sorry, I didn't catch that. Could you repeat?");
            }}
            
            toggleInput(true);
        }}
        
        async function getNPCResponse(message) {{
            const response = await fetch(
                `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key=${{API_KEY}}`,
                {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        system_instruction: {{ parts: [{{ text: systemPrompt }}] }},
                        contents: conversationHistory,
                        generationConfig: {{
                            temperature: 0.9,
                            maxOutputTokens: 200,
                        }}
                    }})
                }}
            );
            
            const data = await response.json();
            console.log('NPC Response:', data);
            
            if (data.candidates && data.candidates[0]) {{
                return data.candidates[0].content.parts[0].text;
            }}
            
            throw new Error('No response from API');
        }}
        
        async function checkIfInfoRevealed() {{
            // Use LLM to check if the critical information was revealed
            const checkPrompt = `Based on this conversation, has the NPC revealed the following information: "${{OBJECTIVE_INFO}}"?

Conversation:
${{conversationHistory.map(msg => 
    `${{msg.role === 'user' ? 'Player' : NPC_NAME}}: ${{msg.parts[0].text}}`
).join('\\n')}}

Answer with ONLY "YES" or "NO". Answer YES if the information was clearly communicated, even if phrased differently.`;
            
            const response = await fetch(
                `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key=${{API_KEY}}`,
                {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        contents: [{{ parts: [{{ text: checkPrompt }}] }}],
                        generationConfig: {{
                            temperature: 0.1,
                            maxOutputTokens: 10,
                        }}
                    }})
                }}
            );
            
            const data = await response.json();
            const answer = data.candidates[0].content.parts[0].text.trim().toUpperCase();
            
            console.log('Info revealed check:', answer);
            
            if (answer.includes('YES')) {{
                showSuccess();
            }}
        }}
        
        function addPlayerMessage(text) {{
            const container = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'chat-message';
            messageDiv.innerHTML = `
                <div style="display: flex; justify-content: flex-end;">
                    <div class="chat-bubble player">
                        <div class="chat-text">${{escapeHtml(text)}}</div>
                    </div>
                </div>
            `;
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }}
        
        function addNPCMessage(text) {{
            const container = document.getElementById('chatContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'chat-message';
            messageDiv.innerHTML = `
                <div class="chat-bubble npc">
                    <div class="chat-label">${{NPC_NAME}}</div>
                    <div class="chat-text">${{escapeHtml(text)}}</div>
                </div>
            `;
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }}
        
        function showLoading() {{
            const container = document.getElementById('chatContainer');
            const loadingDiv = document.createElement('div');
            loadingDiv.id = 'loadingIndicator';
            loadingDiv.className = 'loading';
            loadingDiv.textContent = '...';
            container.appendChild(loadingDiv);
            container.scrollTop = container.scrollHeight;
        }}
        
        function hideLoading() {{
            const loading = document.getElementById('loadingIndicator');
            if (loading) loading.remove();
        }}
        
        function showSuccess() {{
            gameOver = true;
            const statusContainer = document.getElementById('statusContainer');
            statusContainer.innerHTML = `
                <div class="status success">
                    ✅ SUCCESS! You learned: {objective_info}
                </div>
            `;
            toggleInput(false);
        }}
        
        function toggleInput(enabled) {{
            document.getElementById('playerInput').disabled = !enabled;
            document.getElementById('sendButton').disabled = !enabled;
        }}
        
        function resetConversation() {{
            conversationHistory = [];
            gameOver = false;
            document.getElementById('chatContainer').innerHTML = '';
            document.getElementById('statusContainer').innerHTML = '';
            document.getElementById('playerInput').value = '';
            toggleInput(true);
            addNPCMessage(getGreeting());
        }}
        
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        
        // Enter key to send
        document.getElementById('playerInput').addEventListener('keypress', (e) => {{
            if (e.key === 'Enter' && !e.shiftKey) {{
                e.preventDefault();
                sendMessage();
            }}
        }});
    </script>
</body>
</html>
"""
    
    # Write to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content)
    
    print(f"\n✅ Generated NPC prototype!")
    print(f"💾 Saved to: {output_path}")
    print(f"\n🎮 Open in browser: {output_path.absolute()}")
    print(f"🎭 Character: {npc_name} ({npc_role})")
    print(f"🎯 Objective: {objective}")
    print(f"💪 Difficulty: {difficulty}")
    print()
    
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description='Generate NPC interaction prototype HTML files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple casino manager scenario
  python generate_npc_prototype.py --name "Vincent Cole" --role "Casino Manager" \\
    --objective "Find the vault access code" --info "4-digit code: 7392"
  
  # Museum curator with full details
  python generate_npc_prototype.py --name "Dr. Sarah Chen" --role "Art Curator" \\
    --objective "Learn the painting's location" --info "Third floor, east wing, room 3E" \\
    --scenario "Charity gala at the museum" --difficulty hard \\
    --gender female --ethnicity "Asian" --clothing "elegant evening dress" \\
    --background "museum gallery" --expression "sophisticated"
        """
    )
    
    parser.add_argument('--name', required=True, help='NPC name')
    parser.add_argument('--role', required=True, help='NPC role/job')
    parser.add_argument('--objective', required=True, help='What player needs to learn')
    parser.add_argument('--info', required=True, help='The critical information to extract')
    
    parser.add_argument('--scenario', default='', help='Scenario context')
    parser.add_argument('--difficulty', default='medium', choices=['easy', 'medium', 'hard'],
                       help='Difficulty level (default: medium)')
    
    # Character appearance
    parser.add_argument('--gender', default='person', choices=['male', 'female', 'person'],
                       help='Character gender')
    parser.add_argument('--ethnicity', help='Character ethnicity')
    parser.add_argument('--clothing', help='What they wear')
    parser.add_argument('--background', help='Setting/background')
    parser.add_argument('--expression', default='neutral', help='Facial expression')
    parser.add_argument('--details', help='Additional visual details')
    parser.add_argument('--attitude', default='neutral', help='Overall personality vibe')
    
    parser.add_argument('--output', help='Output HTML file path')
    
    args = parser.parse_args()
    
    generate_npc_prototype_html(
        npc_name=args.name,
        npc_role=args.role,
        objective=args.objective,
        objective_info=args.info,
        scenario=args.scenario,
        difficulty=args.difficulty,
        gender=args.gender,
        ethnicity=args.ethnicity,
        clothing=args.clothing,
        background=args.background,
        expression=args.expression,
        details=args.details,
        attitude=args.attitude,
        output_file=args.output,
    )


if __name__ == '__main__':
    main()
