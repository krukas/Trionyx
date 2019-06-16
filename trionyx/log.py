"""
trionyx.log
~~~~~~~~~~~

Core app for Trionyx

:copyright: 2019 by Maikel Martens
:license: GPLv3
"""
import logging
from django.conf import settings


class LogDBHandler(logging.Handler):
    """DB log handler"""

    def emit(self, record):
        """Save log record"""
        try:
            from trionyx.trionyx.models import Log
            Log.objects.create_log_entry_by_record(record)
        except Exception:
            pass  # Logception?


def enable_db_logger():
    """Enable DB logger"""
    db_handler = LogDBHandler()
    db_handler.setLevel(settings.TX_DB_LOG_LEVEL)
    logging.getLogger().addHandler(db_handler)
