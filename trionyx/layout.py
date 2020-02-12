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
import datetime
import decimal
from typing import List, Dict, Union, Any

from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.conf import settings
from django.db.models import QuerySet

from trionyx import utils

register = template.Library()


class Colors:
    """Colors"""

    THEME = 'theme'
    LIGHT_BLUE = 'light-blue'
    AQUA = 'aqua'
    GREEN = 'green'
    YELLOW = 'yellow'
    RED = 'red'
    GRAY = 'gray'
    NAVY = 'navy'
    TEAL = 'teal'
    PURPLE = 'purple'
    ORANGE = 'orange'
    MAROON = 'maroon'
    BLACK = 'black'


class Layout:
    """Layout object that holds components"""

    def __init__(self, *components, **options):
        """Initialize Layout"""
        self.id = f'layout_{utils.random_string(8)}'.lower()
        self.update_url = ''
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

        # When ComponentFieldsMixin is used the value can be a component
        if isinstance(component, ComponentFieldsMixin):
            for field in component.get_fields():
                if isinstance(field.get('value'), Component):
                    files.extend(self.collect_css_files(field.get('value')))

        return list(set(files))

    def collect_js_files(self, component=None):
        """Collect all js files"""
        component = component if component else self
        files = getattr(component, 'js_files', None)
        files = files if files else []

        for comp in component.components:
            files.extend(self.collect_js_files(comp))

        # When ComponentFieldsMixin is used the value can be a component
        if isinstance(component, ComponentFieldsMixin):
            for field in component.get_fields():
                if isinstance(field.get('value'), Component):
                    files.extend(self.collect_js_files(field.get('value')))

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
            component.set_object(self.object, layout_id=self.id)

    def add_component(self, component, id=None, path=None, before=False, append=False):
        """
        Add component to existing layout can insert component before or after component

        :param component:
        :param id: component id
        :param path: component path, example: container.row.column6[1].panel
        :param append: append component to selected component from id or path
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

        if append:
            if before:
                comp.components.append(component)
            else:
                comp.components.insert(0, component)
        elif parent:
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

    template_name: str = ''
    """Component template to be rendered, default template only renders child components"""

    js_files: List[str] = []
    """List of required javascript files"""

    css_files: List[str] = []
    """List of required css files"""

    def __init__(self, *components, **options):
        """Initialize Component"""
        self.id = options.pop('id', None)
        self.css_id = f"component-{self.id}" if self.id else None
        self.layout_id = None
        self.components = list(filter(None, components))
        self.object = options.get('object', False)
        self.lock_object = options.get('lock_object', False)
        self.context = {}
        self.request = None

        # set options on object
        for key, value in options.items():
            setattr(self, key, value)

    def set_object(self, object, force=False, layout_id=None):
        """
        Set object for rendering component and set object to all components

        when object is set the layout should be complete with all components.
        So we also use it to set the layout_id so it's available in the updated method
        and also prevent whole other lookup of all components.

        :param object:
        :return:
        """
        if layout_id:
            self.layout_id = layout_id

        if not self.lock_object and (self.object is False or force):
            self.object = object
        else:
            object = self.object

        self.updated()

        # Pass object along to child components for rendering
        for component in self.components:
            component.set_object(object, force, layout_id)

    def updated(self):
        """Object updated hook method that is called when component is updated with object"""
        pass

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

    fields: List[Union[str, Dict[str, Any]]] = []
    """
    List of fields to be rendered. Item can be a string or dict, default options:

    - **field**: Name of object attribute or dict key to be rendered
    - **label**: Label of field
    - **value**: Value to be rendered (Can also be a component)
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

    fields_options: Dict[str, Dict[str, Any]] = {}
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

    objects: Union[str, list, QuerySet] = []
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

    def get_value(self, field, data):
        """Get value"""
        if 'value' in field:
            return field['value']
        elif isinstance(data, object) and field['field'] and hasattr(data, field['field']):
            return getattr(data, field['field'])
        elif isinstance(data, dict) and field['field'] in data:
            return data.get(field['field'])
        elif isinstance(data, list) and field['__index__'] < len(data):
            return data[field['__index__']]
        return ''

    def render_field(self, field, data):
        """Render field for given data"""
        from trionyx.renderer import renderer
        value = self.get_value(field, data)

        options = {key: value for key, value in field.items() if key not in ['value', 'data_object']}
        if 'renderer' in field:
            value = field['renderer'](value, data_object=data, **options)
        elif isinstance(value, Component):
            value.set_object(data, True, self.layout_id)
            value = value.render(self.context.copy(), self.request)
        elif isinstance(data, object) and field['field'] and hasattr(data, field['field']):
            value = renderer.render_field(data, field['field'], **field)
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
        return [
            self.get_rendered_object(obj)
            for obj in self.get_objects()
        ]

    def get_objects(self):
        """Get objects"""
        objects = self.objects

        if isinstance(objects, str):
            objects = getattr(self.object, objects).all()

        return objects


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

    tag: str = 'div'
    """Html tag nam"""

    attr: Dict[str, str] = {}
    """Dict with html attributes"""

    valid_attr: List[str] = []
    """Valid attributes that can be used"""

    color_class: str = ''
    """When color is set the will be used as class example: btn btn-{color}"""

    def __init__(self, *args, **kwargs):
        """Initialize HtmlTagWrapper"""
        super().__init__(*args, **kwargs)
        self.attr = self.attr.copy() if self.attr else {}

        if 'css_class' in kwargs:
            kwargs['class'] = kwargs.pop('css_class')
        elif 'color' in kwargs:
            self.attr['class'] = self.color_class.format(color=kwargs['color'])
            kwargs.pop('class', None)
        elif self.color_class:
            self.attr['class'] = self.color_class.format(color=Colors.THEME)
            kwargs.pop('class', None)

        if self.css_id:
            self.attr['id'] = self.css_id

        for key, value in kwargs.items():
            if key in self.valid_attr:
                self.attr[key] = value

    def get_attr_text(self):
        """Get html attr text to render in template"""
        return ' '.join([
            '{}="{}"'.format(key, value)
            for key, value in self.attr.items()
        ])


