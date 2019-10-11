from django.test import TestCase
from django.utils import translation

from trionyx import utils


class UtilsTestCase(TestCase):

    def test_random_string(self):
        self.assertNotEqual(utils.random_string(8), utils.random_string(8))
        self.assertEqual(len(utils.random_string(16)), 16)

    def test_get_current_language(self):
        translation.activate('nl-nl')
        self.assertEqual('nl-nl', utils.get_current_language())

    def test_get_local(self):
        translation.activate('nl-nl')
        self.assertEqual('nl_NL', utils.get_current_locale())

    def test_get_datetime_input_format(self):
        translation.activate('nl-nl')
        self.assertEqual('%d-%m-%Y %H:%M:%S', utils.get_datetime_input_format())
        translation.activate('en-us')
        self.assertNotEqual('%d-%m-%Y %H:%M:%S', utils.get_datetime_input_format())

    def test_datetime_format_to_momentjs(self):
        self.assertEqual('DD-MM-YYYY HH:mm:ss', utils.datetime_format_to_momentjs('%d-%m-%Y %H:%M:%S'))

    def test_datetime_format_to_django_template(self):
        self.assertEqual('d-m-Y H:i:s', utils.datetime_format_to_django_template('%d-%m-%Y %H:%M:%S'))
