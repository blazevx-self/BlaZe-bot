# BlaZe | Telegram RPG Bot

## Описание

BlaZe | Bot — Telegram RPG-бот вдохновлённым аниме "Токийский гуль" и ботом @chestor.

Игрок развивается в игровом мире, улучшает характеристики, получает кагуне, повышает свою силу и занимает место в рейтингах.

Основная идея проекта — создание полноценной RPG-системы внутри Telegram с механиками развития персонажа, экономики и дальнейшего расширения игрового мира.

---

# Технологии

- Python 3.13+
- Aiogram 3.x
- Asyncio
- PostgreSQL 
- SQLAlchemy 
- Docker 

---

# Архитектура проекта

Проект построен по модульной архитектуре с разделением ответственности между слоями.

Основные компоненты:
```
app/
├── bot/          # Telegram слой: роутеры, middleware, клавиатуры
├── services/     # Бизнес-логика игры
├── database/     # Работа с базой данных
├── core/         # Константы, шаблоны, enums
├── configs/      # Конфигурация приложения
├── types/        # Типизированные структуры данных
└── utils/        # Вспомогательные инструменты
```
Подробнее архитектура описана в:

ARCHITECTURE.md
---

# Запуск

Проект запускается с помощью Docker и Docker Compose.

### 1. Создайте `.env`

Скопируйте `.env.example` в `.env` и укажите необходимые значения переменных окружения.

### 2. Запустите проект

```bash
docker compose up -d --build
```

Docker автоматически создаст и запустит необходимые контейнеры:

* Telegram-бот;
* PostgreSQL;
* pgAdmin.

### 3. Проверка

```bash
docker compose ps
```

Для просмотра логов бота:

```bash
docker compose logs -f bot
```

### 4. Остановка

```bash
docker compose down
```

Для повторного запуска:

```bash
docker compose up -d
```

pgAdmin доступен на `http://localhost:5050`.


---

# Конфигурация

Для работы проекта используются:

- `.env` — секретные и окруженческие параметры;
- `config.yaml` — текста бота.
- `game_config.py` — игровая настройка проекта

Пример переменных окружения находится в `.env.example`.

Основные параметры `.env`:

```env
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_database_name

PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=your_pgadmin_password

BOT_TOKEN=your_bot_token
ADMIN_ID=your_telegram_id

DATABASE_URL="postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}"

TELEGRAPH_ACCESS_TOKEN=your_telegraph_access_token
TELEGRAPH_PAGE_PATH=your_telegraph_page_path
```

---

# Игровой мир

Игровая часть проекта построена вокруг развития персонажа.

Игрок может:

- развивать своего гуля;
- увеличивать боевую мощь и ранг опасности;
- получать новые формы кагуне;
- улучшать характеристики;
- участвовать в рейтингах;
- открывать новые игровые механики.

Полное описание игрового лора находится отдельно в виде статьи.

---

# Автор

#### Developer: https://t.me/blazevx

#### Channel: https://t.me/blazevx_self
