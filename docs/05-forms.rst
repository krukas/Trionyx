Forms
=====

Forms are rendered in Trionyx with crispy forms using the bootstrap3 template.

Example:

.. code:: python

    from django import forms
    from crispy_forms.helper import FormHelper
    from crispy_forms.layout import Layout, Fieldset, Div

    class UserUpdateForm(forms.ModelForm):
        # your form fields

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.layout = Layout(
                'email',
                Div(
                    Fieldset(
                        'Personal info',
                        'first_name',
                        'last_name',
                        css_class="col-md-6",
                    ),
                    Div(
                        'avatar',
                        css_class="col-md-6",
                    ),
                    css_class="row"
                ),
                Fieldset(
                    'Change password',
                    'new_password1',
                    'new_password2',
                ),
            )

Crispy Forms
------------

Standard
~~~~~~~~
.. automodule:: crispy_forms.layout
    :members:

Bootstrap
~~~~~~~~~
.. automodule:: crispy_forms.bootstrap
    :members:

Trionyx
-------

TimePicker
~~~~~~~~~~

.. autoclass:: trionyx.trionyx.forms.layout.TimePicker
    :members:

