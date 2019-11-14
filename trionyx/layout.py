# copyright 2019 by Maikel Martens
#
# license GPLv3

"""
Layout and Components
=====================

Layouts are used to render a view for an object.
Layouts are defined and registered in layouts.py in an app.


**Example of a tab layout for the user profile:**

.. code-block:: python

    @tabs.register('trionyx.profile')
    def account_overview(obj):
        return Container(
            Row(
                Column2(
                    Panel(
                        'Avatar',
                        Img(src="{}{}".format(settings.MEDIA_URL, obj.avatar)),
                        collapse=True,
                    ),
                ),
                Column10(
                    Panel(
                        'Account information',
                        DescriptionList(
                            'email',
                            'first_name',
                            'last_name',
                        ),
                    )
                ),
            )
        )


"""
import re
import time

from django import template
from django.utils.functional import cached_property
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.conf import settings
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

    def get_paths(self):
        """Get all paths in layout for easy lookup"""
        def generate_paths(component=None, path=None, index=None):
            """Generate all paths in layout"""
            path = [
                *path,
                str(component.__class__.__name__ + '-' + str(index)).lower()
            ]
            paths = {'.'.join(path): component}

            for index, comp in enumerate(component.components):
                paths.update(generate_paths(comp, path, index))
            return paths

        paths = {}
        for index, comp in enumerate(self.components):
            paths.update(generate_paths(comp, [], index))

        # Can't cache paths because after one change the are not valid
        return paths

    def find_component_by_path(self, path):
        """Find component by path, gives back component and parent"""
        path_re = re.compile(r'([\wd]+)(\[(\d+)\])?')
        new_path = []
        for p in path.lower().split('.'):
            match = path_re.match(p)
            new_path.append('{}-{}'.format(
                match.group(1),
                match.group(3) if match.group(3) else 0
            ))

        paths = self.get_paths()
        return (
            paths.get('.'.join(new_path)),
            paths.get('.'.join(new_path[:-1]))
        )

    def find_component_by_id(self, id=None, current_comp=None):
        """Find component by id, gives back component and parent"""
        current_comp = current_comp if current_comp else self

        for comp in current_comp.components:
            if id and comp.id == id:
                return (comp, current_comp)

        for comp in current_comp.components:
            r_comp, r_parent = self.find_component_by_id(id=id, current_comp=comp)
            if r_comp:
                return (r_comp, r_parent)

        return (None, None)

    def render(self, request=None):
        """Render layout for given request"""
        return render_to_string('trionyx/layout.html', {
            'layout': self,
            'css_files': self.collect_css_files(),
            'js_files': self.collect_js_files(),
        }, request)

    def collect_css_files(self, component=None):
        """Collect all css files"""
        component = component if component else self
        files = getattr(component, 'css_files', None)
        files = files if files else []

        for comp in component.components:
            files.extend(self.collect_css_files(comp))

        return list(set(files))

    def collect_js_files(self, component=None):
        """Collect all js files"""
        component = component if component else self
        files = getattr(component, 'js_files', None)
        files = files if files else []

        for comp in component.components:
            files.extend(self.collect_js_files(comp))

        return list(set(files))

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

    def add_component(self, component, id=None, path=None, before=False):
        """
        Add component to existing layout can insert component before or after component

        :param component:
        :param id: component id
        :param path: component path, example: container.row.column6[1].panel
        :return:
        """
        if not id and not path:
            if before:
                self.components.append(component)
            else:
                self.components.insert(0, component)

        if id:
            comp, parent = self.find_component_by_id(id)
        else:
            comp, parent = self.find_component_by_path(path)

        if not comp:
            raise Exception('Could not add component: Unknown path {} or id {}'.format(path, id))

        if parent:
            index = parent.components.index(comp) if before else parent.components.index(comp) + 1
            parent.components.insert(index, component)
        elif comp:
            index = self.components.index(comp) if before else self.components.index(comp) + 1
            self.components.insert(index, component)

    def delete_component(self, id=None, path=None):
        """
        Delete component for given path or id

        :param id: component id
        :param path: component path, example: container.row.column6[1].panel
        :return:
        """
        if not id and not path:
            raise Exception('You must supply an id or path')

        if id:
            comp, parent = self.find_component_by_id(id)
        else:
            comp, parent = self.find_component_by_path(path)

        if not comp:
            raise Exception('Could not delete component: Unknown path {} or id {}'.format(path, id))

        if parent:
            parent.components.remove(comp)
        elif comp:
            self.components.remove(comp)


