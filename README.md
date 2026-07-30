# code_docs

Веб-приложение для хранения и автоматической генерации документации к исходному коду. Пользователи загружают файлы проектов, а система разбирает их структуру и формирует читаемое описание кода. Состоит из FastAPI-бэкенда и React-фронтенда.

## Возможности

- Загрузка файлов проекта и автоматический разбор их структуры
- Генерация документации к коду с подсветкой синтаксиса (Monaco Editor)
- JWT-аутентификация с регистрацией и входом
- Управление проектами: создание, просмотр, удаление
- Хранение документации в базе данных (SQLite / PostgreSQL)
- REST API с автодокументацией через FastAPI

## Стек

### Бэкенд
- Python 3.12 (образ `python:3.12-slim`)
- [FastAPI](https://fastapi.tiangolo.com/) — REST API
- SQLAlchemy 2 — ORM и работа с БД
- PyJWT + bcrypt + passlib — аутентификация и хеширование паролей
- python-dotenv — загрузка секретов из `.env`
- uvicorn — ASGI-сервер
- Docker + Docker Compose — контейнеризация и запуск

### Фронтенд
- React 19
- Material UI 7 — компоненты интерфейса
- Monaco Editor — редактор с подсветкой кода
- React Router 7 — маршрутизация
- Axios — HTTP-клиент

## Структура

```
code_docs/
├── backend/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── app/
│       ├── main.py              # FastAPI-приложение, подключение роутеров
│       ├── config.py            # Настройки из .env
│       ├── database.py          # Подключение к БД, Base, engine
│       ├── requirements.txt
│       ├── .env.example
│       ├── models/              # SQLAlchemy-модели
│       ├── schemas/             # Pydantic-схемы
│       ├── routers/             # Эндпоинты: auth, users, projects, files, docs
│       ├── services/            # Бизнес-логика и парсинг кода
│       └── utils/               # Вспомогательные утилиты
└── frontend/
    ├── package.json
    └── src/
        ├── App.js               # Корневой компонент, маршруты
        ├── api/                 # Axios-клиенты для каждого ресурса
        ├── components/          # Переиспользуемые компоненты
        ├── contexts/            # React Context (Auth и др.)
        └── pages/               # Страницы приложения
```

## Запуск

### Бэкенд

Бэкенд запускается через Docker Compose. Образ собирается локально из `Dockerfile`.

1. Скопируйте `.env.example` в `.env` и заполните значения:

```bash
cd backend
cp app/.env.example app/.env
```

2. Соберите и запустите контейнер:

```bash
docker compose up -d --build
```

Контейнер `code-docs-backend` запустится и будет автоматически перезапускаться (`restart: unless-stopped`).

API будет доступен по адресу `http://localhost:3001/code-docs/api`.  
Автодокументация: `http://localhost:3001/docs`.

> Порт `3001` на хосте проброшен на порт `3000` внутри контейнера.

#### Остановка

```bash
docker compose down
```

### Фронтенд

```bash
cd frontend
npm install
npm start
```

Приложение откроется на `http://localhost:3000`.

## Переменные окружения

См. файл `backend/app/.env.example`. Переменные передаются в контейнер через `env_file` в `docker-compose.yml`.

| Переменная | Описание | Значение по умолчанию |
|---|---|---|
| `SECRET_KEY` | Секрет для подписи JWT | — (обязательно) |
| `ADMIN_EMAIL` | Email администратора | `admin@codedocs.example` |
| `DATABASE_URL` | URL базы данных | `sqlite:///./code_docs.db` |
| `ALGORITHM` | Алгоритм подписи JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_HOURS` | Время жизни токена (часы) | `3000` |
