import uuid
import logging
from django.test import TestCase

from trionyx.trionyx.models import Log
from trionyx.log import enable_db_logger

logger = logging.getLogger('trionyx')


class LogTestCase(TestCase):

    def test_log_entry(self):
        with self.settings(TX_DB_LOG_LEVEL=logging.ERROR):
            enable_db_logger()
            log_message = uuid.uuid4().hex
            logger.error(log_message)

            Log.objects.get(message=log_message)

    def test_no_log_entry(self):
        with self.settings(TX_DB_LOG_LEVEL=logging.ERROR):
            enable_db_logger()
            log_message = uuid.uuid4().hex
            logger.debug(log_message)

            self.assertRaises(Log.DoesNotExist, Log.objects.get, message=log_message)
