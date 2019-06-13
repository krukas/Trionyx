"""
trionyx.trionyx
~~~~~~~~~~~~~~~

Core app for Trionyx

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import logging


default_app_config = 'trionyx.trionyx.apps.Config'


class LogDBHandler(logging.Handler):
    """DB log handler"""

    def emit(self, record):
        """Save log record"""
        try:
            from trionyx.trionyx.models import Log
            Log.objects.create_log_entry_by_record(record)
        except Exception:
            pass  # Logception?


db_handler = LogDBHandler()
db_handler.setLevel(logging.WARNING)
logging.getLogger().addHandler(db_handler)