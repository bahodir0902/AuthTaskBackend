from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    GUEST = "guest", "Guest"
    USER = "user", "User"
    MANAGER = "manager", "Manager"
    ADMIN = "admin", "Admin"


from .managers import CustomUserManager  # noqa E402
from .managers import DeactivatedUsersManager  # noqa E402


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=120, null=True, blank=True)

    email_verified = models.BooleanField(default=False)
    must_set_password = models.BooleanField(default=True)
    mfa_enabled = models.BooleanField(default=False)

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    objects = CustomUserManager()
    deactivated_users = DeactivatedUsersManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save(update_fields=["is_active"])

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = "Users"
        indexes = [
            models.Index(fields=["role", "is_active"]),
            models.Index(fields=["email", "first_name", "last_name"]),
        ]
