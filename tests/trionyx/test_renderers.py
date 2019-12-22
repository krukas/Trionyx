from django.test import TestCase

from trionyx.trionyx import renderers


class FakeModel:
    level = 20
    progress = 45
    status = 50

    def get_level_display(self):
        return ''

    def get_status_display(self):
        return ''


class RenderersTest(TestCase):

    def test_render_level(self):
        self.assertIn('info', renderers.render_level(FakeModel()))

    def test_render_progress(self):
        self.assertIn('45', renderers.render_progress(FakeModel()))

    def test_render_status(self):
        self.assertIn('success', renderers.render_status(FakeModel()))
