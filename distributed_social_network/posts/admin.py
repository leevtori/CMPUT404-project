from django.contrib import admin
from .models import Post, Comment



class CustomPostAdmin(admin.ModelAdmin):
    model = Post
    list_display = ['title', 'author',]

class CustomCommentAdmin(admin.ModelAdmin):
    model = Comment
    list_display = ['comment', 'author', 'get_post_title']

    def get_post_title(self, obj):
        return obj.post.title
    get_post_title.short_description = "Post Title"


# Register your models here.
admin.site.register(Post, CustomPostAdmin)
admin.site.register(Comment, CustomCommentAdmin)