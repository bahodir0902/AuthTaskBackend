from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import Group

from apps.users.models.user import Role


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        user = self.create_user(email, password, **extra_fields)
        user.email_verified = True
        user.must_set_password = False
        user.is_active = True
        user.role = Role.ADMIN
        user.save(using=self._db)
        admin_groups, _ = Group.objects.get_or_create(name="Admins")
        user.groups.add(admin_groups)