class OnclickTag(HtmlTagWrapper):
    """HTML tag with onlick for url or dialog"""

    valid_attr = ['onClick']

    def __init__(
        self, *components, url=None, model_url=None, model_params=None, model_code=None,
        sidebar=False, dialog=False, dialog_options=None,
        dialog_reload_tab=None, dialog_reload_sidebar=False, dialog_reload_layout=False, **options
    ):
        """Init tag"""
        super().__init__(*components, **options)
        self.url = url
        self.model_url = model_url
        self.model_code = model_code
        self.model_params = model_params
        self.sidebar = sidebar
        self.dialog = dialog
        self.dialog_options = dialog_options if dialog_options else {}
        self.on_click = options.get('onClick', False)
        self.dialog_reload_layout = dialog_reload_layout

        if dialog_reload_tab:
            self.dialog_options['callback'] = """function(data, dialog){{
                if (data.success) {{
                    dialog.close();
                    trionyx_reload_tab('{tab}');
                }}
            }}""".format(tab=dialog_reload_tab)
        elif dialog_reload_sidebar:
            self.dialog_options['callback'] = """function(data, dialog){
                if (data.success) {
                    dialog.close();
                    reloadSidebar();
                }
            }"""

    def updated(self):
        """Set onClick url based on object"""
        if self.dialog_reload_layout:
            self.dialog_options['callback'] = """function(data, dialog){{
                        if (data.success) {{
                            dialog.close();
                            txUpdateLayout('{id}', '{component}');
                        }}
                    }}""".format(
                id=self.layout_id,
                component=self.dialog_reload_layout if isinstance(self.dialog_reload_layout, str) else ''
            )

        if not self.on_click:
            from trionyx.urls import model_url
            url = model_url(
                model=self.object,
                view_name=self.model_url,
                code=self.model_code,
                params=self.model_params
            ) if self.model_url else self.url

            if not url and hasattr(self.object, 'get_absolute_url'):
                url = self.object.get_absolute_url()

            if self.dialog:
                self.attr['onClick'] = "openDialog('{}', {}); return false;".format(url, self.format_dialog_options())
            elif self.sidebar:
                self.attr['onClick'] = "openSidebar('{}'); return false;".format(url)
            else:
                self.attr['onClick'] = "window.location.href='{}'; return false;".format(url)

    def format_dialog_options(self):
        """Fromat options to JS dict"""
        return '{{ {} }}'.format(','.join(
            ("{}:{}" if key == 'callback' else "{}:'{}'").format(key, value)
            for key, value in self.dialog_options.items()))


class Html(HtmlTagWrapper):
    """Renders html in a tag when set"""

    template_name = 'trionyx/components/html.html'
    tag = ''

    def __init__(self, html=None, **kwargs):
        """Init Html"""
        super().__init__(**kwargs)
        self.html = html


class Img(Html):
    """Img tag"""

    tag = 'img'
    valid_attr = ['src', 'width', 'class']
    attr = {
        'width': '100%',
    }


class Link(Html):
    """Link tag"""

    tag = 'a'
    valid_attr = ['href', 'class']

    def __init__(self, label=None, href=None, **kwargs):
        """Init"""
        self.label = label
        self.href = href
        super().__init__(label, href=href, **kwargs)

    def updated(self):
        """Update link"""
        self.html = self.html if self.label else str(self.object)
        self.attr['href'] = self.attr['href'] if self.href else self.object.get_absolute_url()


class OnclickLink(OnclickTag):
    """Link"""

    tag = 'a'
    valid_attr = ['onClick', 'class']
    attr = {
        'href': '#',
    }

    def __init__(self, label, **options):
        """Init OnclickLink"""
        super().__init__(Html(label), **options)


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
class Badge(Html):
    """Bootstrap badge"""

    tag = 'span'
    valid_attr = ['class']
    color_class = 'badge bg-{color}'

    def __init__(self, field=None, html=None, **kwargs):
        """Init badge"""
        self.field = field
        super().__init__(html, **kwargs)

    def updated(self):
        """Set HTML with rendered field"""
        from trionyx.renderer import renderer
        self.html = renderer.render_field(self.object, self.field) if self.field else self.html


class Alert(Html):
    """Bootstrap alert"""

    INFO = 'info'
    SUCCESS = 'success'
    WARNING = 'warning'
    DANGER = 'danger'

    tag = 'div'
    color_class = 'alert alert-{color}'

    def __init__(self, html, alert='success', no_margin=False, **options):
        """Init alert"""
        options.pop('color', None)
        super().__init__(html, color=alert, **options)
        if no_margin:
            self.attr['class'] += ' no-margin'


class ButtonGroup(HtmlTagWrapper):
    """Bootstrap button group"""

    valid_attr = ['class']

    attr = {
        'class': 'btn-group'
    }


class Button(OnclickTag):
    """Bootstrap button"""

    tag = 'button'
    valid_attr = ['onClick', 'class']
    color_class = 'btn btn-flat bg-{color}'

    def __init__(self, label, **options):
        """Init button"""
        super().__init__(Html(label), **options)


class Thumbnail(OnclickTag):
    """Bootstrap Thumbnail"""

    tag = 'a'

    attr = {
        'href': '#',
        'class': 'thumbnail'
    }

    def __init__(self, src, **options):
        """Init thumbnail"""
        super().__init__(Img(src=src), **options)


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


class UnorderedList(Html, ComponentFieldsMixin):
    """Unordered list"""

    tag = 'ul'

    def __init__(self, *fields, objects=None, **options):
        """Init list"""
        super().__init__('', **options)
        self.objects = objects
        self.fields = fields

    def updated(self):
        """Set html with rendered fields"""
        if self.objects:
            values = [item[0]['value'] for item in self.get_rendered_objects()]
        else:
            values = [item['value'] for item in self.get_rendered_object()]

        sublist_indexes = {
            field['__index__']: field['label']
            for field in self.get_fields() if isinstance(field.get('value'), UnorderedList)
        }
        self.html = ''.join('<li>{label}{value}</li>'.format(
            label=sublist_indexes.get(index, ''),
            value=value
        ) for index, value in enumerate(values))


class OrderedList(UnorderedList):
    """Ordered list"""

    tag = 'ol'


class ProgressBar(Component):
    """Bootstrap progressbar, fields are the params"""

    template_name = 'trionyx/components/progressbar.html'

    def __init__(self, field='', value=0, max_value=100, size='md', striped=False, active=False, **options):
        """Init progressbar"""
        super().__init__(**options)
        self.field = field
        self.max_value = max_value
        self.value = value
        self.color = options.get('color', 'theme')
        self.striped = striped or active
        self.size = size
        self.active = active
        self.show_text = size not in ['sm', 'xs', 'xxs']

    def updated(self):
        """Set value with rendered field"""
        self.value = round((getattr(self.object, self.field, self.value) / self.max_value) * 100)


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

    def __init__(self, objects, *fields, css_class='table',
                 condensed=True, hover=False, striped=False, bordered=False, **options):
        """Init Table"""
        footer = options.pop('footer', None)
        super().__init__(**options)

        css_class = f'{css_class} table-condensed' if condensed else css_class
        css_class = f'{css_class} table-hover' if hover else css_class
        css_class = f'{css_class} table-striped' if striped else css_class
        css_class = f'{css_class} table-bordered' if bordered else css_class
        self.css_class = css_class

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


