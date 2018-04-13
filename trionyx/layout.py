"""
trionyx.layout
~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from django import template
from django.utils.functional import cached_property
from django.template.loader import render_to_string
from django.db.models import QuerySet

from trionyx import utils

register = template.Library()


class Layout:
    """Layout object that holds components"""

    def __init__(self, *components, **options):
        """Initialize Layout"""
        self.object = False
        self.components = list(components)
        self.options = options

    def __getitem__(self, slice):
        """Get component item"""
        return self.components[slice]

    def __setitem__(self, slice, value):
        """Set component"""
        self.components[slice] = value

    def __delitem__(self, slice):
        """Delete component"""
        del self.components[slice]

    def __len__(self):
        """Get component length"""
        return len(self.components)

    def render(self, request=None):
        """Render layout for given request"""
        return render_to_string('trionyx/layout.html', {'layout': self}, request)

    def set_object(self, object):
        """
        Set object for rendering layout and set object to all components

        :param object:
        :return:
        """
        if self.object is False:
            self.object = object

        # Pass object along to child components for rendering
        for component in self.components:
            component.set_object(self.object)

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
    """Base component"""

    template_name = None
    """Component template to be rendered, default template only renders child components"""

    js_files = None
    """List of required javascript files"""

    css_files = None
    """List of required css files"""

    def __init__(self, *components, **options):
        """Initialize Component"""
        self.id = options.get('id')
        self.components = list(components)
        self.object = False

        # set options on object
        for key, value in options.items():
            setattr(self, key, value)

    @cached_property
    def css_id(self):
        """Generate random css id for component"""
        return 'component-{}'.format(utils.random_string(6))

    def set_object(self, object):
        """
        Set object for rendering component and set object to all components

        :param object:
        :return:
        """
        if self.object is False:
            self.object = object

        # Pass object along to child components for rendering
        for component in self.components:
            component.set_object(object)

    def render(self, context, request=None):
        """Render component"""
        context['component'] = self
        return render_to_string(self.template_name, context, request)


# =============================================================================
# Simple HTML tags
# =============================================================================
class HtmlTagWrapper(Component):
    """HtmlTagWrapper wraps given component in given html tag"""

    template_name = 'trionyx/components/html_tag.html'

    tag = 'div'
    """Html tag nam"""

    attr = None
    """Dict with html attributes"""

    def __init__(self, *args, **kwargs):
        """Initialize HtmlTagWrapper"""
        super().__init__(*args, **kwargs)
        self.attr = self.attr if self.attr else {}

    def get_attr_text(self):
        """Get html attr text to render in template"""
        return ' '.join([
            '{}="{}"'.format(key, value)
            for key, value in self.attr.items()
        ])


class Html(HtmlTagWrapper):
    """Html single html tag"""

    template_name = 'trionyx/components/html.html'
    tag = None

    valid_attr = []
    """Valid attributes that can be used"""

    def __init__(self, html=None, **kwargs):
        """Init Html"""
        super().__init__(**kwargs)
        self.html = html
        for key, value in kwargs.items():
            if key in self.valid_attr:
                self.attr[key] = value


class Img(Html):
    """Img tag"""

    tag = 'img'
    valid_attr = ['src', 'width']
    attr = {
        'width': '100%',
    }


# =============================================================================
# Bootstrap grid system
# =============================================================================
class Container(HtmlTagWrapper):
    """Bootstrap container"""

    attr = {
        'class': 'container-fluid'
    }


class Row(HtmlTagWrapper):
    """Bootstrap row"""

    attr = {
        'class': 'row'
    }


class Column(HtmlTagWrapper):
    """Bootstrap Column"""

    size = 'md'
    columns = 1

    def __init__(self, *args, **kwargs):
        """Initialize Column"""
        super().__init__(*args, **kwargs)
        self.attr['class'] = '-'.join(x for x in ['col', str(self.size), str(self.columns)] if x)


class Column2(Column):
    """Bootstrap Column 2"""

    columns = 2


class Column3(Column):
    """Bootstrap Column 3"""

    columns = 3


class Column4(Column):
    """Bootstrap Column 4"""

    columns = 4


class Column5(Column):
    """Bootstrap Column 5"""

    columns = 5


class Column6(Column):
    """Bootstrap Column 6"""

    columns = 6


class Column7(Column):
    """Bootstrap Column 7"""

    columns = 7


class Column8(Column):
    """Bootstrap Column 8"""

    columns = 8


class Column9(Column):
    """Bootstrap Column 9"""

    columns = 9


class Column10(Column):
    """Bootstrap Column 10"""

    columns = 10


class Column11(Column):
    """Bootstrap Column 11"""

    columns = 11


class Column12(Column):
    """Bootstrap Column 12"""

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

    collapse = True

    def __init__(self, title, *components, **options):
        """Init Panel"""
        super().__init__(*components, **options)
        self.title = title


class DescriptionList(Component):
    """
    Bootstrap description, fields are the params. available options

    - horizontal

    .. code-block:: python

        # fields example's
        DescriptionList(
            'first_name',
            'last_name'
        )

        DescriptionList(
            'first_name',
            {
                'label': 'Real last name',
                'value': object.last_name
            }
        )


    """

    template_name = 'trionyx/components/description_list.html'
    horizontal = True
    no_data_message = "There is no data"

    def __init__(self, *fields, **options):
        """Init panel"""
        super().__init__(**options)
        self.fields = fields

    @property
    def fields(self):
        """Give back fields"""
        if not self.object:
            return []
        return [
            {
                'label': self.object._meta.get_field(field).verbose_name,
                'value': getattr(self.object, field)
            } if isinstance(field, str) else field
            for field in getattr(self, '_fields', [])
        ]

    @fields.setter
    def fields(self, fields):
        """Set fields"""
        setattr(self, '_fields', fields)


class Table(Component):
    """Bootstrap table"""

    template_name = 'trionyx/components/table.html'

    def __init__(self, items, *fields, **options):
        """Init Table"""
        super().__init__(**options)

        self.items = items
        """Can be string with field name relation, Queryset or list"""

        self.fields = fields

    @cached_property
    def rendered_items(self):
        """Get rendered items"""
        items = self.items

        if isinstance(items, list):
            return items

        if isinstance(items, str):
            items = getattr(self.object, items).all()

        fields = [f['field'] for f in self.rendered_fields]
        # get items from QuerySet
        return [
            [
                getattr(item, field)
                for field in fields
            ]
            for item in items
        ]

    @cached_property
    def rendered_fields(self):
        """Get rendered fields"""
        model = None
        if isinstance(self.items, str):
            items = getattr(self.object, self.items)
            model = items.model if items else None

        if not model and isinstance(self.items, QuerySet):
            model = self.items.model

        if not model:
            return [
                {
                    'title': field.split(':')[0],
                    'width': field.split(':')[1] if ':' in field else None
                } if isinstance(field, str) else field
                for field in self.fields
            ]

        return [
            {
                'title': model._meta.get_field(field.split(':')[0]).verbose_name,
                'field': field.split(':')[0],
                'width': field.split(':')[1] if ':' in field else None
            } if isinstance(field, str) else field
            for field in self.fields
        ]
