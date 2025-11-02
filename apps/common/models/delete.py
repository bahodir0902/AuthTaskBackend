from django.db import models

from apps.common.queryset import DeleteManager


class DeleteModel(models.Model):
    is_active = models.BooleanField(default=True)

    all_objects = models.Manager()
    objects = DeleteManager()

    class Meta:
        abstract = True

    def delete(self, **kwargs):
        self.is_active = False
        self.save()
