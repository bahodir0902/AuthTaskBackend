from django.db import models


class LogEntry(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=30)
    logger_name = models.CharField(max_length=255)
    message = models.TextField()
    pathname = models.CharField(max_length=500, null=True, blank=True)
    line_no = models.IntegerField(null=True, blank=True)
    exception = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"[{self.level}] {self.logger_name}: {self.message[:50]}"

    class Meta:
        db_table = "Logs"
        verbose_name = "Log Entry"
        verbose_name_plural = "Log Entries"
