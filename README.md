# Ads API — aiohttp

REST API для управления объявлениями на **aiohttp + SQLAlchemy (async) + SQLite**.

## Структура проекта

```
├── app.py            # Приложение aiohttp, маршруты, обработчики
├── models.py         # Модель Advertisement (SQLAlchemy 2.0 async)
├── requirements.txt
├── Dockerfile
└── README.md
```

## Установка и запуск (без Docker)

```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

pip install -r requirements.txt
python app.py
```

Сервер запустится на `http://0.0.0.0:8080`.

## Запуск через Docker (задание 2)

```bash
# Собрать образ
docker build -t ads-api .

# Запустить контейнер
docker run -d -p 8080:8080 --name ads-api ads-api

# Проверить работу
curl http://localhost:8080/api/ads
```

## Эндпоинты

| Метод  | URL                | Описание                    |
|--------|--------------------|-----------------------------|
| POST   | /api/ads           | Создать объявление          |
| GET    | /api/ads           | Получить все объявления     |
| GET    | /api/ads/`<id>`    | Получить объявление по ID   |
| PUT    | /api/ads/`<id>`    | Обновить объявление         |
| DELETE | /api/ads/`<id>`    | Удалить объявление          |

## Примеры запросов

### Создать объявление

```bash
curl -X POST http://localhost:8080/api/ads \
  -H "Content-Type: application/json" \
  -d '{"title": "Продам велосипед", "description": "Горный, б/у", "owner": "Иван"}'
```

### Создать без owner (подставится "anonymous")

```bash
curl -X POST http://localhost:8080/api/ads \
  -H "Content-Type: application/json" \
  -d '{"title": "Продам велосипед", "description": "Горный, б/у"}'
```

### Получить все объявления

```bash
curl http://localhost:8080/api/ads
```

### Получить по ID

```bash
curl http://localhost:8080/api/ads/1
```

### Обновить

```bash
curl -X PUT http://localhost:8080/api/ads/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Продам велосипед (срочно)"}'
```

### Удалить

```bash
curl -X DELETE http://localhost:8080/api/ads/1
```

Успешное удаление возвращает пустой ответ со статусом `204 No Content`.

## Модель данных

| Поле        | Тип      | Обязательное | Описание                              |
|-------------|----------|:------------:|---------------------------------------|
| id          | integer  | —            | Автоматически                         |
| title       | string   | ✓            | Заголовок объявления (макс. 200)      |
| description | text     | ✓            | Текст объявления                      |
| owner       | string   | —            | Владелец (по умолчанию `anonymous`)   |
| created_at  | datetime | —            | Время создания (UTC, ISO 8601)        |
