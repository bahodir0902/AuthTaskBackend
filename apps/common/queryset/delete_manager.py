from django.db import models


class BaseQuerySet(models.QuerySet):

    def delete(self):
        self.update(is_active=False)


class DeleteManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return BaseQuerySet(self.model).filter(is_active=True)
