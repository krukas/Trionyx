from trionyx import forms

from app.testblog.models import Tag


@forms.register(default_edit=True)
class TagForm(forms.ModelForm):
    name = forms.CharField(label='name (default edit form)')

    class Meta:
        model = Tag
        fields=['name']
