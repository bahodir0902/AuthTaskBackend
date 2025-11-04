
## 🔐 Auth Task Backend

> Готовый сервис аутентификации и авторизации, построенный на Django REST Framework, PostgreSQL, Redis и Celery.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.x-red.svg)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-Latest-red.svg)](https://redis.io/)


## 🌐 Живой Сайт этой программы

* **Swagger (документация API):** [http://13.53.73.97:8009/](http://13.53.73.97:8009/)
* **Админ-панель:** [http://13.53.73.97:8009/admin](http://13.53.73.97:8009/admin)

## Видео-обзор

### Обзор системы аутентификации

[Смотреть демо](https://youtu.be/oWUvEWSYCeE)

Это подробная видео-демонстрация полного цикла аутентификации: регистрация пользователей, подтверждение email, реализация многофакторной аутентификации (MFA), восстановление пароля, смена email и дополнительные механизмы безопасности. Каждая часть показана на живых примерах, подчёркивая надёжность системы и архитектуру безопасности.

### Обзор системы авторизации

[Смотреть демо](https://youtu.be/TLRYm7g2qtY)

Демонстрация покрывает систему авторизации на основе ролей (RBAC): настройку правил доступа, модели прав и практическое применение. На живых примерах показано, как разные роли взаимодействуют с ресурсами, как работают детальные разрешения и их применение на различных эндпоинтах API.

## 📋 Обзор

Полноценный backend аутентификации и авторизации с JWT-аутентификацией, MFA, RBAC и продвинутыми механизмами безопасности. Идеален для современных веб-приложений, которым нужен надёжный менеджмент пользователей и тонкая настройка прав.

### 🔎 Авторизация одним взглядом (итоговая матрица)

| Роль    | Список            | Получение            | Создать | Обновить                 | Удалить                  |
| ------- | ----------------- | -------------------- | ------- | ------------------------ | ------------------------ |
| guest   | 401               | 401                  | 401     | 401                      | 401                      |
| user    | 200 (только свои) | 200 свои / 404 чужие | 201     | 200 свои / 404 чужие     | 204 свои / 404 чужие     |
| manager | 200 (все)         | 200 любые            | 201     | 200 свои / **403** чужие | 204 свои / **403** чужие |
| admin   | 200 (все)         | 200 любые            | 201     | 200 любые                | 204 любые                |

### 🔑 Модель авторизации (кратко)

**Resource** (`code`, `name`, `description`) — реестр защищённых ресурсов (например, `"orders"`).

**AccessRule** (`role`, `resource`, `read_own`, `read_all`, `create`, `update_own`, `update_all`, `delete_own`, `delete_all`) — набор разрешений для роли на ресурс.

**Orders** — демо-модель для демонстрации правил доступа.

Во вью установлен `access_resource = "orders"`.
`HasResourcePermission` ищет `AccessRule` пользователя по этому ресурсу и применяет:

* **List/Retrieve** → `read_all` или `read_own` (+ проверка владельца для объектных маршрутов)
* **Create** → `create`
* **Update** → `update_all` или `update_own` (+ проверка владельца)
* **Delete** → `delete_all` или `delete_own` (+ проверка владельца)

Администраторы проходят без проверок.

* Если выдан только `read_own`, queryset ограничивается собственными записями пользователя ⇒ объекты других пользователей невидимы (**404**).
* Если есть `read_all`, но `update_all`/`delete_all` — **False**, читать чужие можно, изменять — нельзя ⇒ при записи **403**.

### ✨ Ключевые возможности

**Слой аутентификации**

* 🎫 Кастомная реализация JWT (Access + Refresh токены)
* 🔄 Автоматическая ротация refresh-токена с занесением старого в blacklist
* 📧 Аутентификация по email/паролю
* 🔐 Многофакторная аутентификация (MFA/OTP)
* 🔑 Сброс пароля и смена email
* 📨 Система приглашений пользователей
* 🚪 Выход из текущего устройства и со всех устройств

**Слой авторизации**

* 👥 RBAC (доступ на основе ролей)
* 📊 Управление ресурсами и правилами
* 🎯 Гранулярные права (read_own, read_all, create, update_own, update_all, delete_own, delete_all)
* 🛡️ Классы разрешений DRF с маппингом действий

**Удобство для разработчика**

* 📚 Интерактивная документация Swagger/OpenAPI
* 🐳 Docker Compose
* Готовые пайплайны CI/CD
* 📬 Асинхронная отправка писем через Celery
* ⚡ Кэширование в Redis
* 🧪 Полный набор тестов на pytest
* 🚦 Ограничение частоты запросов на чувствительных эндпоинтах

---

## 🏗️ Архитектура

### Компоненты системы

```
┌─────────────────────────────────────────────────────────────┐
│                         Клиентский слой                     │
├─────────────────────────────────────────────────────────────┤
│  Web-фронтенд  │  Мобильное приложение  │  Сторонние сервисы │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                        Слой API-шлюза                       │
├─────────────────────────────────────────────────────────────┤
│  Django REST Framework + Swagger UI                         │
│  • Эндпоинты аутентификации                                 │
│  • Эндпоинты управления пользователями                      │
│  • Эндпоинты администрирования RBAC                         │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                   Слой бизнес-логики                        │
├─────────────────────────────────────────────────────────────┤
│  JWT-обработчик  │  Сервис OTP  │  Движок разрешений RBAC   │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                 Слой данных и кэша                          │
├──────────────────────────┬──────────────────────────────────┤
│  PostgreSQL              │  Redis                           │
│  • Данные пользователей  │  • OTP-коды                      │
│  • Токены                │  • Сессии                        │
│  • Правила RBAC          │  • Брокер Celery                 │
└──────────────────────────┴──────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│               Слой фоновых заданий                          │
├─────────────────────────────────────────────────────────────┤
│  Celery Workers                                             │
│  • Доставка писем                                           │
│  • Генерация OTP                                            │
└─────────────────────────────────────────────────────────────┘
```

### Поток аутентификации

**Жизненный цикл JWT-токенов**

* Access-токен: срок жизни 15 минут
* Refresh-токен: срок жизни 7 дней
* Автоматическая ротация при обновлении с добавлением старого в blacklist

**Безопасность MFA/OTP**

* Временные коды хранятся в Redis
* Хранение в виде хэша
* Счётчик максимальных попыток
* Автоматическое истечение

---

## 🛠️ Технологический стек

| Категория          | Технология            | Назначение                 |
| ------------------ | --------------------- | -------------------------- |
| **Core**           | Python 3.13           | Среда выполнения           |
|                    | Django 5.2.7          | Веб-фреймворк              |
|                    | Django REST Framework | Разработка API             |
| **База данных**    | PostgreSQL 16         | Основное хранилище         |
| **Кэш и очередь**  | Redis                 | Кэш и брокер сообщений     |
|                    | django-redis          | Интеграция с Django        |
|                    | Celery                | Очередь асинхронных задач  |
| **Аутентификация** | PyJWT                 | Работа с JWT-токенами      |
| **Документация**   | drf-spectacular       | Генерация OpenAPI/Swagger  |
| **Утилиты**        | CORS Headers          | Поддержка CORS             |
|                    | Whitenoise            | Раздача статических файлов |
| **Тестирование**   | pytest                | Фреймворк тестов           |

---

## 📁 Структура проекта

```
auth-task-backend/
│
├── core/                           # Конфигурация проекта
│   ├── settings.py                 # Основные настройки (JWT, Celery, Redis)
│   ├── settings_test.py            # Настройки для тестов
│   ├── urls.py                     # Корневой роутинг
│   └── celery.py                   # Инициализация Celery
│
├── apps/                           # Модули приложения
│   │
│   ├── users/                      # Управление пользователями
│   │   ├── auth/                   # Реализация JWT и OTP
│   │   ├── models/                 # Модели User, Profile, Token
│   │   ├── serializers/            # Сериализаторы DRF
│   │   ├── views/                  # API-представления
│   │   ├── service/                # Бизнес-логика и задачи Celery
│   │   └── signals/                # Сигналы Django
│   │
│   ├── accesses/                   # Авторизация (RBAC): ресурсы и правила
│   │   ├── models.py               # Модели Resource и AccessRule
│   │   ├── permissions.py          # Кастомные разрешения DRF
│   │   ├── serializers.py          # Сериализаторы RBAC
│   │   └── views.py                # Вью для управления RBAC
│   │
│   └── demo/                       # Временное демо-приложение
│       ├── models.py               # Модель Order (демо-задача)
│       ├── serializers.py          # OrderSerializer
│       └── views.py                # OrdersViewSet для демонстрации RBAC
│
├── tests/                          # Набор тестов
│   └── users/                      # Тесты приложения users
│
├── docs/                           # Документация
│   └── images/                     # Скриншоты и диаграммы
│
├── Dockerfile                      # Описание контейнера
├── docker-compose.yml              # Оркестрация мульти-контейнеров
├── entrypoint.sh                   # Стартовый скрипт контейнера
├── requirements.txt                # Зависимости Python
└── README.md                       # Этот файл
```

---

## 🚀 Быстрый старт

### Предварительные требования

* Docker & Docker Compose (рекомендуется)
* Python 3.13+ (для локальной разработки)
* PostgreSQL 16+ (если запускаете локально)
* Redis (если запускаете локально)

### Вариант A: Docker Compose (рекомендуется)

**Шаг 1: Настройка окружения**

Создайте файл `.env` в корне проекта:

```bash
# Django Configuration
SECRET_KEY=your-secret-key-change-in-production
DEBUG=1
DOMAIN_URL=http://localhost:8010
FRONTEND_URL=http://localhost:5173

# Database Configuration
DB_NAME=appdb
DB_USER=appuser
DB_PASSWORD=apppass
DB_HOST=host.docker.internal
DB_PORT=5432

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Email Configuration (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# OTP Configuration
OTP_LEN=6
TTL_SECONDS=300
MAX_ATTEMPTS=5

# Superuser Bootstrap
CREATE_SUPERUSER=1
DJANGO_SUPERUSER_EMAIL=admin@admin.com
DJANGO_SUPERUSER_PASSWORD=securepassword123
DJANGO_SUPERUSER_FIRST_NAME=Admin
```

**Шаг 2: Запуск сервисов**

```bash
docker compose up --build
```

**Шаг 3: Доступ к приложению**

* **API и Swagger UI**: [http://localhost:8010/](http://localhost:8010/)
* **Django Admin**: [http://localhost:8010/admin/](http://localhost:8010/admin/)

  * Email: `admin@admin.com`
  * Пароль: `securepassword123`

#### Опционально: PostgreSQL в Docker

Добавьте этот сервис в `docker-compose.yml`, если нужен контейнер PostgreSQL:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppass
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

Обновите переменные окружения:

```bash
DB_HOST=postgres
DB_PORT=5432
```

### Вариант B: Локальная разработка

**Шаг 1: Виртуальное окружение**

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Шаг 2: Настройка окружения**

```bash
export DJANGO_SETTINGS_MODULE=core.settings
# Скопируйте и настройте .env как показано выше
```

**Шаг 3: Инициализация базы**

```bash
python manage.py migrate
python manage.py createsuperuser
```

**Шаг 4: Запуск сервисов**

```bash
# Терминал 1: dev-сервер Django
python manage.py runserver 0.0.0.0:8010

# Терминал 2: worker Celery
celery -A core worker -l info

# Терминал 3: Redis (если не запущен)
redis-server
```

---

## 📖 Руководство по использованию

### Настройка RBAC

#### 1. Создание ресурсов

Перейдите в **Django Admin → Access → Resources** и создайте:

| Код      | Имя          | Описание                         |
| -------- | ------------ | -------------------------------- |
| `orders` | Orders       | Ресурс управления заказами       |
| `rules`  | Access Rules | Управление правилами RBAC        |

#### 2. Определение правил доступа

Перейдите в **Django Admin → Access → Access Rules** и настройте разрешения:

**Роль Admin — ресурс Orders**

```
Role: ADMIN
Resource: orders
Permissions: ALL enabled (read_own, read_all, create, update_own, update_all, delete_own, delete_all)
```

**Роль User — ресурс Orders**

```
Role: USER
Resource: orders
Permissions:
  ✓ read_own: True
  ✓ create: True
  ✓ update_own: True
  ✓ delete_own: False
  ✗ read_all: False
  ✗ update_all: False
  ✗ delete_all: False
```

**Роль Manager — ресурс Orders**

```
Role: MANAGER
Resource: orders
Permissions:
  ✓ read_own: True
  ✓ create: True
  ✓ update_own: True
  ✓ read_all: True
  ✓ delete_own: True
  ✗ update_all: False
  ✗ delete_all: False
```

**Роль Guest — ресурс Orders**

```
Role: Guest
Resource: orders
Permissions:
  ✗ read_own: False
  ✗ create: False
  ✗ update_own: False
  ✗ read_all: False
  ✗ delete_own: False
  ✗ update_all: False
  ✗ delete_all: False
```

#### 3. Создание демо-пользователей

В **Django Admin → Users** создайте тестовые учётные записи:

**User 1**

* Email: `user1@example.com`
* Role: `USER`
* Groups: `Users`
* Флаги: `is_active=True`, `email_verified=True`, `must_set_password=False`, `Let use set password=False` и поставьте пароль, например `12`

**User 2**

* Email: `user2@example.com`
* Role: `USER`
* Groups: `Users`
* Та же конфигурация, что и у User 1

### Интерактивное тестирование API (Swagger UI)

#### Сценарий 1: Неавторизованный доступ (401)

```
1. Откройте Swagger UI: http://localhost:8010/
2. Попробуйте GET /api/demo/orders/ без аутентификации
3. Результат: 401 Unauthorized
```

#### Сценарий 2: Успешные аутентификация и авторизация

```
1. POST /api/accounts/auth/login/
   Body: {
     "email": "user1@example.com",
     "password": "yourpassword"
   }

2. Скопируйте "access" токен из ответа

3. Нажмите "Authorize" в Swagger UI
   Введите: Bearer <your-access-token>

4. POST /api/demo/orders/
   Body: {
     "title": "My first order"
   }
   Result: 201 Created

5. GET /api/demo/orders/
   Result: 200 OK (отображаются только заказы user1)
```

#### Сценарий 3: Запрещённый доступ (403)

```
1. Войдите как admin и создайте заказ
2. Запомните ID заказа
3. Перевойдите как user1
4. Попробуйте GET /api/demo/orders/{admin-order-id}/
5. Результат: 403 Forbidden (user1 не владелец)
```

#### Сценарий 4: Доступ к собственным ресурсам (200)

```
1. От имени user1 создайте заказ
2. Запомните ID заказа
3. GET /api/demo/orders/{user1-order-id}/
4. Результат: 200 OK (user1 владелец)
```

---

## 🔄 Пользовательские сценарии

### Регистрация

```
1. POST /api/accounts/auth/register/
   → Система отправляет OTP на email через Celery

2. POST /api/accounts/auth/verify-registration/
   → Проверка OTP-кода
   → Возвращаются access и refresh токены
   → Пользователь автоматически авторизуется
```

### Вход

**Без MFA:**

```
POST /api/accounts/auth/login/
→ Мгновенно возвращаются access и refresh токены
```

**С MFA:**

```
1. POST /api/accounts/auth/login/
   → Система отправляет OTP на email

2. POST /api/accounts/auth/verify-otp/
   → Проверка OTP-кода
   → Возвращаются access и refresh токены
```

### Обновление токена

```
POST /api/accounts/auth/refresh/
Body: { "refresh": "your-refresh-token" }
→ Старый refresh вносят в blacklist и отзывают
→ Возвращаются новые access и refresh токены
```

### Выход из системы

**С одного устройства:**

```
POST /api/accounts/auth/logout/
Body: { "refresh": "your-refresh-token" }
→ В blacklist попадают и access, и refresh токены
```

**Со всех устройств:**

```
POST /api/accounts/auth/logout-of-all-devices/
→ Отзываются все refresh токены пользователя
→ Все активные сессии становятся недействительными
```

### Сброс пароля

```
1. POST /api/accounts/auth/forgot-password/
   Body: { "email": "user@example.com" }
   → Отправка OTP на email

2. POST /api/accounts/auth/verify-password-reset/
   Body: { "email": "...", "otp": "123456" }
   → Возвращаются uid и token

3. POST /api/accounts/auth/reset-password/
   Body: {
       "uid": "...",
       "token": "...",
       "new_password": "...",
       "re_new_password": "..."
   }
   → Пароль обновлён
```

### Смена email

```
1. POST /api/accounts/users/request-email-change/
   Body: { "new_email": "newemail@example.com" }
   → Отправка OTP на новый адрес

2. POST /api/accounts/users/confirm-email-change/
   Body: { "otp": "123456" }
   → Email обновлён
```

### Профиль

**Чтение профиля:**

```
GET /api/accounts/users/profile/
→ Возвращает данные профиля
```

**Обновление профиля:**

```
PUT/PATCH /api/accounts/users/update-profile/
Body: {
  "first_name": "John",
  "last_name": "Doe",
  "mfa_enabled": true,
  "birth_date": "1990-01-01",
  "phone_number": "+1234567890"
}
```

### Удаление аккаунта

```
DELETE /api/accounts/users/delete-account/
→ Мягкое удаление (is_active=False)
→ Пользователь больше не может войти
→ Все токены пользователя добавляются в blacklist и отзываются
→ Данные сохраняются в базе
```

---

## 🔐 Модель авторизации (RBAC)

### Базовые понятия

**Resource**

* Представляет защищаемую сущность в системе
* Примеры: orders, users, posts, comments
* Хранится в базе с уникальным кодом

**Access Rule**

* Связывает роль и ресурс с набором разрешений
* Определяет, какие операции разрешены

**Типы разрешений**

| Разрешение   | Область | Описание              |
| ------------ | ------- | --------------------- |
| `read_own`   | Свои    | Просмотр собственных  |
| `read_all`   | Все     | Просмотр всех         |
| `create`     | N/A     | Создание              |
| `update_own` | Свои    | Изменение собственных |
| `update_all` | Все     | Изменение всех        |
| `delete_own` | Свои    | Удаление собственных  |
| `delete_all` | Все     | Удаление всех         |

### Определение прав

**Маппинг действий:**

| Действие DRF | HTTP-метод | Требуемое разрешение          |
| ------------ | ---------- | ----------------------------- |
| `list`       | GET        | `read_all` или `read_own`     |
| `retrieve`   | GET        | `read_all` или `read_own`     |
| `create`     | POST       | `create`                      |
| `update`     | PUT/PATCH  | `update_all` или `update_own` |
| `destroy`    | DELETE     | `delete_all` или `delete_own` |

**Логика:**

1. Если у пользователя роль `ADMIN` → **полный доступ**
2. Если есть разрешение `*_all` → **доступ ко всем объектам**
3. Если есть `*_own`:

   * Сравнить `owner_field` объекта с `request.user`
   * Если совпадает → **разрешить**
   * Иначе → **запретить (403)**

### Пример реализации

```python
from apps.access.permissions import HasResourcePermission

class OrdersViewSet(viewsets.ModelViewSet):
    access_resource = "orders"
    queryset = Order.objects.select_related("user").all()
    serializer_class = OrderSerializer
```

### Примечания по реализации

В текущей демо-реализации используется жёстко заданный атрибут `access_resource` в `OrdersViewSet`, чтобы продемонстрировать работу RBAC для модели Order.

Для продакшена рекомендуется использовать `ContentType` Django: добавить `ForeignKey` на `ContentType` в модель `Resource` (как я комментировал), чтобы динамически связывать правила доступа с любой моделью. Тип модели можно выводить автоматически по queryset у viewset или по `Meta` сериализатора. Это даст универсальный слой авторизации, применимый ко всем моделям приложения.

Эта усовершенствованная реализация не включена из-за сроков, однако текущая версия полностью демонстрирует ключевые идеи RBAC и служит прочной основой для расширения.

---

## 🌐 Справочник API

### Эндпоинты аутентификации

**Базовый URL:** `/api/accounts/auth/`

| Эндпоинт                  | Метод | Описание                        | Аутентификация |
| ------------------------- | ----- | ------------------------------- | -------------- |
| `/login/`                 | POST  | Вход пользователя               | Нет            |
| `/refresh/`               | POST  | Обновление access-токена        | Нет            |
| `/register/`              | POST  | Старт регистрации               | Нет            |
| `/verify-registration/`   | POST  | Завершение регистрации          | Нет            |
| `/verify-otp/`            | POST  | Проверка кода MFA               | Нет            |
| `/forgot-password/`       | POST  | Запрос на сброс пароля          | Нет            |
| `/verify-password-reset/` | POST  | Проверка OTP для сброса         | Нет            |
| `/reset-password/`        | POST  | Установка нового пароля         | Нет            |
| `/logout/`                | POST  | Выход с одного устройства       | Требуется      |
| `/logout-of-all-devices/` | POST  | Выход со всех устройств         | Требуется      |
| `/set-initial-password/`  | POST  | Установка пароля по приглашению | Нет            |
| `/validate-invitation/`   | POST  | Проверка токена приглашения     | Нет            |

### Эндпоинты управления пользователями

**Базовый URL:** `/api/accounts/users/`

| Эндпоинт                 | Метод     | Описание            | Аутентификация |
| ------------------------ | --------- | ------------------- | -------------- |
| `/profile/`              | GET       | Получить профиль    | Требуется      |
| `/update-profile/`       | PUT/PATCH | Обновить профиль    | Требуется      |
| `/request-email-change/` | POST      | Запрос смены email  | Требуется      |
| `/confirm-email-change/` | POST      | Подтверждение смены | Требуется      |
| `/delete-account/`       | DELETE    | Мягкое удаление     | Требуется      |

### Эндпоинты администрирования RBAC

**Базовый URL:** `/api/access/`

| Эндпоинт           | Метод          | Описание            | Аутентификация | Права |
| ------------------ | -------------- | ------------------- | -------------- | ----- |
| `/resources/`      | GET            | Список ресурсов     | Требуется      | Admin |
| `/resources/`      | POST           | Создать ресурс      | Требуется      | Admin |
| `/resources/{id}/` | GET/PUT/DELETE | Управление ресурсом | Требуется      | Admin |
| `/rules/`          | GET            | Список правил       | Требуется      | Admin |
| `/rules/`          | POST           | Создать правило     | Требуется      | Admin |
| `/rules/{id}/`     | GET/PUT/DELETE | Управление правилом | Требуется      | Admin |

### Эндпоинты документации

| Эндпоинт   | Описание                                |
| ---------- | --------------------------------------- |
| `/`        | Swagger UI (интерактивная документация) |
| `/schema/` | OpenAPI-схема (JSON)                    |
| `/admin/`  | Интерфейс администрирования Django      |

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Запустить все тесты
pytest

# Подробный вывод
pytest -v

# Конкретный файл
pytest tests/users/test_auth.py

# С отчётом покрытия
pytest --cov=apps --cov-report=html
```

### Конфигурация тестов

Тесты используют `core.settings_test`:

* In-memory база SQLite
* Кэш в памяти
* Почтовый backend — консоль
* Celery в режиме eager (синхронно)

### Покрытие тестами

Набор тестов покрывает:

* ✅ Регистрацию пользователя
* ✅ Подтверждение email
* ✅ Вход (с MFA и без)
* ✅ Генерацию и проверку OTP
* ✅ Обновление и ротацию токенов
* ✅ Blacklisting токенов
* ✅ Выход (один и со всех устройств)
* ✅ Сброс пароля
* ✅ Смену email
* ✅ Управление профилем
* ✅ Мягкое удаление аккаунта
* ✅ Rate limiting на чувствительных эндпоинтах
* ✅ Проверки разрешений RBAC

### Написание новых тестов

```python
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_user_creation():
    user = User.objects.create_user(
        email='test@example.com',
        password='testpass123'
    )
    assert user.email == 'test@example.com'
    assert user.check_password('testpass123')
```

---

## 🔒 Соображения безопасности

### Безопасность JWT-токенов

**Рекомендации:**

* В этом проекте `JWT_SECRET` берётся из `SECRET_KEY`, но в реальной разработке в продакшене необходимо использовать отдельный `JWT_SECRET`, отличающийся от `SECRET_KEY`.

**Конфигурация:**

```python
# settings.py
JWT_SECRET = os.getenv('JWT_SECRET', SECRET_KEY)
JWT_ACCESS_TOKEN_LIFETIME = timedelta(minutes=15)
JWT_REFRESH_TOKEN_LIFETIME = timedelta(days=7)
```

### Безопасность OTP

**Реализация:**

* OTP-коды хэшируются перед сохранением
* Ограниченный срок действия (по умолчанию 5 минут)
* Счётчик максимальных попыток (5)
* Хранение в Redis (авто-истечение)
* Ограничение частоты на эндпоинтах OTP

### Безопасность паролей

**Встроенная защита Django:**

* Хэширование паролей PBKDF2
* Правила валидации паролей
* Проверка на популярные пароли

### Ограничение частоты запросов

**Защищённые эндпоинты:**

* Вход: 5 запросов/мин
* Регистрация: 3 запросов/мин
* Проверка OTP: 5 запросов/мин
* Сброс пароля: 3 запросов/мин

### Конфиденциальность данных

**Обращение с пользовательскими данными:**

* Мягкое удаление сохраняет данные для соответствия требованиям
* Персональные данные зашифрованы на уровне PostgreSQL
* Безопасные токены для сброса пароля
* OTP-коды не логируются

---

## ⚙️ Эксплуатация

### Роли контейнеров

Скрипт `entrypoint.sh` поддерживает два режима:

**Web-роль (`ROLE=web`)**

```bash
ROLE=web
→ Выполнить миграции
→ Собрать статические файлы
→ Запустить Gunicorn
```

**Worker-роль (`ROLE=worker`)**

```bash
ROLE=worker
→ Ожидание базы (опционально)
→ Выполнить миграции
→ Запустить Celery worker
```

### Архитектура развертывания

```
┌─────────────────┐
│   Load Balancer │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│ Web  │  │ Web  │  (несколько инстансов)
│ ROLE │  │ ROLE │
└───┬──┘  └──┬───┘
    │         │
    └────┬────┘
         │
    ┌────▼─────┐
    │ Database │
    │  Redis   │
    └────┬─────┘
         │
    ┌────▼────┐
    │ Worker  │  (процессы Celery)
    │  ROLE   │
    └─────────┘
```

### Мониторинг и логирование

**Где искать логи:**

* Логи приложения: `app.log`
* Консольный вывод: stdout/stderr
* Логи БД: через кастомный handler (apps.logs)

**Мониторинг Celery:**

```bash
# Активные задачи
celery -A core inspect active

# Статус воркеров
celery -A core inspect stats

# Зарегистрированные задачи
celery -A core inspect registered
```

### Масштабирование (планирую сделать в будущем)

**Горизонтальное масштабирование:**

* Web-инстансы: масштабировать за балансировщиком
* Celery-воркеры: масштабировать по длине очереди
* Redis: кластер Redis для высокой доступности
* PostgreSQL: реплики для чтения

**Оптимизация производительности:**

* Включить кэширование запросов в Redis
* Пулинг соединений (pgbouncer)
* Настройка Gunicorn: `workers = (2 * CPU_cores) + 1`
* CDN для статических файлов

### Стратегия бэкапов

**База данных:**

```bash
# Бэкап
pg_dump -U appuser -h localhost appdb > backup_$(date +%Y%m%d).sql

# Восстановление
psql -U appuser -h localhost appdb < backup_20251103.sql
```

**Redis:**

```bash
# Persistency Redis
# В redis.conf:
save 900 1
save 300 10
save 60 10000
```

---

## 🎥 Медиа и документация

### Скриншоты

Документация содержит визуальные материалы по:

* Интерфейсу Swagger UI
* Панели Django Admin
* Настройке RBAC
* Примерам запросов/ответов API
* Обработке ошибок

**Путь:** `docs/images/`

---

### Окружение для разработки

```bash
# Установка dev-зависимостей
pip install -r requirements-dev.txt

# Форматирование кода
black .

# Линтинг
flake8

# Проверка типов
mypy apps/
```

---

## 🆘 Поддержка

По вопросам, багам или запросам фич:

* **Issues:** создайте issue на GitHub
* **Документация:** смотрите каталог `/docs`
* **Email:** [vbahodir00@gmail.com](mailto:vbahodir00@gmail.com)

---

## 🙏 Благодарности

Сделано с использованием:

* Django и Django REST Framework
* PostgreSQL
* Redis
* Celery
* drf-spectacular


---

<div align="center">

**[Документация](#-руководство-по-использованию)** • **[Справочник API](#-справочник-api)** • **[Безопасность](#-соображения-безопасности)** • **[Contributing](#-окружение-для-разработки)**

Сделано с ❤️ Bahodir :)

</div>
