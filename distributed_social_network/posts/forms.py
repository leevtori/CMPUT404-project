from django.forms import ModelForm, widgets
from .models import Post, Categories


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'content', 'visible_to', 'visibility', 'unlisted', 'categories', 'content_type']
        widgets = {'content_type': widgets.HiddenInput}


class CategoryForm(ModelForm):
    class Meta:
        model = Categories
        fields = ['name']
        widgets = {'content_type': widgets.HiddenInput}