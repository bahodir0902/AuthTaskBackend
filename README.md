# 🔐 Auth Task Backend

> A production-grade authentication and authorization service built with Django REST Framework, PostgreSQL, Redis, and Celery.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.x-red.svg)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-Latest-red.svg)](https://redis.io/)

---

## 📋 Overview

A comprehensive authentication and authorization backend service featuring JWT-based authentication, multi-factor authentication (MFA), role-based access control (RBAC), and production-ready security features. Perfect for modern web applications requiring robust user management and fine-grained permissions.

### ✨ Key Features

**Authentication Layer**
- 🎫 Custom JWT implementation (Access + Refresh tokens)
- 🔄 Automatic refresh token rotation with blacklisting
- 📧 Email/Password authentication
- 🔐 Multi-Factor Authentication (MFA/OTP)
- 🔑 Password reset and email change flows
- 📨 User invitation system
- 🚪 Logout and logout-all-devices support

**Authorization Layer**
- 👥 Role-Based Access Control (RBAC)
- 📊 Resource and Rule management
- 🎯 Granular permissions (read_own, read_all, create, update_own, update_all, delete_own, delete_all)
- 🛡️ DRF permission classes with action mapping

**Developer Experience**
- 📚 Interactive Swagger/OpenAPI documentation
- 🐳 Docker Compose setup
- 📬 Asynchronous email delivery via Celery
- ⚡ Redis caching layer
- 🧪 Comprehensive pytest test suite
- 🚦 Rate limiting on sensitive endpoints

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                        │
├─────────────────────────────────────────────────────────────┤
│  Frontend App  │  Mobile App  │  Third-party Services       │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Django REST Framework + Swagger UI                         │
│  • Authentication Endpoints                                 │
│  • User Management Endpoints                                │
│  • RBAC Administration Endpoints                            │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                     │
├─────────────────────────────────────────────────────────────┤
│  JWT Handler  │  OTP Service  │  RBAC Permission Engine     │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data & Cache Layer                      │
├──────────────────────────┬──────────────────────────────────┤
│  PostgreSQL              │  Redis                           │
│  • User data             │  • OTP codes                     │
│  • Tokens                │  • Session cache                 │
│  • RBAC rules            │  • Celery broker                 │
└──────────────────────────┴──────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Background Jobs Layer                    │
├─────────────────────────────────────────────────────────────┤
│  Celery Workers                                             │
│  • Email delivery                                           │
│  • OTP generation                                           │
│  • Notification system                                      │
└─────────────────────────────────────────────────────────────┘
```

### Authentication Flow

**JWT Token Lifecycle**
- Access Token: 15 minutes lifespan
- Refresh Token: 7 days lifespan
- Automatic rotation on refresh with old token blacklisting

**MFA/OTP Security**
- Time-limited codes stored in Redis
- Hashed storage for security
- Maximum attempt counter
- Automatic expiration

---

## 🛠️ Tech Stack

| Category | Technology           | Purpose |
|----------|----------------------|---------|
| **Core** | Python 3.13          | Runtime environment |
| | Django 5.2.7         | Web framework |
| | Django REST Framework | API development |
| **Database** | PostgreSQL 16        | Primary data store |
| **Cache & Queue** | Redis                | Caching & message broker |
| | django-redis         | Django Redis integration |
| | Celery               | Asynchronous task queue |
| **Authentication** | PyJWT                | JWT token handling |
| **Documentation** | drf-spectacular      | OpenAPI/Swagger generation |
| **Utilities** | CORS Headers         | Cross-origin support |
| | Whitenoise           | Static file serving |
| **Testing** | pytest               | Test framework |

---

## 📁 Project Structure

```
auth-task-backend/
│
├── core/                           # Project configuration
│   ├── settings.py                 # Main settings (JWT, Celery, Redis)
│   ├── settings_test.py            # Test environment settings
│   ├── urls.py                     # Root URL configuration
│   └── celery.py                   # Celery application setup
│
├── apps/                           # Application modules
│   │
│   ├── users/                      # User management
│   │   ├── auth/                   # JWT & OTP implementation
│   │   ├── models/                 # User, Profile, Token models
│   │   ├── serializers/            # DRF serializers
│   │   ├── views/                  # API views
│   │   ├── service/                # Business logic & Celery tasks
│   │   └── signals/                # Django signals
│   │
│   ├── access/                     # Authorization (RBAC)
│   │   ├── models.py               # Resource & AccessRule models
│   │   ├── permissions.py          # Custom DRF permissions
│   │   ├── serializers.py          # RBAC serializers
│   │   └── views.py                # RBAC management views
│   │
│   └── demo/                       # Demo implementation
│       └── views.py                # Sample OrdersViewSet
│
├── tests/                          # Test suite
│   └── users/                      # User app tests
│
├── docs/                           # Documentation
│   └── images/                     # Screenshots & diagrams
│
├── Dockerfile                      # Container definition
├── docker-compose.yml              # Multi-container orchestration
├── entrypoint.sh                   # Container startup script
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose (recommended)
- Python 3.13+ (for local development)
- PostgreSQL 16+ (if running locally)
- Redis (if running locally)

### Option A: Docker Compose (Recommended)

**Step 1: Configure Environment**

Create a `.env` file in the project root:

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

**Step 2: Launch Services**

```bash
docker compose up --build
```

**Step 3: Access Application**

- **API & Swagger UI**: http://localhost:8010/
- **Django Admin**: http://localhost:8010/admin/
  - Email: `admin@admin.com`
  - Password: `securepassword123`

#### Optional: PostgreSQL in Docker

Add this service to `docker-compose.yml` if you need PostgreSQL containerized:

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

Update environment variables:
```bash
DB_HOST=postgres
DB_PORT=5432
```

### Option B: Local Development

**Step 1: Create Virtual Environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

**Step 2: Configure Environment**

```bash
export DJANGO_SETTINGS_MODULE=core.settings
# Copy and configure .env file as shown above
```

**Step 3: Initialize Database**

```bash
python manage.py migrate
python manage.py createsuperuser
```

**Step 4: Start Services**

```bash
# Terminal 1: Django development server
python manage.py runserver 0.0.0.0:8010

# Terminal 2: Celery worker
celery -A core worker -l info

# Terminal 3: Redis (if not running)
redis-server
```

---

## 📖 Usage Guide

### RBAC Configuration

#### 1. Create Resources

Navigate to **Django Admin → Access → Resources** and create:

| Code | Name | Description |
|------|------|-------------|
| `orders` | Orders | Order management resource |
| `users` | Users | User management resource |
| `rules` | Access Rules | RBAC rule management |

#### 2. Define Access Rules

Navigate to **Django Admin → Access → Access Rules** and configure permissions:

**Admin Role - Orders Resource**
```
Role: ADMIN
Resource: orders
Permissions: ALL enabled (read_own, read_all, create, update_own, update_all, delete_own, delete_all)
```

**User Role - Orders Resource**
```
Role: USER
Resource: orders
Permissions:
  ✓ read_own: True
  ✓ create: True
  ✓ update_own: True
  ✗ read_all: False
  ✗ update_all: False
  ✗ delete_own: False
  ✗ delete_all: False
```

**Manager Role - Orders Resource**
```
Role: MANAGER
Resource: orders
Permissions:
  ✓ read_all: True
  ✓ create: True
  ✓ update_all: True
  ✗ delete_all: False
```

#### 3. Create Demo Users

In **Django Admin → Users**, create test accounts:

**User 1**
- Email: `user1@example.com`
- Role: `USER`
- Flags: `is_active=True`, `email_verified=True`, `must_set_password=False`
- Set password via admin

**User 2**
- Email: `user2@example.com`
- Role: `USER`
- Same configuration as User 1

### Interactive API Testing (Swagger UI)

#### Scenario 1: Unauthorized Access (401)

```
1. Open Swagger UI: http://localhost:8010/
2. Try GET /api/demo/orders/ without authentication
3. Result: 401 Unauthorized
```

#### Scenario 2: Successful Authentication & Authorization

```
1. POST /api/accounts/auth/login/
   Body: {
     "email": "user1@example.com",
     "password": "yourpassword"
   }

2. Copy the "access" token from response

3. Click "Authorize" button in Swagger UI
   Enter: Bearer <your-access-token>

4. POST /api/demo/orders/
   Body: {
     "title": "My first order"
   }
   Result: 201 Created

5. GET /api/demo/orders/
   Result: 200 OK (shows only user1's orders)
```

#### Scenario 3: Forbidden Access (403)

```
1. Login as admin and create an order
2. Note the order ID
3. Re-authenticate as user1
4. Try GET /api/demo/orders/{admin-order-id}/
5. Result: 403 Forbidden (user1 doesn't own this order)
```

#### Scenario 4: Accessing Own Resources (200)

```
1. As user1, create an order
2. Note the order ID
3. GET /api/demo/orders/{user1-order-id}/
4. Result: 200 OK (user1 owns this order)
```

---

## 🔄 User Flows

### Registration Flow

```
1. POST /api/accounts/auth/register/
   → System sends OTP to email via Celery

2. POST /api/accounts/auth/verify-registration/
   → Verify OTP code
   → Returns access & refresh tokens
   → User automatically logged in
```

### Login Flow

**Without MFA:**
```
POST /api/accounts/auth/login/
→ Returns access & refresh tokens immediately
```

**With MFA:**
```
1. POST /api/accounts/auth/login/
   → System sends OTP to email

2. POST /api/accounts/auth/verify-otp/
   → Verify OTP code
   → Returns access & refresh tokens
```

### Token Refresh Flow

```
POST /api/accounts/auth/refresh/
Body: { "refresh": "your-refresh-token" }
→ Old refresh token blacklisted & revoked
→ Returns new access & refresh tokens
```

### Logout Flow

**Single Device:**
```
POST /api/accounts/auth/logout/
Body: { "refresh": "your-refresh-token" }
→ Blacklists both access and refresh tokens
```

**All Devices:**
```
POST /api/accounts/auth/logout-of-all-devices/
→ Revokes all refresh tokens for user
→ Invalidates all active sessions
```

### Password Reset Flow

```
1. POST /api/accounts/auth/forgot-password/
   Body: { "email": "user@example.com" }
   → Sends OTP to email

2. POST /api/accounts/auth/verify-password-reset/
   Body: { "email": "...", "otp": "123456" }
   → Returns uid & token

3. POST /api/accounts/auth/reset-password/
   Body: {
       "uid": "...",
        "token": "...",
        "new_password": "...",
        "re_new_password": "..."
   }
   → Password updated
```

### Email Change Flow

```
1. POST /api/accounts/users/request-email-change/
   Body: { "new_email": "newemail@example.com" }
   → Sends OTP to new email address

2. POST /api/accounts/users/confirm-email-change/
   Body: { "otp": "123456" }
   → Email updated
```

### Profile Management

**Read Profile:**
```
GET /api/accounts/users/profile/
→ Returns user profile data
```

**Update Profile:**
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

### Account Deletion

```
DELETE /api/accounts/users/delete-account/
→ Soft delete (sets is_active=False)
→ User cannot login anymore
→ All user's tokens are blacklisted and revoked
→ Data preserved in database
```

---

## 🔐 Authorization Model (RBAC)

### Core Concepts

**Resource**
- Represents a protected entity in this system
- Examples: orders, users, posts, comments
- Stored in database with unique code

**Access Rule**
- Links a role to a resource with specific permissions
- Defines what operations are allowed

**Permission Types**

| Permission | Scope | Description |
|-----------|-------|-------------|
| `read_own` | Own | View own resources |
| `read_all` | All | View all resources |
| `create` | N/A | Create new resources |
| `update_own` | Own | Modify own resources |
| `update_all` | All | Modify all resources |
| `delete_own` | Own | Delete own resources |
| `delete_all` | All | Delete all resources |

### Permission Resolution

**Action Mapping:**

| DRF Action | HTTP Method | Required Permission |
|-----------|-------------|-------------------|
| `list` | GET | `read_all` or `read_own` |
| `retrieve` | GET | `read_all` or `read_own` |
| `create` | POST | `create` |
| `update` | PUT/PATCH | `update_all` or `update_own` |
| `destroy` | DELETE | `delete_all` or `delete_own` |

**Resolution Logic:**

1. Check if user has `ADMIN` role → **Grant full access**
2. Check if `*_all` permission exists → **Grant access to all objects**
3. Check if `*_own` permission exists:
   - Compare object's `owner_field` with `request.user`
   - If match → **Grant access**
   - If no match → **Deny access (403)**

### Implementation Example

```python
from apps.access.permissions import HasResourcePermission

class OrdersViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, HasResourcePermission]
    access_resource = "orders"  # Links to Resource.code
    owner_field = "user"  # Field to check for ownership

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
```

---

## 🌐 API Reference

### Authentication Endpoints

**Base URL:** `/api/accounts/auth/`

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/login/` | POST | User login | None |
| `/refresh/` | POST | Refresh access token | None |
| `/register/` | POST | Start registration | None |
| `/verify-registration/` | POST | Complete registration | None |
| `/verify-otp/` | POST | Verify MFA code | None |
| `/forgot-password/` | POST | Request password reset | None |
| `/verify-password-reset/` | POST | Verify reset OTP | None |
| `/reset-password/` | POST | Set new password | None |
| `/logout/` | POST | Logout single device | Required |
| `/logout-of-all-devices/` | POST | Logout all devices | Required |
| `/set-initial-password/` | POST | Set password from invitation | None |
| `/validate-invitation/` | POST | Validate invitation token | None |

### User Management Endpoints

**Base URL:** `/api/accounts/users/`

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/profile/` | GET | Get user profile | Required |
| `/update-profile/` | PUT/PATCH | Update profile | Required |
| `/request-email-change/` | POST | Request email change | Required |
| `/confirm-email-change/` | POST | Confirm email change | Required |
| `/delete-account/` | DELETE | Soft delete account | Required |

### RBAC Administration Endpoints

**Base URL:** `/api/access/`

| Endpoint | Method | Description | Authentication | Permission |
|----------|--------|-------------|----------------|-----------|
| `/resources/` | GET | List resources | Required | Admin |
| `/resources/` | POST | Create resource | Required | Admin |
| `/resources/{id}/` | GET/PUT/DELETE | Manage resource | Required | Admin |
| `/rules/` | GET | List access rules | Required | Admin |
| `/rules/` | POST | Create rule | Required | Admin |
| `/rules/{id}/` | GET/PUT/DELETE | Manage rule | Required | Admin |

### Documentation Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Swagger UI (Interactive API documentation) |
| `/schema/` | OpenAPI schema (JSON) |
| `/admin/` | Django administration interface |

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/users/test_auth.py

# Run with coverage report
pytest --cov=apps --cov-report=html
```

### Test Configuration

Tests use `core.settings_test` with:
- SQLite in-memory database
- Local memory cache backend
- Console email backend
- Celery eager mode (synchronous)

### Test Coverage

The test suite covers:

- ✅ User registration flow
- ✅ Email verification
- ✅ Login (with and without MFA)
- ✅ OTP generation and validation
- ✅ Token refresh and rotation
- ✅ Token blacklisting
- ✅ Logout (single and all devices)
- ✅ Password reset flow
- ✅ Email change flow
- ✅ Profile management
- ✅ Account soft deletion
- ✅ Rate limiting on sensitive endpoints
- ✅ RBAC permission checks

### Writing New Tests

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

## 🔒 Security Considerations

### JWT Token Security

**Best Practices:**
- In this project I get `JWT_SECRET` from `SECRET_KEY`, but in real development, we need to set dedicated `JWT_SECRET`, separate from `SECRET_KEY` in production

**Configuration:**
```python
# settings.py
JWT_SECRET = os.getenv('JWT_SECRET', SECRET_KEY)
JWT_ACCESS_TOKEN_LIFETIME = timedelta(minutes=15)
JWT_REFRESH_TOKEN_LIFETIME = timedelta(days=7)
```

### OTP Security

**Implementation:**
- OTP codes are hashed before storage
- Time-limited validity (5 minutes by default)
- Maximum attempt counter (5 attempts)
- Stored in Redis cache (auto-expiration)
- Rate limiting on OTP endpoints

### Password Security

**Django's Built-in Protection:**
- PBKDF2 password hashing
- Password validation rules
- Minimum length requirements
- Common password checks

### Rate Limiting

**Protected Endpoints:**
- Login: 5 requests per minute
- Registration: 3 requests per minute
- OTP verification: 5 requests per minute
- Password reset: 3 requests per minute

### Data Privacy

**User Data Handling:**
- Soft delete preserves data for compliance
- Personal data encrypted at rest (PostgreSQL level)
- Secure password reset tokens
- OTP codes not logged

---

## ⚙️ Operations

### Container Roles

The `entrypoint.sh` script supports two operational modes:

**Web Role (`ROLE=web`)**
```bash
ROLE=web
→ Run migrations
→ Collect static files
→ Start Gunicorn server
```

**Worker Role (`ROLE=worker`)**
```bash
ROLE=worker
→ Wait for database (optional)
→ Run migrations
→ Start Celery worker
```

### Deployment Architecture

```
┌─────────────────┐
│   Load Balancer │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│ Web  │  │ Web  │  (Multiple instances)
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
    │ Worker  │  (Celery workers)
    │  ROLE   │
    └─────────┘
```

### Monitoring & Logging

**Log Locations:**
- Application logs: `app.log`
- Console output: stdout/stderr
- Database logs: via custom handler (apps.logs)

**Celery Monitoring:**
```bash
# Monitor Celery tasks
celery -A core inspect active

# Monitor worker status
celery -A core inspect stats

# View registered tasks
celery -A core inspect registered
```

### Scaling Considerations(I'm planning to do it in future)

**Horizontal Scaling:**
- Web instances: Scale behind load balancer
- Celery workers: Scale based on queue length
- Redis: Redis Cluster for high availability
- PostgreSQL: Set up read replicas

**Performance Optimization:**
- Enable query caching in Redis
- Use connection pooling (pgbouncer)
- Configure Gunicorn workers: `workers = (2 * CPU_cores) + 1`
- Use CDN for static files

### Backup Strategy

**Database:**
```bash
# Backup
pg_dump -U appuser -h localhost appdb > backup_$(date +%Y%m%d).sql

# Restore
psql -U appuser -h localhost appdb < backup_20251103.sql
```

**Redis:**
```bash
# Configure Redis persistence
# In redis.conf:
save 900 1
save 300 10
save 60 10000
```

---

## 🎥 Media & Documentation

### Screenshots

Documentation includes visual guides for:

- Swagger UI interface
- Django Admin panel
- RBAC configuration
- API request/response examples
- Error handling demonstrations

**Location:** `docs/images/`

### Video Tutorial

A comprehensive walkthrough video demonstrating:
- Initial setup and configuration
- Creating resources and rules
- User registration and authentication
- RBAC permissions in action
- Common troubleshooting scenarios

**YouTube Link:** _[To be added]_

---

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run code formatting
black .

# Run linting
flake8

# Run type checking
mypy apps/
```

---

## 🆘 Support

For questions, issues, or feature requests:

- **Issues:** Open an issue on GitHub
- **Documentation:** Check the `/docs` directory
- **Email:** vbahodir00@gmail.com

---

## 🙏 Acknowledgments

Built with:
- Django & Django REST Framework
- PostgreSQL
- Redis
- Celery
- drf-spectacular

Special thanks to the open-source community for these amazing tools.

---

<div align="center">

**[Documentation](#-usage-guide)** • **[API Reference](#-api-reference)** • **[Security](#-security-considerations)** • **[Contributing](#-contributing)**

Made with ❤️ by Bahodir :)

</div>
