from django.test import TestCase
from django.template import Context, RequestContext, Template
from django.utils import timezone
from django.test.client import RequestFactory

from trionyx.trionyx.models import User
from trionyx.menu import MenuItem
from trionyx.layout import HtmlTagWrapper


class TemplateTagTest(TestCase):
    def test_active_menu_item(self):
        request = RequestFactory().get('/dashboard/')
        request.user = User(is_superuser=True)

        context = RequestContext(
            request,
            {
                'item': MenuItem(
                    path='dashboard',
                    name='Dashboard',
                    url='/dashboard/'
                )
            }
        )
        template = Template(
            '{% load trionyx %}'
            '{% active_menu_item request item %}'
        )
        self.assertInHTML('active', template.render(context))

    def test_not_active_menu_item(self):
        request = RequestFactory().get('/not/')
        request.user = User(is_superuser=True)

        context = RequestContext(
            request,
            {
                'item': MenuItem(
                    path='dashboard',
                    name='Dashboard',
                    url='/dashboard/'
                )
            }
        )
        template = Template(
            '{% load trionyx %}'
            '{% active_menu_item request item %}'
        )
        self.assertInHTML('', template.render(context))

    def test_render_component(self):
        context = Context({'component': HtmlTagWrapper()})
        template = Template(
            '{% load trionyx %}'
            '{% render_component component %}'
        )
        self.assertInHTML('<div></div>', template.render(context))

    def test_jsonify(self):
        context = Context({'data': [1, 2, {'key': 'value'}]})
        template = Template(
            '{% load trionyx %}'
            '{{ data|jsonify }}'
        )
        self.assertInHTML('[1, 2, {"key": "value"}]', template.render(context))

    def test_jsonify_queryset(self):
        context = Context({'data': User.objects.all()})
        template = Template(
            '{% load trionyx %}'
            '{{ data|jsonify }}'
        )
        self.assertInHTML('[]', template.render(context))

    def test_model_url(self):
        context = Context({'user': User()})
        template = Template(
            '{% load trionyx %}'
            "{% model_url user 'list' %}"
        )
        self.assertInHTML('/model/trionyx/user/', template.render(context))

    def test_is_date_true(self):
        context = Context({'date': timezone.now()})
        template = Template(
            '{% load trionyx %}'
            "{{ date|is_date }}"
        )
        self.assertInHTML('True', template.render(context))

    def test_is_date_false(self):
        context = Context({'date': 'No date'})
        template = Template(
            '{% load trionyx %}'
            "{{ date|is_date }}"
        )
        self.assertInHTML('False', template.render(context))

    def test_price(self):
        context = Context({'total': 110.25})
        template = Template(
            '{% load trionyx %}'
            "{{ total|price }}"
        )
        self.assertInHTML('US$ 110,25', template.render(context))
