from trionyx import forms

from app.testblog.models import Tag, Post


@forms.register(code='new', default_edit=True)
class TagForm(forms.ModelForm):
    name = forms.CharField(label='name (default edit form)')

    class Meta:
        model = Tag
        fields=['name']


@forms.register(default_edit=True)
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'publish_date', 'category', 'status', 'price', 'tags']