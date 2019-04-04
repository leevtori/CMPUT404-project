# users/admin.py

from django.contrib import admin
from .models import User, Node, ConnectedServer
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.db.models import Q
from posts.models import Post


class NodeInline(admin.StackedInline):
    model = Node
    fieldsets = (
        ("Server Information", {
            "fields": ("hostname", "prefix"),
            "description" : "Who are we connecting to?"
        }),
        ("Authentication Information", {
            "fields" : ("send_username", "send_password"),
            "description": "The credentials to get your connected server's posts, given by them."
        }),
        ("Active", {
            "fields": ("active", ),
            "description": "Get posts from them, and allow them to get our posts?"
        })
    )
    can_delete = False


class CustomUserAdmin(UserAdmin):

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ['username', 'email',]
    list_display_links = ('username', )
    UserAdmin.fieldsets += (
    ('Important stats', {
        'fields': (
            'friends', 'followers'
    )}),)

    def get_queryset(self, request):
        nodes = Node.objects.values_list('user_auth', flat=True)
        qs = User.objects.all().exclude(id__in=nodes)
        return qs


class NodeAdmin(UserAdmin):
    inlines = (NodeInline, )
    list_display = ('node',)
    fieldsets = (
        ("Authentication", {
            'fields': ('username', 'password'),
            'description': "Credentials for your connected server to get your posts"
        }),
    )

    def get_queryset(self, request):
        return User.objects.filter(id__in=Node.objects.all().values('user_auth'))

    def node(self, obj):
        return Node.objects.get(user_auth=obj)


# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(ConnectedServer, NodeAdmin)

# (users) $ python manage.py makemigrations users
# (users) $ python manage.py migrate