# Architecture Overview

## System Design

BlaZe Bot is built using a modular service-oriented architecture.

### Layers

- Bot Layer → Telegram handlers, routers, middlewares
- Service Layer → Business logic and game mechanics
- Database Layer → Repositories, models and persistence
- Core Layer → Shared components, constants, templates and utilities

---

## Request Flow

User → Telegram Bot → Router → Middleware → Service → Repository → Database
