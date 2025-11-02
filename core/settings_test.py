from .settings import *  # noqa

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

RATE_LIMIT = 5

REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"].update(  # noqa
    {
        "anon": "1000/min",
        "user": "1000/min",
        "auth_login": f"{RATE_LIMIT}/min",
        "auth_verify_registration": f"{RATE_LIMIT}/min",
        "auth_verify_password_reset": f"{RATE_LIMIT}/min",
    }
)
