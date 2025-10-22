# 📮 Appeals Bot

Telegram-бот для работы с обращениями граждан.  
Позволяет пользователям отправлять обращения в комиссии, прикреплять файлы, отслеживать статус и получать уведомления об изменениях.

---

## 🚀 Основные возможности

### 👤 Пользователи
- Отправка обращений в выбранную комиссию.  
- Прикрепление фото или документов к обращению.  
- Просмотр статуса своих обращений в реальном времени.  
- Получение уведомлений о смене статуса.  

### 🛠 Администраторы
- Управление обращениями (изменение статусов, просмотр истории).  
- Управление комиссиями (создание, редактирование, удаление).  
- Управление пользователями (активация, блокировка).  
- Одобрение заявок на получение административных прав.  

---

## 🧱 Архитектура

Проект представляет собой единый контейнеризованный сервис — Telegram-бот на **Python 3.12**, использующий:

- [aiogram 3.x](https://docs.aiogram.dev/) — Telegram API фреймворк  
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/) — ORM для работы с БД  
- [Alembic](https://alembic.sqlalchemy.org/) — управление миграциями  
- [asyncpg](https://github.com/MagicStack/asyncpg) — асинхронный драйвер PostgreSQL  
- [pydantic-settings](https://docs.pydantic.dev/latest/usage/pydantic_settings/) — загрузка `.env`  
- [loguru](https://github.com/Delgan/loguru) — удобное логирование  
- [uv](https://github.com/astral-sh/uv) — быстрый пакетный менеджер  

Хранение данных — **PostgreSQL**, оркестрация контейнеров — **Docker Compose**.  
Миграции применяются автоматически при запуске контейнера.

---

## 🗂 Структура проекта

```
appeals-bot/
├─ app/
│  ├─ core/              # Настройки и логирование
│  │  ├─ settings.py
│  │  └─ logging.py
│  ├─ db/                # Работа с базой данных
│  │  ├─ base.py
│  │  ├─ models.py
│  │  ├─ session.py
│  │  └─ repositories.py
│  ├─ services/          # Доменные сервисы
│  ├─ telegram/          # Telegram-бот
│  │  ├─ main.py
│  │  ├─ keyboards.py
│  │  ├─ states/
│  │  └─ routers/
│  └─ utils/             # Утилиты и форматирование
├─ alembic/              # Миграции Alembic
│  ├─ env.py
│  └─ versions/
├─ docker-compose.yml
├─ Dockerfile
├─ pyproject.toml
├─ uv.lock
├─ .env.example
└─ README.md
```

---

## ⚙️ Настройка окружения

Создайте файл `.env` на основе примера `.env.example`:

```env
POSTGRES_DB=appeals
POSTGRES_USER=app
POSTGRES_PASSWORD=app
DATABASE_URL=postgresql+asyncpg://app:app@db:5432/appeals

BOT_TOKEN=000000000:YOUR_TELEGRAM_BOT_TOKEN
ADMIN_IDS=123456789
```

---

## 🐳 Запуск через Docker Compose

```bash
docker compose up -d --build
```

Контейнеры:
- **db** — PostgreSQL 16  
- **migrate** — применение миграций Alembic  
- **bot** — Telegram-бот (aiogram 3)

Проверить логи:
```bash
docker compose logs -f bot
```

---

## 🧩 Миграции

Создание новой миграции:
```bash
docker compose run --rm bot uv run alembic revision --autogenerate -m "add field"
```

Применение миграций:
```bash
docker compose run --rm bot uv run alembic upgrade head
```

Просмотр истории:
```bash
docker compose run --rm bot uv run alembic history
```

---

## 🧠 Ключевые концепции

### 1. ORM-модели
Все модели наследуются от `Base` (app/db/base.py), что обеспечивает общий `metadata` и корректную работу Alembic.

### 2. `relationship` vs `ForeignKey`
- `ForeignKey` — связь на уровне SQL (ограничение).  
- `relationship` — связь на уровне ORM (Python-объекты, ленивые связи).

### 3. `AppealStatus (StrEnum)`
Определяет допустимые статусы обращения и обеспечивает типовую безопасность.  
Enum автоматически сериализуется в строку при передаче через API или сохранении в БД.

### 4. FSM в aiogram
Используется конечный автомат состояний для пошагового сбора обращения:
```
choose_commission → ask_contact → ask_text → ask_file → done
```

---

## 🧾 Логирование

- В коде приложения используется **loguru** (stdout, уровень INFO).  
- Alembic использует стандартный `logging`, это отдельный процесс и не конфликтует с loguru.  

---

## 🧰 Запуск без Docker

```bash
uv sync
uv run alembic upgrade head
uv run python -m app.telegram.main
```

---

## 📜 Лицензия

MIT License © 2025
