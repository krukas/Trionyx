from django.test import TestCase

from app.testblog.models import Tag
from trionyx.config import ModelConfig


class ModelConfigTestCase(TestCase):
    fields = ['id', 'created_at', 'updated_at', 'created_by', 'verbose_name', 'name']

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
