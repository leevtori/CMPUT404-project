# users/admin.py

from django.contrib import admin
from .models import User, Node
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['email', 'username',]

# Register your models here.
admin.site.register(User, CustomUserAdmin)
# admin.site.register(User)
admin.site.register(Node)

# (users) $ python manage.py makemigrations users
# (users) $ python manage.py migrate