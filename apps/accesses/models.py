from django.db import models

from apps.users.models.user import Role


class Resource(models.Model):
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "Access_Resource"

    def __str__(self):
        return f"{self.code} - {self.name}"


class AccessRule(models.Model):
    role = models.CharField(max_length=20, choices=Role.choices)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name="rules")

    read_own = models.BooleanField(default=False)
    read_all = models.BooleanField(default=False)
    create = models.BooleanField(default=False)
    update_own = models.BooleanField(default=False)
    update_all = models.BooleanField(default=False)
    delete_own = models.BooleanField(default=False)
    delete_all = models.BooleanField(default=False)

    class Meta:
        db_table = "Access_Rule"
        verbose_name = "Access Rule"
        verbose_name_plural = "Access Rules"
        unique_together = ("role", "resource")

    def __str__(self):
        return f"{self.role} -> {self.resource.name}"
