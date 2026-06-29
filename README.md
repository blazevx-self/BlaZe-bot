# BlaZe | Bot

## Description

BlaZe Bot is a Telegram RPG game built around character progression, combat mechanics, and an in-game economy system.

Players develop their characters through interactive commands, unlock abilities, evolve their Ghoul forms, and progress through a rank-based system tied to combat power.

---

## Features

- Persistent character progression with long-term growth
- Combat system based on stats, abilities, and kagune evolution
- In-game economy (BlazeCoins) used for upgrades and progression
- Ghoul transformation system with randomized kagune types and unique buffs
- Coffee mechanic with risk/reward system, debuffs, and achievements
- Achievement system tied to gameplay milestones (e.g. Coffee Master)
- Rank system based on calculated combat power
- Interactive stat upgrade system with direct gameplay impact
- Modular backend structure focused on scalability and extension
- Async Telegram bot with fast, event-driven interactions
- Logging system for gameplay and system-level events

---

## Tech Stack

- Python 3.13+
- aiogram 3.x
- asyncio
- PostgreSQL(production) / SQLite(development)
- SQLAlchemy
- Docker

---

## Project Structure

### bot/
Telegram interface layer:
- routers
- middleware
- filters
- keyboards
- ui rendering

### routers/
Feature-based routing system:
- ghoul
- game
- common
- (future: group, moderation)

### services/
Business logic layer:
- game mechanics
- ghoul system
- shared logic
- system processing

### database/
Data access layer:
- models
- repositories
- schemas

### core/
Shared system kernel:
- constants
- enums
- exceptions
- responses
- templates

### configs/
Application configuration files

---

## How to Run

```bash
pip install -r requirements.txt
python -m app.__main__
```

---

## Environment Variables

```
## Environment Variables

- TOKEN
- ADMIN_ID
- DATABASE_URL
```

---

## Gameplay

BlaZe | Bot is a Telegram-based RPG system where players continuously develop their character, increase their strength, and shape their progression inside the game world.

The core gameplay loop is built around:

- earning BlazeCoins through in-game actions and commands  
- upgrading character stats and overall power  
- obtaining and evolving Kagune with different mechanics and bonuses  
- participating in rankings and competitive leaderboards  
- choosing a personal development path as a Ghoul

The entire system is designed around long-term progression, where every action has a direct impact on the player's strength, status, and position in the game world.

---

## Status

The project is currently in active development.
New features, gameplay mechanics, and system improvements are being added regularly.

The architecture is continuously evolving to support long-term scalability and new game systems.

---

## Roadmap

- PvP combat system between players  
- Guild / group system for social gameplay  
- Expanded combat mechanics and balance rework  
- UI/UX improvements for in-game interactions  
- Telegram Mini App integration (future expansion)
- Admin panel
- Daily rewards
- Inventory
- Items
- Craft / Alchemy

---

## Author

- Developer: https://t.me/blazevx  
- Channel: https://t.me/+H67pSJL-qYU5Y2Qy

---

## Acknowledgements

Inspired by Telegram RPG bots such as CheStor | Bot and anime universes like Tokyo Ghoul.

---

## License

This project is for personal and educational use.

---

## Final Note

BlaZe | Bot is a long-term project that will continue to evolve with new mechanics, systems, and gameplay ideas.

Thank you for checking it out.
