from django.contrib.auth.base_user import BaseUserManager


class DeactivatedUsersManager(BaseUserManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                is_active=False,
            )
        )
