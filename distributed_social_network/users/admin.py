# users/admin.py

from django.contrib import admin
from .models import User, Node
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm


# class ProfileInline(admin.StackedInline):
#     model = User
#     can_delete = False


class CustomUserAdmin(UserAdmin):
    # inlines = (ProfileInline, )

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['email', 'username']
    UserAdmin.fieldsets += ('Important stats', {'fields': ('friends', 'followers')}),
 

# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(Node)

# (users) $ python manage.py makemigrations users
# (users) $ python manage.py migrate