<div align="center">

<img src="app/assets/photo/banner.jpg" alt="BlaZe | Bot" width="720">

# ⚡ BlaZe | Bot

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=3500&pause=900&color=E8E8E8&center=true&vCenter=true&width=640&lines=%D0%98%D0%B3%D1%80%D0%B0+%D0%B2+Telegram+%D0%BF%D0%BE+%D0%BC%D0%BE%D1%82%D0%B8%D0%B2%D0%B0%D0%BC+%D0%A2%D0%BE%D0%BA%D0%B8%D0%B9%D1%81%D0%BA%D0%BE%D0%B3%D0%BE+%D0%B3%D1%83%D0%BB%D1%8F;%D0%9A%D0%B0%D0%B3%D1%83%D0%BD%D0%B5+%C2%B7+%D1%81%D1%82%D0%B0%D1%82%D1%8B+%C2%B7+%D0%BC%D0%B8%D0%BD%D0%B8-%D0%B8%D0%B3%D1%80%D1%8B;%D0%9C%D0%BE%D0%B4%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D1%8F+%D1%87%D0%B0%D1%82%D0%BE%D0%B2+%C2%B7+AI-c%D0%BE%D0%B1%D0%B5%D1%81%D0%B5%D0%B4%D0%BD%D0%B8%D0%BA)](https://t.me/BlaZev2_bot)

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3-2AABEE?logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[![Try Bot](https://img.shields.io/badge/TRY%20BOT-@BlaZev2__bot-2AABEE?style=for-the-badge&logo=telegram)](https://t.me/BlaZev2_bot)
[![Author](https://img.shields.io/badge/AUTHOR-@blazevx-111111?style=for-the-badge&logo=telegram)](https://t.me/blazevx)
[![Channel](https://img.shields.io/badge/CHANNEL-@blazevx__self-E4405F?style=for-the-badge&logo=telegram)](https://t.me/blazevx_self)

Продакшен на VPS · сентябрь 2026 · один разработчик  
Вдохновлён [@chestor](https://t.me/chestor) — механики написаны с нуля

<br>

<img src="https://skillicons.dev/icons?i=python,postgres,docker,linux,git" alt="stack">

</div>

---

## 🧬 Что такое BlaZe | Bot?

**BlaZe | Bot** — игра в Telegram по мотивам вселенной «Токийского гуля».

Ты пишешь боту, становишься гулем и живёшь в той же экономике, что и остальные: фармишь BlaZeCoin, щелкаешь, пьёшь кофе, пробуждаешь кагуне, качаешь статы, раз в день открываешь бонус. В группах это не отдельный «игровой режим», а тот же бот: модерация, RP, брак с общим балансом, поздравление с др, викторина, Wordle, лотерея.

Гуль качается неделями, чат при этом остаётся живым. Автор — BlaZe Self.

---

## ✨ Возможности

| 🎮 | Что умеет |
|---|---|
| 🫰 Щелк / ☕ кофе | Фарм валюты, кулдауны, передоз кофе |
| 🦠 Кагуне | 4 типа, шанс при пробуждении, платная прокачка |
| 💪 Статы | Сила, ловкость, скорость, HP, реген; цена растёт экспонентой |
| 🎁 Ежедневный бонус | 5 коробок: деньги, сброс кд, ускорения, скидки, редкие эффекты |
| 💸 Переводы и топы | BlaZeCoin между игроками, рейтинги по механикам |
| 💍 Семья | Брак в чате, общий баланс, развод 50/50 |
| 🎂 День рождения | `/birthday`, поздравление в лс и в чатах, где ты есть |
| 🧠 Мини-игры | Викторина, Wordle (картинка), лотерея (видео), `/anime` |
| 🛡 Модерация | бан / мут / кик / варны, `/report`, история, антиспам, фильтр ссылок |
| 👋 Чаты | приветствия, прощания, правила, свои RP-команды, «бот …» |
| 🤖 AI | Реплай на бота — ответ с характером (DeepSeek) |
| 👑 Админка | баланс, поля, бан в боте, рассылка, сброс, `/add_gif`, логи ошибок |

---

## 🏗 Как устроено

Около **280 Python-модулей**. Слои: роутер не пишет SQL, репозиторий не знает про Telegram. Подробно — [ARCHITECTURE.md](ARCHITECTURE.md).

```text
Update → Middleware → Router → Service → Repository → PostgreSQL
```

- Сервис возвращает `dataclass` + `ResultStatus`, не словарь и не traceback игроку
- Кулдауны в БД с атомарным `claim` — двойной клик не выдаст награду дважды
- Эффекты — JSONB с временем истечения, без лишней таблицы
- Медиатека: файл один раз, дальше `file_id`
- ffmpeg для `/anime` — семафор и таймаут, бот не встаёт колом
- Middleware: сессия БД, синхронизация людей и чатов, бан, антифлуд, логи
- Дампы Postgres уходят в Telegram-канал по расписанию

**Стек:** Python 3.14 · aiogram 3 · asyncio · PostgreSQL · SQLAlchemy 2 · Alembic · dependency-injector · pydantic-settings · aiohttp · ffmpeg · Pillow · Docker · Telegraph · DeepSeek

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,postgres,docker,linux,git" alt="stack">
</p>

---

## 🚀 Запуск

```bash
cp .env.example .env
docker compose up -d --build
```

Поднимаются бот, PostgreSQL, pgAdmin (`http://localhost:5050`) и миграции.

```bash
docker compose ps
docker compose logs -f bot
docker compose run --rm migrations
docker compose down
```

---

<details>
<summary><b>🔑 Переменные среды</b></summary>

```env
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

PGADMIN_EMAIL=
PGADMIN_PASSWORD=

BOT_TOKEN=
ADMIN_IDS=

DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}

TELEGRAPH_ACCESS_TOKEN=
TELEGRAPH_PAGE_PATH=

BACKUP_CHANNEL_ID=
BACKUP_DIR=

API_KEY=
AI_BASE_URL=
AI_MODEL=
```

| Переменная | Зачем |
|---|---|
| `BOT_TOKEN` | [@BotFather](https://t.me/BotFather) |
| `ADMIN_IDS` | Telegram ID админов, через запятую |
| `DATABASE_URL` | async-доступ к Postgres |
| `TELEGRAPH_*` | статья помощи |
| `BACKUP_*` | дамп БД в канал |
| `API_KEY` / `AI_*` | нейросеть на реплай; пусто — бот без AI |

⚠️ Секреты в публичный репозиторий не клади.

</details>

Тексты — `app/configs/config.yaml`. Конфигурация игровых настроек — `app/configs/game.py`.

---

## 💬 Ссылки

[![Bot](https://img.shields.io/badge/BOT-@BlaZe2__bot-2AABEE?logo=telegram)](https://t.me/BlaZe2_bot)
[![Author](https://img.shields.io/badge/AUTHOR-@blazevx-black?logo=telegram)](https://t.me/blazevx)
[![Channel](https://img.shields.io/badge/CHANNEL-@blazevx__self-red?logo=telegram)](https://t.me/blazevx_self)
