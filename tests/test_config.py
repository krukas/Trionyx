from django.test import TestCase

from app.testblog.models import Tag
from trionyx.trionyx.models import SystemVariable
from trionyx.config import ModelConfig, variables


class ModelConfigTestCase(TestCase):
    fields = ['id', 'created_at', 'updated_at', 'created_by', 'verbose_name', 'name']

    def test_variable_default_value(self):
        self.assertEqual(variables.get('notexists', 123), 123)

    def test_variable_save(self):
        variables.set('new_variable', 1337)
        self.assertEqual(variables.get('new_variable'), 1337)  # warm up local cache
        self.assertEqual(SystemVariable.objects.filter(code='new_variable').count(), 1)

        # Test if cache version works
        SystemVariable.objects.all().delete()
        self.assertEqual(variables.get('new_variable'), 1337)

    def test_variable_increment(self):
        with variables.get_increment('increment', start=10):
            pass
        self.assertEqual(variables.get('increment'), 11)

    def test_variable_increment_failed(self):
        try:
            with variables.get_increment('increment2', start=10):
                raise Exception()
        except Exception:
            pass

        with variables.get_increment('increment2', start=10):
            pass
        self.assertEqual(variables.get('increment2'), 11)

    def test_default_list_fields(self):
        config = ModelConfig(Tag)
        self.assertEqual(set(config.get_list_fields().keys()), set(self.fields))

    def test_custom_list_fields(self):
        config = ModelConfig(Tag)
        config.list_fields = [
            {
                'field': 'custom_field',
                'renderer': lambda model, field: model.name.upper()
            }
        ]

        self.assertEqual(set(config.get_list_fields().keys()), {'custom_field', *self.fields})

    def test_missing_name_list_fields(self):
        config = ModelConfig(Tag)
        config.list_fields = [
            {
                'field_name': 'custom_field',
                'renderer': lambda model, field: model.name.upper()
            }
        ]

        self.assertRaises(Exception, config.get_list_fields)
