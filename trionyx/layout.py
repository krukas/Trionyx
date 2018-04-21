"""
trionyx.layout
~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from django import template
from django.utils.functional import cached_property
from django.template.loader import render_to_string

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


class ComponentFieldsMixin:
    """Mixin for adding fields support and rendering of object(s) with fields."""

    fields = []
    """
    List of fields to be rendered. Item can be a string or dict, default options:

    - **field**: Name of object attribute or dict key to be rendered
    - **label**: Label of field
    - **value**: Value to be rendered
    - **format**: String format for rendering field, default is '{0}'
    - **renderer**: Render function for rendering value, result will be given to format. (lambda value, **options: value)

    Based on the order the fields are in the list a __index__ is set with the list index,
    this is used for rendering a object that is a list.

    .. code-block:: python

        fields = [
            'first_name',
            'last_name'
        ]

        fields = [
            'first_name',
            {
                'label': 'Real last name',
                'value': object.last_name
            }
        ]
    """

    fields_options = {}
    """
    Options available for the field, this is not required to set options on field.

    - **default**: Default option value when not set.

    .. code-block:: python

        fields_options = {
            'width': {
                'default': '150px',
            }
        }

    """

    objects = []
    """
    List of object to be rendered, this can be a QuerySet, list or string.
    When its a string it will get the attribute of the object.

    The items in the objects list can be a mix of Models, dicts or lists.
    """

    def get_fields(self):
        """Get all fields"""
        if not hasattr(self, '__fields'):
            self.__fields = [
                self.parse_field(field, index)
                for index, field in enumerate(getattr(self, 'fields', []))
            ]
        return self.__fields

    def parse_field(self, field_data, index=0):
        """Parse field and add missing options"""
        field = {
            '__index__': index,
        }

        if isinstance(field_data, str):
            field.update(self.parse_string_field(field_data))
        elif isinstance(field_data, dict):
            field.update(field_data)
        else:
            raise TypeError('Expected a str or dict get {}'.format(type(field_data)))

        if 'field' not in field:
            field['field'] = None

        if 'label' not in field and field['field']:
            try:
                field['label'] = self.object._meta.get_field(field['field']).verbose_name.capitalize()
            except Exception:
                field['label'] = field['field'].replace('_', '').capitalize()
        elif 'label' not in field:
            field['label'] = ''

        if 'format' not in field:
            field['format'] = '{0}'

        # Set default options
        for name, options in self.fields_options.items():
            if 'default' in options and name not in field:
                field[name] = options['default']

        return field

    def parse_string_field(self, field_data):
        """
        Parse a string field to dict with options

        String value is used as field name. Options can be given after = symbol.
        Where key value is separated by : and different options by ;, when no : is used then the value becomes True.

        **Example 1:** `field_name`

        .. code-block:: python

            # Output
            {
                'field': 'field_name'
            }

        **Example 3** `field_name=option1:some value;option2: other value`

        .. code-block:: python

            # Output
            {
                'field': 'field_name',
                'option1': 'some value',
                'option2': 'other value',
            }

        **Example 3** `field_name=option1;option2: other value`

        .. code-block:: python

            # Output
            {
                'field': 'field_name',
                'option1': True,
                'option2': 'other value',
            }

        :param str field_data:
        :return dict:
        """
        field_name, *data = field_data.split('=', 1)
        field = {
            'field': field_name,
        }

        for option_string in ''.join(data).split(';'):
            option, *value = option_string.split(':')
            if option.strip():
                field[option.strip()] = value[0].strip() if value else True

        return field

    def render_field(self, field, data):
        """Render field for given data"""
        from trionyx.renderer import renderer

        if 'value' in field:
            value = field['value']
        elif isinstance(data, object) and hasattr(data, field['field']):
            value = getattr(data, field['field'])
            if 'renderer' not in field:
                value = renderer.render_field(data, field['field'], **field)
        elif isinstance(data, dict) and field['field'] in data:
            value = data.get(field['field'])
        elif isinstance(data, list) and field['__index__'] < len(data):
            value = data[field['__index__']]
        else:
            return ''

        options = {key: value for key, value in field.items() if key not in ['value', 'data_object']}
        if 'renderer' in field:
            value = field['renderer'](value, data_object=data, **options)
        else:
            value = renderer.render_value(value, data_object=data, **options)

        return field['format'].format(value)

    def get_rendered_object(self, obj=None):
        """Render object"""
        obj = obj if obj else self.object
        return [
            {
                **field,
                'value': self.render_field(field, obj)
            }
            for field in self.get_fields()
        ]

    def get_rendered_objects(self):
        """Render objects"""
        objects = self.objects

        if isinstance(objects, str):
            objects = getattr(self.object, objects).all()

        return [
            self.get_rendered_object(obj)
            for obj in objects
        ]


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


class DescriptionList(Component, ComponentFieldsMixin):
    """
    Bootstrap description, fields are the params. available options

    - horizontal
    """

    template_name = 'trionyx/components/description_list.html'
    horizontal = True
    no_data_message = "There is no data"

    def __init__(self, *fields, **options):
        """Init panel"""
        super().__init__(**options)
        self.fields = fields


class TableDescription(Component, ComponentFieldsMixin):
    """Bootstrap table description, fields are the params"""

    template_name = 'trionyx/components/table_description.html'

    fields_options = {
        'width': {
            'default': '150px',
        }
    }

    def __init__(self, *fields, **options):
        """Init panel"""
        super().__init__(**options)
        self.fields = fields


class Table(Component, ComponentFieldsMixin):
    """Bootstrap table"""

    template_name = 'trionyx/components/table.html'

    def __init__(self, objects, *fields, **options):
        """Init Table"""
        super().__init__(**options)

        self.objects = objects
        """Can be string with field name relation, Queryset or list"""

        self.fields = fields
