# Sa Fona — Project Guide

## Overview
Sa Fona is a 2D retro side-scrolling platformer with combat, built with **Pygame (Python)**. Set across the Balearic Islands through different historical eras, the player controls Ramon, a grumpy talayotic slinger cursed into time-traveling with his myotragus companion Bep.

## Tech Stack
- **Framework**: Pygame (Python)
- **Resolution**: 320x180 or 384x216 (pixel-perfect, scaled up)
- **Target**: 60 FPS, PC (keyboard + gamepad)
- **Art**: 16-bit pixel art (SNES era)

## Language
- Code, documentation, and commits in **English**
- Game content uses English with **Balearic local terms** for character names, place names, cultural references, and historical terms (Catalan/Mallorquin)

## Development Practices
- **Docstrings**: Google style
- **Testing**: Small, concise tests for all implementations
- **Git**: Worktrees and feature branches; meaningful commits; PR-based workflow
- **Communication**: GitHub Issues for deliverables and user requests
- **Reviews**: PRs reviewed by Senior Engineer (En Pau) and Software Architect (En Miquel)
- **Iteration limits**: Max 3 rounds for Auditor-PM feedback and for PR review cycles
- **Assets**: Use simple placeholder shapes during development; easily swappable with real assets later

## Key Documents
- `game_design_document_draft.md` — Original GDD draft
- `docs/game_design_document.md` — Polished GDD (created by En Biel)
- `docs/software_architecture.md` — Architecture (created by En Miquel)
- `docs/implementation_roadmap.md` — Living roadmap (maintained by Na Francina)

## Team Roster

| Agent | Role | Primary Responsibility |
|-------|------|----------------------|
| **En Biel** | Game Director | GDD, mechanics design, level synergies, learning curve |
| **En Miquel** | Software Architect | Architecture, modularity, component design, PR review |
| **Na Francina** | Project Manager | Deliverables, roadmap, task assignment, verification |
| **N'Aina** | Auditor | Process efficiency, dependency analysis, implementation order |
| **En Pau** | Senior Software Engineer | Code quality, PR review, best practices enforcement |
| **N'Andreu** | Engine Programmer | Core engine, game systems implementation |
| **En Tomeu** | Level Designer | Level implementation, map layouts, world content |
| **Na Margalida** | Graphic Designer & Pixel Artist | Pixel art assets, visual design |
| **Na Catalina** | Narrative Writer | Dialogue, story, narrative content |

## Development Workflow
1. En Biel refines GDD from draft
2. En Miquel creates software architecture from GDD
3. Na Francina breaks architecture into incremental deliverables
4. N'Aina audits plan for inefficiencies (max 3 iterations with PM)
5. Na Francina assigns deliverables, updates roadmap
6. Developers implement (N'Andreu, En Tomeu)
7. En Pau + En Miquel review PRs (max 3 review rounds)
8. Na Francina verifies deliverable works (runs the game)
9. User signs off via GitHub Issues

## Running the Game
The game runs via pygame. When running for verification or user testing, always print the display/connection info. The user connects via **code tunnel** and needs the port info to access the game window.

## Asset Pipeline
- Development uses simple geometric shapes as placeholders
- All assets stored in `assets/` with clear subdirectories
- Na Margalida creates real assets when requested by user
- AI-generated content requires explicit user permission (cost consideration)
- Assets must be hot-swappable (change file, no code changes)