class Chart(Component, ComponentFieldsMixin):
    """Chart component"""

    chart_type = ''

    template_name = "trionyx/components/chart.html"

    css_files = ['plugins/chartjs/Chart.min.css']
    js_files = ['plugins/chartjs/Chart.min.js']

    def __init__(self, objects, *fields, **options):
        """Init Chart"""
        options['id'] = options.pop('id', utils.random_string(8))
        super().__init__(**options)
        self.chart_data = {}
        self.chart_scales = {}
        self.height = options.get('height', '300px')
        self.options = options

        self.objects = objects
        """Can be string with field name relation, Queryset or list"""

        self.fields = fields

        # Set all colors from, default first color is theme
        self.colors = {
            'blue': {
                'fill': 'rgba(60, 141, 188, 0.2)',
                'stroke': 'rgba(60, 141, 188, 1)',
            },
            'yellow': {
                'fill': 'rgba(243, 156, 18, 0.2)',
                'stroke': 'rgba(243, 156, 18, 1)',
            },
            'green': {
                'fill': 'rgba(0, 166, 90, 0.2)',
                'stroke': 'rgba(0, 166, 90, 1)',
            },
            'purple': {
                'fill': 'rgba(96, 92, 168, 0.2)',
                'stroke': 'rgba(96, 92, 168, 1)',
            },
            'red': {
                'fill': 'rgba(221, 75, 57, 0.2)',
                'stroke': 'rgba(221, 75, 57, 1)',
            },
            'black': {
                'fill': 'rgba(17, 17, 17, 0.2)',
                'stroke': 'rgba(17, 17, 17, 1)',
            },
        }
        self.color_order = ['blue', 'yellow', 'green', 'purple', 'red', 'black']
        self.theme_color = settings.TX_THEME_COLOR.replace('-light', '')

    def get_json_value(self, value):
        """Get json value"""
        if issubclass(value.__class__, (int, float, str, bool)):
            return value
        if isinstance(value, decimal.Decimal):
            return float(value)
        if isinstance(value, datetime.date):
            return time.mktime(value.timetuple()) * 1000
        return str(value)

    def get_colors(self, size, color_type):
        """Get colors"""
        colors = []

        if self.theme_color in self.colors:
            colors.append(self.colors[self.theme_color][color_type])

        for name, color_types in self.colors.items():
            if len(colors) >= size:
                break

            if name == self.theme_color:
                continue

            colors.append(color_types[color_type])

        return colors

    def get_color(self, index, color_type):
        """Get color"""
        return self.get_colors(10, color_type)[index]


class LineChart(Chart):
    """LineChart"""

    chart_type = 'line'

    def updated(self):
        """Set chart data and scales"""
        fields = self.get_fields()
        items = self.get_objects()

        self.chart_data = {
            'labels': [self.get_json_value(self.get_value(fields[0], item)) for item in items],
            'datasets': [
                {
                    'label': fields[index]['label'],
                    'backgroundColor': self.get_color(index - 1, 'fill'),
                    'borderColor': self.get_color(index - 1, 'stroke'),
                    'fill': self.options.get('fill', True),
                    'data': [{
                        'x': self.get_json_value(self.get_value(fields[0], item)),
                        'y': self.get_json_value(self.get_value(fields[index], item)),
                        'label': self.render_field(fields[index], item),
                    } for item in items],
                } for index in range(1, len(fields))
            ],
        }

        if items and isinstance(self.get_value(fields[0], items[0]), datetime.date):
            unit = 'hour' if isinstance(self.get_value(fields[0], items[0]), datetime.datetime) else 'day'
            self.chart_scales = {
                'xAxes': [{
                    'type': 'time',
                    'autoSkip': False,
                    'time': {
                        'unit': self.options.get('time_unit', unit),
                        'unitStepSize': self.options.get('time_unit_step_size', 1),
                    },
                }]
            }


class BarChart(LineChart):
    """BarChart"""

    chart_type = 'bar'


class PieChart(Chart):
    """BarChart"""

    chart_type = 'pie'

    def updated(self):
        """Set chart data and scales"""
        fields = self.get_fields()
        items = self.get_objects()

        self.chart_data = {
            'labels': [self.render_field(fields[0], item) for item in items],
            'datasets': [{
                'label': fields[1]['label'],
                'data': [self.get_json_value(self.get_value(fields[1], item)) for item in items],
                'backgroundColor': self.get_colors(len(items), 'fill'),
                'borderColor': self.get_colors(len(items), 'stroke'),
                'borderWidth': 1,
            }]
        }


class DoughnutChart(PieChart):
    """BarChart"""

    chart_type = 'doughnut'
