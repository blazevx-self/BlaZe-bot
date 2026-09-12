# Архитектура BlaZe Bot

Модульная архитектура с разделением на слои: Telegram-слой, бизнес-логика, данные.
Цель — чтобы игровые механики можно было менять независимо друг от друга.

```
app/
├── assets/        # шрифты, словари, статические данные
├── bot/           # Telegram-слой: routers, filters, middlewares, keyboards
├── configs/       # настройки окружения и игровые константы
├── core/          # constants, enums, exceptions, templates
├── database/      # models, repositories, mappers
├── services/      # бизнес-логика
├── types/         # entities и services_result
├── utils/         # мелкие переиспользуемые функции
├── containers.py  # Dependency Injection
└── __main__.py    # точка входа

migrations/        # Alembic-миграции
logs/               # логи, разделены по доменам
```

## Поток запроса

```
Telegram → Middleware → Filter → Router → Service → Repository → PostgreSQL
                                              │
                                              ├──► Template  (текст ответа)
                                              └──► Keyboard  (интерфейс)
```

Не каждый запрос проходит все звенья — простая команда может обойтись без
Keyboard, операция без БД — без Repository.

## Слои и их ответственность

| Слой | Где | За что отвечает | Чего не делает |
|---|---|---|---|
| **Router** | `bot/routers/` | принимает Telegram-событие, вызывает Service, отправляет ответ | не содержит бизнес-логику |
| **Filter** | `bot/filters/` | решает, подходит ли событие под хендлер (админ? есть гуль? только группа?) | не выполняет бизнес-логику |
| **Middleware** | `bot/middlewares/` | сквозное поведение: сессия БД, антифлуд, бан, логирование | не привязано к конкретному Router |
| **Keyboard** | `bot/keyboards/` | строит Telegram-клавиатуры | не содержит игровую логику |
| **Service** | `services/` | бизнес-правила конкретного домена (лотерея, гули, кофе, кагуне...) | не зависит от Router, не знает про Telegram |
| **Repository** | `database/repositories/` | SQL-запросы и работа с ORM | не знает про Telegram/UI |
| **Model** | `database/models/` | структура таблиц (SQLAlchemy ORM) | не содержит бизнес-логику |
| **Mapper** | `database/mappers/` | превращает ORM (`UserOrm`) в доменные сущности (`UserData`) | — |
| **Template** | `core/templates/` | текст сообщений пользователю | не содержит логику |
| **Entities / Results** | `types/` | типизированные структуры (`UserData`, `BanResult`, ...) вместо словарей | — |

Routers, Services, Repositories, Templates, Keyboards и Constants разбиты по
одинаковым доменам (`game`, `ghoul`, `admin`, `tops`...) — так проще находить
всё, что относится к одной игровой механике.

## Примеры по паттернам

**Расчёты отдельно от сервиса**, если механика математически нетривиальна:
```
services/ghouls/stats/
├── stats_service.py            # взаимодействие с механикой
└── calculate_stats_service.py  # чистые расчётные правила
```

**Генерация файлов отдельно от бизнес-логики:**
```
services/game/lottery/
├── lottery_service.py           # игровая логика лотереи
└── lottery_video_generator.py   # рендер видео результата
```

## Dependency Injection

`app/containers.py` собирает Repository → Service → Router, чтобы Router не
создавал зависимости вручную.

## Миграции

Схема БД версионируется через Alembic (`migrations/`) — изменения структуры
PostgreSQL проходят миграциями, без ручного `create_all()` в проде.

## Принципы

- Separation of Concerns, Single Responsibility.
- Минимум логики в Router — вся бизнес-логика в Service.
- Repository — единственная точка доступа к БД.
- ORM-модели не покидают слой `database` — наружу идут `entities`/`services_result`.
- Общие механизмы (антифлуд, бан, логирование) — через Middleware, а не дублируются в Router'ах.