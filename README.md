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
- Python 3.10+
- [FastAPI](https://fastapi.tiangolo.com/) — REST API
- SQLAlchemy 2 — ORM и работа с БД
- PyJWT + bcrypt + passlib — аутентификация и хеширование паролей
- python-dotenv — загрузка секретов из `.env`
- uvicorn — ASGI-сервер

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
│   ├── main.py                  # Точка входа (uvicorn)
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py              # FastAPI-приложение, подключение роутеров
│       ├── config.py            # Настройки из .env
│       ├── database.py          # Подключение к БД, Base, engine
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

1. Скопируйте `.env.example` в `.env` и заполните значения:

```bash
cd backend
cp .env.example .env
```

2. Установите зависимости и запустите сервер:

```bash
pip install -r requirements.txt
python main.py
```

API будет доступен по адресу `http://localhost:8000/code-docs/api`.
Автодокументация: `http://localhost:8000/docs`.

### Фронтенд

```bash
cd frontend
npm install
npm start
```

Приложение откроется на `http://localhost:3000`.

## Переменные окружения

См. файл `backend/.env.example`.

| Переменная | Описание | Значение по умолчанию |
|---|---|---|
| `SECRET_KEY` | Секрет для подписи JWT | — (обязательно) |
| `ADMIN_EMAIL` | Email администратора | `admin@codedocs.example` |
| `DATABASE_URL` | URL базы данных | `sqlite:///./code_docs.db` |
| `ALGORITHM` | Алгоритм подписи JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_HOURS` | Время жизни токена (часы) | `3000` |
