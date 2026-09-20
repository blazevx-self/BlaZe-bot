# BlaZe | Telegram RPG Bot

Telegram RPG-бот с атмосферой «Токийского гуля», вдохновлён ботом @chestor —
механики переосмыслены и переписаны своим кодом, не скопированы.

Игрок развивает гуля, качает характеристики, получает кагуне, поднимается
в рейтингах. Цель проекта — полноценная RPG-экономика внутри Telegram.

## Технологии

- Python 3.13+, Aiogram 3.x, Asyncio
- PostgreSQL + SQLAlchemy
- Docker

## Архитектура

Слои: 
- Telegram (`bot/`) 
- бизнес-логика (`services/`)
- база данных (`database/`)

Подробности — в [ARCHITECTURE.md](ARCHITECTURE.md).

## Запуск

1. Скопируй `.env.example` в `.env` и заполни переменные (см. ниже).
2. Подними контейнеры:
```bash
   docker compose up -d --build
```

Поднимутся бот, PostgreSQL и pgAdmin (`http://localhost:5050`).

```bash
docker compose ps            # статус контейнеров
docker compose logs -f bot   # логи бота
docker compose down          # остановить
```

## Конфигурация

- `.env` — секреты и параметры окружения
- `app/configs/config.yaml` — тексты бота
- `app/configs/game.py` — игровые настройки 

```env
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_database_name

PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=your_pgadmin_password

BOT_TOKEN=your_bot_token
ADMIN_ID=[123456789,987654321]

DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}

TELEGRAPH_ACCESS_TOKEN=your_telegraph_access_token
TELEGRAPH_PAGE_PATH=your_telegraph_page_path

BACKUP_CHANNEL_ID=your_telegram_channel_id
BACKUP_DIR=your_folder
```

## Возможности

**Пользователь** — `/quiz` (викторина, 15/день), `/wordle`, «Депнуть» (лотерея,
5 цветов, ставка 100–1 000 000), профиль и баланс, `/set_rp`/`/all_rp`/`/del_rp`
(свои RP-команды в чате, до 20 штук).

**Гуль** — «Щёлк» и «Пить кофе» (фарм валюты, у кофе есть передоз при
злоупотреблении), «Растить кагуне» (4 типа, рандом + прокачка), «Качаца»
(прокачка характеристик, только в ЛС), топы по каждой механике.

**Чат** — администраторы настраивают правила, приветствие и прощание для
участников.

**Администратор** — бан/разбан в личке бота, изменение баланса и полей
пользователя, просмотр профилей, сброс прогресса игрока или гуля.

Полное описание каждой команды — в статье `/help` внутри самого бота.

## Автор

- **Разработчик** — [@blazevx](https://t.me/blazevx)
- **Канал** — [@blazevx_self](https://t.me/blazevx_self)