# Architecture Overview

## System Design

BlaZe | Bot - is built using a modular service-based architecture.

### Layers

- Bot Layer → Telegram interaction (handlers, middleware)
- Service Layer → Game logic and mechanics
- Database Layer → Data storage and repositories
- Core Layer → Shared system components

---

## Flow

User → Bot → Router → Middleware → Service → Repository → Database
