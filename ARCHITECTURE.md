# Архитектура BlaZe

Модульная слоистая архитектура: Telegram-слой, бизнес-логика, данные.
Цель — чтобы игровые механики можно было менять и добавлять независимо друг от друга.

## Структура

```
app/
├── assets/        # шрифты, словари, вопросы викторины, медиа и серии (вне git)
├── bot/           # Telegram-слой: routers, filters, middlewares, keyboards
├── configs/       # настройки окружения, игровой баланс, тексты (yaml)
├── core/          # constants, enums, exceptions, templates
├── database/      # models, repositories, mappers
├── services/      # бизнес-логика
├── types/         # entities и services_result
├── utils/         # мелкие переиспользуемые функции
├── containers.py  # Dependency Injection
└── __main__.py    # точка входа

migrations/        # Alembic-миграции
logs/              # логи, разделены по доменам, ротация по дням
```

## Поток запроса

```
Telegram → Middleware → Filter → Router → Service → Repository → PostgreSQL
                                   │          │
                                   │          ├──► Template  (текст ответа)
                                   │          └──► Result    (статус + данные)
                                   └──► Keyboard (интерфейс)
```

Не каждый запрос проходит все звенья: простая команда обходится без Keyboard,
операция без БД — без Repository.

## Слои и их ответственность

| Слой | Где | За что отвечает | Чего не делает |
|---|---|---|---|
| **Middleware** | `bot/middlewares/` | сквозное поведение для всех событий | не привязано к конкретному Router |
| **Filter** | `bot/filters/` | подходит ли событие хендлеру (админ? есть гуль? группа?) | не выполняет бизнес-логику |
| **Router** | `bot/routers/` | принимает событие, вызывает Service, отправляет ответ | не содержит бизнес-логику |
| **Keyboard** | `bot/keyboards/` | строит inline-клавиатуры | не содержит игровую логику |
| **Service** | `services/` | бизнес-правила домена | не знает про Telegram и Router |
| **Repository** | `database/repositories/` | SQL-запросы и работа с ORM | не знает про UI и бизнес-правила |
| **Model** | `database/models/` | структура таблиц (SQLAlchemy ORM) | не содержит логику |
| **Mapper** | `database/mappers/` | ORM (`UserOrm`) → сущность (`UserData`) | — |
| **Template** | `core/templates/` | сборка текста сообщений | не содержит логику |
| **Entities / Results** | `types/` | типизированные структуры вместо словарей | — |

Routers, Services, Repositories, Templates, Keyboards и Constants разбиты по
одинаковым доменам (`admin`, `chat`, `common`, `game`, `ghoul`, `tops`) — всё,
что относится к одной механике, находится по одному пути.

## Middleware

| Middleware | Назначение |
|---|---|
| `database` | открывает сессию БД на событие, коммит или откат |
| `sync_entities` | создаёт и обновляет пользователя, чат и участника чата |
| `ban` | не пропускает забаненных в боте |
| `antiflood` | ограничивает частоту команд одного пользователя |
| `antispam_for_chats` | флуд-лимит в группах: предупреждения → мут (в памяти) |
| `link_filter` | удаляет ссылки от новых участников, мут при повторе |
| `message_counter` | считает сообщения участников чата |
| `logging` | логирует команды и время обработки |

## Результаты сервисов

Сервис не бросает исключения на игровые ситуации и не возвращает словари.
Он возвращает dataclass со статусом:

```python
@dataclass
class SnapResult:
    status: ResultStatus
    text: str | None = None
    remaining: int | None = None
```

Роутер смотрит на `status` (`SUCCESS`, `COOLDOWN`, `NOT_ENOUGH_MONEY`...) и
только отображает результат. Исключения остаются для настоящих ошибок,
их перехватывает общий error-router и отправляет администратору.

## Примеры по паттернам

**Расчёты отдельно от сервиса**, если механика математически нетривиальна:
```
services/ghouls/stats/
├── stats.py            # сценарий прокачки: проверки, запись, ответ
└── calculate_stats.py  # чистые функции: цена, лимиты, доступность
```

**Генерация файлов отдельно от бизнес-логики:**
```
services/game/lottery/
├── lottery.py                   # игровая логика лотереи
└── lottery_video_generator.py   # рендер видео результата

services/game/wordle/
├── wordle.py     # логика игры
└── renderer.py   # отрисовка поля в картинку
```

**Общие механики — отдельными сервисами**, которые используют другие:
- `CooldownService` — кулдауны всех действий в одной таблице, атомарный `claim`
- `MediaService` — медиатека и кэш `file_id`
- `utils/effects.py` — временные эффекты бонуса (множители кулдаунов и цен)

## Хранение данных

| Что | Где | Почему |
|---|---|---|
| Игроки, гули, чаты, кулдауны, история | PostgreSQL | основное состояние |
| Временные эффекты | JSONB-поле `users.effects` | без отдельной таблицы и фоновых задач |
| GIF и видео | `app/assets/media/` + `file_id` в БД | файл загружается в Telegram один раз |
| Серии для `/anime` | `app/assets/anime/` (volume) | большие файлы вне git и образа |
| Антиспам, лимиты AI | память (TTLCache) | данные живут секунды-минуты |
| Тексты | `config.yaml` | правка текстов без изменения кода |

## Dependency Injection

`app/containers.py` собирает Repository → Service, роутеры получают сервисы
через `Provide[...]`. Ресурсоёмкие сервисы с общим состоянием (семафоры,
кэши) объявлены как `Singleton`.

## Миграции

Схема БД версионируется через Alembic. В продакшене миграции применяются
отдельным контейнером при остановленном боте, перед этим делается бэкап.

## Деплой

```
VPS (Ubuntu)
└── Docker Compose
    ├── bot         # aiogram, long polling
    ├── postgres    # данные в именованном volume
    ├── migrations  # alembic upgrade head
    └── pgadmin     # доступ только через SSH-туннель
```

Бэкапы базы автоматически отправляются в закрытый Telegram-канал.
Ошибки приходят администратору в личные сообщения с трейсбеком.

## Принципы

- Separation of Concerns, Single Responsibility
- Минимум логики в Router — бизнес-логика в Service
- Repository — единственная точка доступа к БД
- ORM-модели не покидают слой `database`, наружу идут `entities` и `services_result`
- Общие механизмы — через Middleware, а не копипастой в роутерах
- Игровой баланс и тексты вынесены в конфиги, а не захардкожены