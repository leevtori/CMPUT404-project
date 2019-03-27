from django.forms import ModelForm
from .models import Post

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'content', 'visible_to', 'visibility', 'unlisted', 'categories']
        
    