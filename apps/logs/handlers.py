import logging

from django.db import DatabaseError, OperationalError
from django.utils import timezone


class DatabaseHandler(logging.Handler):
    def emit(self, record):
        try:
            from apps.logs.models import LogEntry

            LogEntry.objects.create(
                timestamp=timezone.now(),
                level=record.levelname,
                logger_name=record.name,
                message=self.format(record),
                pathname=record.pathname,
                line_no=record.lineno,
                exception=self._format_exception(record),
            )
        except (OperationalError, DatabaseError):
            pass
        except Exception:
            pass

    @staticmethod
    def _format_exception(record):
        if record.exc_info:
            import traceback

            return "".join(traceback.format_exception(*record.exc_info))
        return None
