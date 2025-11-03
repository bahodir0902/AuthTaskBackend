from django.db import models


class Order(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="orders")
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Demo_Order"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.id} - {self.title} (owner={self.user_id})"
