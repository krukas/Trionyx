from django import template
from django.utils.functional import cached_property
from django.template.loader import render_to_string

from trionyx import utils

register = template.Library()


class Layout:
    def __init__(self, *components, **options):
        self.object = None
        self.components = list(components)
        self.options = options

    def __getitem__(self, slice):
        return self.components[slice]

    def __setitem__(self, slice, value):
        self.components[slice] = value

    def __delitem__(self, slice):
        del self.components[slice]

    def __len__(self):
        return len(self.components)

    def render(self, request=None):
        return render_to_string('trionyx/layout.html', {'layout': self}, request)

    def set_object(self, object):
        """
        Set object for rendering layout and set object to all components

        :param object:
        :return:
        """
        self.object = object

        # Pass object along to child components for rendering
        for component in self.components:
            component.set_object(object)

    def add_component(self, component, after=None, before=None):
        """
        Add component to existing layout can insert component before or after component path

        :param component:
        :param after: component code path
        :param before: component code path
        :return:
        """
        pass

    def update_component(self, component_path, callback):
        """
        Update component with given path, calls callback with component

        :param component_path:
        :param callback:
        :return:
        """
        pass

    def delete_component(self, component_path):
        """
        Delete component for given path

        :param component_path:
        :return:
        """
        pass


class Component:
    template_name = None
    """Component template to be rendered, default template only renders child components"""

    js_files = None
    """List of required javascript files"""

    css_files = None
    """List of required css files"""

    def __init__(self, *components, **options):
        self.id = options.get('id')
        self.components = list(components)
        self.object = None

        # set options on object
        for key, value in options.items():
            setattr(self, key, value)

    @cached_property
    def css_id(self):
        return 'component-{}'.format(utils.random_string(6))

    def set_object(self, object):
        """
        Set object for rendering component and set object to all components

        :param object:
        :return:
        """
        self.object = object

        # Pass object along to child components for rendering
        for component in self.components:
            component.set_object(object)

    def render(self, context, request=None):
        context['component'] = self
        return render_to_string(self.template_name, context, request)


# =============================================================================
# Simple HTML tags
# =============================================================================
class HtmlTagWrapper(Component):
    template_name = 'trionyx/components/html_tag.html'
    tag = 'div'
    attr = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attr = self.attr if self.attr else {}

    def get_attr_text(self):
        return ' '.join([
            '{}="{}"'.format(key, value)
            for key, value in self.attr.items()
        ])


class Html(HtmlTagWrapper):
    template_name = 'trionyx/components/html.html'
    tag = None
    valid_attr = []

    def __init__(self, html=None, **kwargs):
        super().__init__(**kwargs)
        self.html = html
        for key, value in kwargs.items():
            if key in self.valid_attr:
                self.attr[key] = value


class Img(Html):
    tag = 'img'
    valid_attr = ['src', 'width']
    attr = {
        'width': '100%',
    }


# =============================================================================
# Bootstrap grid system
# =============================================================================
class Container(HtmlTagWrapper):
    attr = {
        'class': 'container-fluid'
    }


class Row(HtmlTagWrapper):
    attr = {
        'class': 'row'
    }


class Column(HtmlTagWrapper):
    size = 'md'
    columns = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attr['class'] = '-'.join(x for x in ['col', str(self.size), str(self.columns)] if x)


class Column2(Column):
    columns = 2


class Column3(Column):
    columns = 3


class Column4(Column):
    columns = 4


class Column5(Column):
    columns = 5


class Column6(Column):
    columns = 6


class Column7(Column):
    columns = 7


class Column8(Column):
    columns = 8


class Column9(Column):
    columns = 9


class Column10(Column):
    columns = 10


class Column11(Column):
    columns = 11


class Column12(Column):
    columns = 12


# =============================================================================
# Bootstrap elements
# =============================================================================
class Panel(Component):
    """
    Bootstrap panel available options

    - title
    - footer_components
    - collapse
    - contextual: primary, success, info, warning, danger

    """
    template_name = 'trionyx/components/panel.html'


class DescriptionList(Component):
    """
    Bootstrap description available options

    - horizontal
    - fields: list of fields to render

    .. code-block:: python

        # fields example's
        ['first_name', 'last_name']

        [
            'first_name',
            {
                'label': 'Real last name',
                'value': object.last_name
            }

        ]


    """
    template_name = 'trionyx/components/description_list.html'
    horizontal = True

    @property
    def fields(self):
        for field in getattr(self, '_fields', []):
            if isinstance(field, str):
                field = {
                    'label': self.object._meta.get_field(field).verbose_name,
                    'value': getattr(self.object, field)
                }
            yield field

    @fields.setter
    def fields(self, fields):
        setattr(self, '_fields', fields)
