# Reports Application

## Описание

Данное приложение состоит из фронтенд-интерфейса, сервиса аутентификации (Keycloak) и API-сервиса для работы с отчётами. Аутентификация настроена с использованием PKCE (Proof Key for Code Exchange), а доступ к API ограничен ролями пользователей.

## Структура проекта

```
/project-root
│
├── API               # Код API на FastAPI
│   ├── main.py       # Основной файл API
│   ├── Dockerfile    # Dockerfile для API
│   └── requirements.txt  # Зависимости для API
│
├── frontend          # Код фронтенда (React)
│   ├── Dockerfile    # Dockerfile для фронтенда
│   └── ...
│
├── keycloak          # Конфигурация Keycloak
│   └── realm-export.json  # Экспортированная конфигурация реалма
│
├── docker-compose.yml  # Файл для запуска всех сервисов
└── README.md           # Инструкция по запуску проекта
```

## Требования

- Docker
- Docker Compose

## Установка и запуск

1. **Клонируйте репозиторий:**

```bash
git clone <URL-репозитория>
cd <папка-проекта>
```

2. **Соберите и запустите контейнеры:**

```bash
docker-compose up --build
```

3. **Проверка работы сервисов:**
   - **Фронтенд:** [http://localhost:3000](http://localhost:3000)
   - **Keycloak Admin Console:** [http://localhost:8080](http://localhost:8080)
     - Логин: `admin`
     - Пароль: `admin`
   - **API-сервис:** [http://localhost:8000/reports](http://localhost:8000/reports)

## Аутентификация и Роли

1. **Аутентификация через фронтенд:**
   - Перейдите по адресу [http://localhost:3000](http://localhost:3000) и выполните вход.

2. **Доступ к API:**
   - API `/reports` доступен только пользователям с ролью `prothetic_user`.
   - Проверка токенов осуществляется через Keycloak.

## Переменные окружения

### Для API:

- `KEYCLOAK_URL` — URL сервиса Keycloak (по умолчанию `http://keycloak:8080`)
- `KEYCLOAK_REALM` — имя реалма (по умолчанию `reports-realm`)

### Для фронтенда:

- `REACT_APP_API_URL` — URL API сервиса (по умолчанию `http://localhost:8000`)
- `REACT_APP_KEYCLOAK_URL` — URL сервиса Keycloak (по умолчанию `http://keycloak:8080`)
- `REACT_APP_KEYCLOAK_REALM` — имя реалма (по умолчанию `reports-realm`)
- `REACT_APP_KEYCLOAK_CLIENT_ID` — ID клиента Keycloak (по умолчанию `reports-frontend`)

## Тестирование

Для проверки работы API используйте следующий запрос с токеном доступа:

```bash
curl -H "Authorization: Bearer <ваш_токен>" http://localhost:8000/reports
```

При успешной валидации токена и наличии роли `prothetic_user` вы получите данные отчёта.

## Проблемы и отладка

1. **Проверка логов контейнеров:**

```bash
docker-compose logs keycloak
```
```bash
docker-compose logs backend
```

2. **Повторная сборка при изменениях:**

```bash
docker-compose down
docker-compose up --build
```
