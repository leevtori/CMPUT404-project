from django.urls import include, path
from django.conf.urls import url
# from django.contrib.auth.views import login

from . import views

urlpatterns = [
    path('login/', views.login, name="login_view")
]
