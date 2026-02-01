#!/usr/bin/env python3
"""
Generate standalone NPC interaction prototype HTML files (V2).

Enhanced with:
- Setup screen for API key and difficulty selection
- Hybrid interaction: Quick response buttons + free-form text
- Proper image path handling
- Neon Purple theme matching Flutter app

Usage:
    python generate_npc_prototype_v2.py --name "Vincent Cole" --role "Casino Manager" \
        --objective "Find the vault access code" --info "4-digit code: 7392"
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
    """Generate a standalone NPC interaction prototype HTML file (V2)."""
    
    # Generate character image first
    print(f"\n🎨 Generating character portrait for {npc_name}...")
    name_safe = npc_name.lower().replace(' ', '_').replace("'", '').replace('"', '')
    
    # Save image in same directory as HTML
    image_filename = f"{name_safe}.png"
    
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
            output_file=f"prototype/{image_filename}",
        )
    except Exception as e:
        print(f"⚠️  Warning: Could not generate image: {e}")
        print("   Prototype will use placeholder")
        image_filename = None
    
    # Build difficulty descriptions
    difficulty_info = {
        "easy": "Very friendly and helpful. You'd have to be rude to fail.",
        "medium": "Professional but cautious. Build rapport first.",
        "hard": "Suspicious and protective. Requires significant trust.",
    }
    
    # Create scenario context
    if not scenario:
        scenario = f"You encounter {npc_name} during your heist operation."
    
    # Determine output path
    if not output_file:
        output_file = f"prototype/{name_safe}_chat.html"
    
    # Generate HTML with setup screen and hybrid interaction
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Heist - {npc_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: #0D0517;
            color: #FFFFFF;
            padding: 20px;
            line-height: 1.5;
        }}
        
        .container {{
            max-width: 480px;
            margin: 0 auto;
        }}
        
        .screen {{
            display: none;
        }}
        
        .screen.active {{
            display: block;
        }}
        
        /* Setup Screen */
        .setup-header {{
            text-align: center;
            margin-bottom: 32px;
        }}
        
        .setup-header h1 {{
            font-size: 32px;
            font-weight: bold;
            color: #B565FF;
            margin-bottom: 8px;
        }}
        
        .setup-header p {{
            font-size: 14px;
            color: #B0B0B0;
        }}
        
        .card {{
            background: #1A0F2E;
            border: 1px solid #3A2550;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
        }}
        
        .card-header {{
            font-size: 12px;
            font-weight: 600;
            color: #888888;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
        }}
        
        .character-preview {{
            text-align: center;
            margin-bottom: 24px;
        }}
        
        .character-image {{
            width: 200px;
            height: 200px;
            border-radius: 12px;
            border: 3px solid #B565FF;
            margin: 0 auto 12px;
            display: block;
            object-fit: cover;
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
        
        .form-group {{
            margin-bottom: 16px;
        }}
        
        .form-label {{
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: #B0B0B0;
            margin-bottom: 8px;
        }}
        
        .form-input {{
            width: 100%;
            background: #2A1A45;
            border: 1px solid #3A2550;
            border-radius: 8px;
            padding: 12px;
            color: #FFFFFF;
            font-size: 14px;
            font-family: inherit;
        }}
        
        .form-input:focus {{
            outline: none;
            border: 2px solid #B565FF;
            box-shadow: 0 0 0 3px rgba(181, 101, 255, 0.1);
        }}
        
        .difficulty-options {{
            display: flex;
            gap: 8px;
            margin-top: 8px;
        }}
        
        .difficulty-option {{
            flex: 1;
            padding: 12px;
            background: #2A1A45;
            border: 2px solid #3A2550;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: all 0.15s;
        }}
        
        .difficulty-option:hover {{
            border-color: #B565FF;
        }}
        
        .difficulty-option.selected {{
            border-color: #B565FF;
            background: rgba(181, 101, 255, 0.1);
        }}
        
        .difficulty-option .diff-name {{
            font-size: 14px;
            font-weight: 600;
            color: #FFFFFF;
            margin-bottom: 4px;
        }}
        
        .difficulty-option .diff-desc {{
            font-size: 11px;
            color: #888888;
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
            box-shadow: none;
        }}
        
        .button.secondary:hover {{
            border-color: #B565FF;
            color: #B565FF;
        }}
        
        /* Chat Screen */
        .chat-header {{
            display: flex;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 16px;
            border-bottom: 1px solid #3A2550;
        }}
        
        .chat-header-image {{
            width: 60px;
            height: 60px;
            border-radius: 8px;
            border: 2px solid #B565FF;
            margin-right: 12px;
            object-fit: cover;
        }}
        
        .chat-header-info {{
            flex: 1;
        }}
        
        .chat-header-name {{
            font-size: 18px;
            font-weight: bold;
            color: #FFFFFF;
        }}
        
        .chat-header-role {{
            font-size: 12px;
            color: #B0B0B0;
        }}
        
        .objective-section {{
            background: #2A1A45;
            border: 2px solid #B565FF;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
        }}
        
        .objective-header {{
            font-size: 12px;
            font-weight: 600;
            color: #D199FF;
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
        
        /* Quick Responses */
        .quick-responses {{
            margin-bottom: 16px;
        }}
        
        .quick-responses-header {{
            font-size: 12px;
            font-weight: 600;
            color: #888888;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}
        
        .quick-response-button {{
            width: 100%;
            background: #2A1A45;
            color: #FFFFFF;
            border: 1px solid #3A2550;
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 13px;
            text-align: left;
            cursor: pointer;
            transition: all 0.15s;
            margin-bottom: 8px;
        }}
        
        .quick-response-button:hover {{
            border-color: #B565FF;
            background: rgba(181, 101, 255, 0.1);
        }}
        
        .quick-response-button:active {{
            transform: scale(0.98);
        }}
        
        .divider {{
            display: flex;
            align-items: center;
            text-align: center;
            margin: 16px 0;
        }}
        
        .divider::before,
        .divider::after {{
            content: '';
            flex: 1;
            border-bottom: 1px solid #3A2550;
        }}
        
        .divider span {{
            padding: 0 12px;
            font-size: 12px;
            color: #888888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
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
        <!-- Setup Screen -->
        <div id="setupScreen" class="screen active">
            <div class="setup-header">
                <h1>🎭 THE HEIST</h1>
                <p>NPC Interaction Prototype</p>
            </div>
            
            <div class="character-preview">
                {f'<img src="{image_filename}" alt="{npc_name}" class="character-image">' if image_filename else '<div style="width: 200px; height: 200px; background: #2A1A45; border: 3px solid #B565FF; border-radius: 12px; margin: 0 auto 12px; display: flex; align-items: center; justify-content: center; color: #888888;">No image</div>'}
                <div class="character-name">{npc_name}</div>
                <div class="character-role">{npc_role}</div>
            </div>
            
            <div class="card">
                <div class="card-header">Scenario</div>
                <div style="font-size: 14px; color: #FFFFFF; line-height: 1.6;">
                    {scenario}
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">Your Objective</div>
                <div style="font-size: 14px; color: #FFFFFF; line-height: 1.6;">
                    {objective}
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">Gemini API Key</label>
                <input 
                    type="password" 
                    id="apiKeyInput" 
                    class="form-input" 
                    placeholder="Enter your API key..."
                    value=""
                >
                <div style="font-size: 11px; color: #888888; margin-top: 4px; display: flex; justify-content: space-between; align-items: center;">
                    <span>Get your key from <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color: #B565FF;">Google AI Studio</a></span>
                    <button 
                        onclick="clearSavedApiKey(event)" 
                        style="background: none; border: none; color: #FF6B9D; font-size: 11px; cursor: pointer; text-decoration: underline; padding: 0;"
                    >
                        Clear Saved Key
                    </button>
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">Difficulty</label>
                <div class="difficulty-options">
                    <div class="difficulty-option" data-difficulty="easy">
                        <div class="diff-name">Easy</div>
                        <div class="diff-desc">Helpful</div>
                    </div>
                    <div class="difficulty-option selected" data-difficulty="medium">
                        <div class="diff-name">Medium</div>
                        <div class="diff-desc">Cautious</div>
                    </div>
                    <div class="difficulty-option" data-difficulty="hard">
                        <div class="diff-name">Hard</div>
                        <div class="diff-desc">Suspicious</div>
                    </div>
                </div>
                <div style="font-size: 12px; color: #888888; margin-top: 8px;" id="difficultyDesc">
                    {difficulty_info['medium']}
                </div>
            </div>
            
            <button id="startButton" class="button" onclick="startConversation()">
                Start Conversation
            </button>
        </div>
        
        <!-- Chat Screen -->
        <div id="chatScreen" class="screen">
            <div class="chat-header">
                {f'<img src="{image_filename}" alt="{npc_name}" class="chat-header-image">' if image_filename else ''}
                <div class="chat-header-info">
                    <div class="chat-header-name">{npc_name}</div>
                    <div class="chat-header-role">{npc_role}</div>
                </div>
            </div>
            
            <div class="objective-section">
                <div class="objective-header">🎯 Your Objective</div>
                <div class="objective-text">{objective}</div>
            </div>
            
            <div class="chat-container" id="chatContainer"></div>
            
            <div id="statusContainer"></div>
            
            <!-- Quick Responses -->
            <div class="quick-responses" id="quickResponses" style="display:none;">
                <div class="quick-responses-header">Quick Responses</div>
                <div id="quickResponseButtons"></div>
            </div>
            
            <div class="divider"><span>or type your own</span></div>
            
            <!-- Free-form Input -->
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
    </div>
    
    <script>
        const NPC_NAME = "{npc_name}";
        const NPC_ROLE = "{npc_role}";
        const OBJECTIVE_INFO = "{objective_info}";
        
        const difficultyDescriptions = {{
            easy: "{difficulty_info['easy']}",
            medium: "{difficulty_info['medium']}",
            hard: "{difficulty_info['hard']}"
        }};
        
        const npcPrompts = {{
            easy: `You are {npc_name}, a {npc_role}. You are very friendly and helpful.

The player is trying to learn: {objective}
The answer is: {objective_info}

You will naturally reveal this information through friendly conversation. Be helpful and share details willingly. You enjoy chatting and helping people.`,
            
            medium: `You are {npc_name}, a {npc_role}. You are professional but cautious.

The player is trying to learn: {objective}
The answer is: {objective_info}

You will reveal this information if the player builds rapport and asks the right questions. You're not immediately suspicious, but you don't volunteer sensitive information to strangers. If they're polite and clever, you'll share what you know.`,
            
            hard: `You are {npc_name}, a {npc_role}. You are suspicious and protective of information.

The player is trying to learn: {objective}
The answer is: {objective_info}

You are VERY protective of this information. You will only reveal it if the player builds significant trust over multiple exchanges and has a convincing reason. If they seem suspicious, you shut down.`
        }};
        
        let API_KEY = '';
        let DIFFICULTY = 'medium';
        let conversationHistory = [];
        let gameOver = false;
        let systemPrompt = '';
        
        // Load saved API key from localStorage on page load
        window.addEventListener('DOMContentLoaded', function() {{
            const savedApiKey = localStorage.getItem('theheist_gemini_api_key');
            if (savedApiKey) {{
                document.getElementById('apiKeyInput').value = savedApiKey;
            }}
            
            // Load saved difficulty preference
            const savedDifficulty = localStorage.getItem('theheist_difficulty');
            if (savedDifficulty) {{
                DIFFICULTY = savedDifficulty;
                document.querySelectorAll('.difficulty-option').forEach(opt => {{
                    opt.classList.remove('selected');
                    if (opt.dataset.difficulty === savedDifficulty) {{
                        opt.classList.add('selected');
                        document.getElementById('difficultyDesc').textContent = difficultyDescriptions[savedDifficulty];
                    }}
                }});
            }}
        }});
        
        // Setup screen handlers
        document.querySelectorAll('.difficulty-option').forEach(option => {{
            option.addEventListener('click', function() {{
                document.querySelectorAll('.difficulty-option').forEach(opt => opt.classList.remove('selected'));
                this.classList.add('selected');
                DIFFICULTY = this.dataset.difficulty;
                document.getElementById('difficultyDesc').textContent = difficultyDescriptions[DIFFICULTY];
                // Save difficulty preference
                localStorage.setItem('theheist_difficulty', DIFFICULTY);
            }});
        }});
        
        function clearSavedApiKey(event) {{
            event.preventDefault();
            localStorage.removeItem('theheist_gemini_api_key');
            document.getElementById('apiKeyInput').value = '';
            alert('Saved API key cleared');
        }}
        
        function startConversation() {{
            API_KEY = document.getElementById('apiKeyInput').value.trim();
            
            if (!API_KEY) {{
                alert('Please enter your Gemini API key');
                return;
            }}
            
            // Save API key to localStorage
            localStorage.setItem('theheist_gemini_api_key', API_KEY);
            
            systemPrompt = npcPrompts[DIFFICULTY];
            
            document.getElementById('setupScreen').classList.remove('active');
            document.getElementById('chatScreen').classList.add('active');
            
            addNPCMessage(getGreeting());
            generateQuickResponses();
        }}
        
        function getGreeting() {{
            const greetings = [
                "Hey there. Can I help you with something?",
                "Hello. What brings you here?",
                "Good to see you. What's up?",
            ];
            return greetings[Math.floor(Math.random() * greetings.length)];
        }}
        
        async function generateQuickResponses() {{
            // Generate 3 contextual quick response options
            const context = conversationHistory.length > 0 
                ? conversationHistory.map(msg => 
                    `${{msg.role === 'user' ? 'Player' : NPC_NAME}}: ${{msg.parts[0].text}}`
                  ).join('\\n')
                : 'Conversation just started';
            
            const prompt = `Based on this conversation with {npc_name} ({npc_role}), generate 3 short response options (max 10 words each) that the player could say next.
Make them varied: one direct, one friendly/rapport-building, one clever/indirect.
Return ONLY 3 responses, one per line, no numbering.

Context:
${{context}}

Player's goal: {objective}`;
            
            try {{
                const response = await fetch(
                    `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key=${{API_KEY}}`,
                    {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{
                            contents: [{{ parts: [{{ text: prompt }}] }}],
                            generationConfig: {{
                                temperature: 0.8,
                                maxOutputTokens: 100,
                            }}
                        }})
                    }}
                );
                
                const data = await response.json();
                if (data.candidates && data.candidates[0]) {{
                    const responsesText = data.candidates[0].content.parts[0].text;
                    const responses = responsesText.split('\\n').filter(r => r.trim()).slice(0, 3);
                    displayQuickResponses(responses);
                }}
            }} catch (error) {{
                console.error('Error generating quick responses:', error);
            }}
        }}
        
        function displayQuickResponses(responses) {{
            const container = document.getElementById('quickResponseButtons');
            container.innerHTML = '';
            
            responses.forEach(response => {{
                const button = document.createElement('button');
                button.className = 'quick-response-button';
                button.textContent = response.trim();
                button.onclick = () => sendQuickResponse(response.trim());
                container.appendChild(button);
            }});
            
            document.getElementById('quickResponses').style.display = 'block';
        }}
        
        function sendQuickResponse(text) {{
            document.getElementById('playerInput').value = text;
            sendMessage();
        }}
        
        async function sendMessage() {{
            if (gameOver) return;
            
            const input = document.getElementById('playerInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            addPlayerMessage(message);
            input.value = '';
            
            toggleInput(false);
            document.getElementById('quickResponses').style.display = 'none';
            showLoading();
            
            conversationHistory.push({{
                role: 'user',
                parts: [{{ text: message }}]
            }});
            
            try {{
                const npcResponse = await getNPCResponse(message);
                hideLoading();
                addNPCMessage(npcResponse);
                
                conversationHistory.push({{
                    role: 'model',
                    parts: [{{ text: npcResponse }}]
                }});
                
                await checkIfInfoRevealed();
                await generateQuickResponses();
                
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
            
            if (data.candidates && data.candidates[0]) {{
                return data.candidates[0].content.parts[0].text;
            }}
            
            throw new Error('No response from API');
        }}
        
        async function checkIfInfoRevealed() {{
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
            document.getElementById('quickResponses').style.display = 'none';
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
            document.getElementById('quickResponses').style.display = 'none';
            toggleInput(true);
            addNPCMessage(getGreeting());
            generateQuickResponses();
        }}
        
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        
        document.getElementById('playerInput').addEventListener('keypress', (e) => {{
            if (e.key === 'Enter' && !e.shiftKey) {{
                e.preventDefault();
                sendMessage();
            }}
        }});
    </script>
</body>
</html>
'''
    
    # Write to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content)
    
    print(f"\n✅ Generated NPC prototype!")
    print(f"💾 Saved to: {output_path}")
    print(f"\n🎮 Open in browser: {output_path.absolute()}")
    print(f"🎭 Character: {npc_name} ({npc_role})")
    print(f"🎯 Objective: {objective}")
    print(f"💪 Default difficulty: {difficulty} (can change in setup)")
    print()
    
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description='Generate NPC interaction prototype HTML files (V2)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_npc_prototype_v2.py --name "Vincent Cole" --role "Casino Manager" \\
    --objective "Find the vault access code" --info "4-digit code: 7392"
  
  python generate_npc_prototype_v2.py --name "Dr. Sarah Chen" --role "Art Curator" \\
    --objective "Learn the painting's location" --info "Third floor, east wing" \\
    --gender female --ethnicity "Asian" --clothing "elegant dress"
        """
    )
    
    parser.add_argument('--name', required=True, help='NPC name')
    parser.add_argument('--role', required=True, help='NPC role/job')
    parser.add_argument('--objective', required=True, help='What player needs to learn')
    parser.add_argument('--info', required=True, help='The critical information to extract')
    
    parser.add_argument('--scenario', default='', help='Scenario context')
    parser.add_argument('--difficulty', default='medium', choices=['easy', 'medium', 'hard'])
    
    # Character appearance
    parser.add_argument('--gender', default='person', choices=['male', 'female', 'person'])
    parser.add_argument('--ethnicity', help='Character ethnicity')
    parser.add_argument('--clothing', help='What they wear')
    parser.add_argument('--background', help='Setting/background')
    parser.add_argument('--expression', default='neutral', help='Facial expression')
    parser.add_argument('--details', help='Additional visual details')
    parser.add_argument('--attitude', default='neutral', help='Personality vibe')
    
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
