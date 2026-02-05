# The Crew - Project Overview

**Chapter 1: Heist**

A collaborative role-driven game where 2-5 players work together in real-time, each taking on specialized roles to complete team missions.

## Core Features

- **Real-time multiplayer**: WebSocket-based coordination between players
- **Role-based gameplay**: 12 unique roles (Mastermind, Hacker, Safe Cracker, Driver, etc.)
- **Dynamic heists**: AI-generated scenarios with unique task dependencies
- **Mini-games**: Role-specific challenges (lock picking, hacking, etc.)
- **NPC interactions**: LLM-powered conversations with guards, staff, etc.
- **Time pressure**: Complete objectives before security catches on

## Game Concept

**"The Crew"** is a franchise of collaborative mission games where players take on specialized roles to complete objectives together. Each chapter features a different theme and setting:

- **Chapter 1: Heist** - Crime crew pulling off elaborate robberies (current)
- **Chapter 2: Voyage** - Spaceship crew managing crises and exploration
- **Chapter 3: Frontier** - Old West posse tackling frontier challenges
- **Chapter 4+** - Pirate crew, special ops team, etc.

## Tech Stack

### Frontend
- **Flutter Web**: Cross-platform UI (mobile-first design)
- **WebSockets**: Real-time game state synchronization
- **Dark theme**: Noir/heist aesthetic with Borderlands art style

### Backend
- **FastAPI**: Python REST API + WebSocket server
- **Google Gemini**: AI for NPC conversations and experience generation
- **Google Imagen**: Character portraits and scenario images
- **In-memory state**: Room/game state management

### AI/ML
- **Gemini 2.5 Flash**: Experience generation (scenarios, NPCs, tasks)
- **Gemini 2.0 Flash Lite**: Real-time NPC dialogue during gameplay
- **Imagen 4.0**: High-quality character portraits (Borderlands style)
- **Imagen 3.0 Fast**: Quick NPC and object illustrations

## Project Structure

```
TheCrew/
├── app/                    # Flutter frontend
│   ├── lib/
│   │   ├── screens/       # UI screens (landing, lobby, game)
│   │   ├── services/      # WebSocket, API clients
│   │   └── widgets/       # Reusable UI components
├── backend/               # Python FastAPI backend
│   ├── app/
│   │   ├── api/          # REST + WebSocket endpoints
│   │   ├── services/     # Game logic, NPC conversations
│   │   └── models/       # Data models (rooms, players, tasks)
│   ├── scripts/          # Content generation tools
│   └── experiences/      # Playable experience files
├── shared_data/          # Shared configuration (roles, scenarios)
├── design/               # UI mockups, design system
└── image_playground/     # Standalone image generator tool
```
