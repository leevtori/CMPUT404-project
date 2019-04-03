# users/admin.py

from django.contrib import admin
from .models import User, Node
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.db.models import Q
from posts.models import Post


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

class CustomNodeAdmin(UserAdmin):
    pass

# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(Node)

# (users) $ python manage.py makemigrations users
# (users) $ python manage.py migrate