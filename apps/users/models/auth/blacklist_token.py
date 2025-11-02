from django.db import models

from apps.users.models import User


class TokenType(models.TextChoices):
    ACCESS = "access", "Access"
    REFRESH = "refresh", "Refresh"


class BlacklistedToken(models.Model):
    jti = models.CharField(max_length=255, unique=True)
    token_type = models.CharField(max_length=10, choices=TokenType.choices)
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.jti} ({self.token_type})"

    class Meta:
        db_table = "BlacklistedTokens"
        verbose_name = "Blacklisted Token"
        verbose_name_plural = "Blacklisted Tokens"