class Component:
    """Base component can be use as an holder for other components"""

    template_name = None
    """Component template to be rendered, default template only renders child components"""

    js_files = None
    """List of required javascript files"""

    css_files = None
    """List of required css files"""

    def __init__(self, *components, **options):
        """Initialize Component"""
        self.id = options.get('id')
        self.components = list(filter(None, components))
        self.parent = None
        self.object = options.get('object', False)
        self.context = {}
        self.request = None

        # set options on object
        for key, value in options.items():
            setattr(self, key, value)

    @cached_property
    def css_id(self):
        """Generate random css id for component"""
        return 'component-{}'.format(utils.random_string(6))

    def set_object(self, object, force=False):
        """
        Set object for rendering component and set object to all components

        :param object:
        :return:
        """
        if self.object is False or force:
            self.object = object
        else:
            object = self.object

        # Pass object along to child components for rendering
        for component in self.components:
            component.set_object(object)

    def render(self, context, request=None):
        """Render component"""
        context['component'] = self
        self.context = context
        self.request = request

        if settings.DEBUG:
            path = [
                *getattr(self, '_debug_path', []),
                '{name}[{index}]'.format(
                    name=str(self.__class__.__name__).lower(),
                    index=getattr(self, '_debug_path_index', 0),
                )
            ]
            self._debug_full_path = '.'.join(path)
            for index, comp in enumerate(self.components):
                comp._debug_path = path
                comp._debug_path_index = index

            start_time = time.time()

        if self.template_name:
            output = render_to_string(self.template_name, context, request)
        else:
            output = ''.join(comp.render(context, request) for comp in self.components)

        if settings.DEBUG:
            output = """
                <!--{class_name}: {template_name}-->
                <!--Path: {path}-->
                <!--Render time: {render_time}-->
                {output}
            """.format(
                class_name=".".join([self.__class__.__module__, self.__class__.__name__]),
                template_name=self.template_name,
                path=self._debug_full_path,
                render_time=round(time.time() - start_time, 4),
                output=output,
            )

        return mark_safe(output)


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
    - **component**: Render field with given component, row object will be set as the component object

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

    def add_field(self, field, index=None):
        """Add field"""
        self.fields = list(self.fields)
        if index is not None:
            self.fields.insert(index, field)
        else:
            self.fields.append(field)

    def get_fields(self):
        """Get all fields"""
        if not hasattr(self, '__fields'):
            self.__fields = [
                self.parse_field(field, index)
                for index, field in enumerate(getattr(self, 'fields', []))
                if not (field is False or field is None)
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
            model = self.objects.model if isinstance(self.objects, QuerySet) else self.object
            try:
                field['label'] = model._meta.get_field(field['field']).verbose_name.capitalize()
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

        if 'component' in field:
            component = field.get('component')
            component.set_object(data, True)
            return component.render(self.context)

        if 'value' in field:
            value = field['value']
        elif isinstance(data, object) and field['field'] and hasattr(data, field['field']):
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
        elif isinstance(value, Component):
            value.set_object(data, True)
            value = value.render(self.context.copy(), self.request)
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
class HtmlTemplate(Component):
    """HtmlTemplate render django html template"""

    def __init__(self, template_name, context=None, css_files=None, js_files=None):
        """Initialize HtmlTemplate"""
        super().__init__()
        self.template_name = template_name
        self.context = context
        self.css_files = css_files if css_files else []
        self.js_files = js_files if js_files else []

    def render(self, context, request=None):
        """Render component"""
        context['component'] = self
        context.update(self.context)
        self.context = context
        self.request = request
        return render_to_string(self.template_name, context, request)


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
        self.attr = self.attr.copy() if self.attr else {}

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
        kwargs['class'] = kwargs.pop('css_class', self.attr.get('class', ''))
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


class Input(Html):
    """Input tag"""

    template_name = 'trionyx/components/input.html'

    valid_attr = ['name', 'value', 'type', 'placeholder', 'class']
    attr = {
        'type': 'text',
        'class': 'form-control',
    }

    def __init__(self, form_field=None, has_error=False, **kwargs):
        """Init input"""
        super().__init__(None, **kwargs)
        self.has_error = has_error

        if form_field:
            self.attr['name'] = form_field.name
            self.attr['value'] = form_field.value()
            self.has_error = form_field.errors

        if 'value' in self.attr and self.attr['value'] is None:
            self.attr['value'] = ''


class ButtonGroup(HtmlTagWrapper):
    """Bootstrap button group"""

    attr = {
        'class': 'btn-group'
    }


class Button(Html):
    """
    Bootstrap button

    - link_url
    - dialog_url
    - onClick
    """

    tag = 'button'
    valid_attr = ['onClick', 'class']
    attr = {
        'class': 'btn btn-flat bg-theme'
    }

    def __init__(
        self, label, url=None, model_url=None, model_params=None, model_code=None,
        dialog=False, dialog_options=None, dialog_reload_tab=None, **options
    ):
        """Init button"""
        super().__init__(html=label, **options)
        self.url = url
        self.model_url = model_url
        self.model_code = model_code
        self.model_params = model_params
        self.dialog = dialog
        self.dialog_options = dialog_options if dialog_options else {}
        self.on_click = options.get('onClick', False)

        if dialog_reload_tab:
            self.dialog_options['callback'] = """function(data, dialog){{
                if (data.success) {{
                    dialog.close();
                    trionyx_reload_tab('{tab}');
                }}
            }}""".format(tab=dialog_reload_tab)

    def set_object(self, object):
        """Set object and onClick"""
        super().set_object(object)

        if not self.on_click:
            from trionyx.urls import model_url
            url = model_url(
                model=object,
                view_name=self.model_url,
                code=self.model_code,
                params=self.model_params
            ) if self.model_url else self.url
            if self.dialog:
                self.attr['onClick'] = "openDialog('{}', {}); return false;".format(url, self.format_dialog_options())
            else:
                self.attr['onClick'] = "window.location.href='{}'; return false;".format(url)

    def format_dialog_options(self):
        """Fromat options to JS dict"""
        return '{{ {} }}'.format(','.join(
            ("{}:{}" if key == 'callback' else "{}:'{}'").format(key, value)
            for key, value in self.dialog_options.items()))


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
    """
    Bootstrap table

    footer: array with first items array/queryset and other items are the fields,
            Same way how the constructor works

    """

    template_name = 'trionyx/components/table.html'

    def __init__(self, objects, *fields, **options):
        """Init Table"""
        footer = options.pop('footer', None)
        super().__init__(**options)

        self.objects = objects
        """Can be string with field name relation, Queryset or list"""

        self.fields = fields

        self.footer_objects = footer[0] if footer else None
        """Can be string with field name relation, Queryset or list"""

        self.footer_fields = footer[1:] if footer else []

    def get_footer_fields(self):
        """Get all footer fields"""
        if not hasattr(self, '__footer_fields'):
            self.__footer_fields = [
                self.parse_field(field, index)
                for index, field in enumerate(self.footer_fields)
            ]
        return self.__footer_fields

    def get_rendered_footer_object(self, obj):
        """Render footer object"""
        return [
            {
                **field,
                'value': self.render_field(field, obj)
            }
            for field in self.get_footer_fields()
        ]

    def get_rendered_footer_objects(self):
        """Render footer objects"""
        objects = self.footer_objects

        if isinstance(objects, str):
            objects = getattr(self.object, objects).all()

        return [
            self.get_rendered_footer_object(obj)
            for obj in objects
        ]
