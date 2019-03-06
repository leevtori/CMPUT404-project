from django.urls import include, path
from django.conf.urls import url
# from django.contrib.auth.views import login

from . import views

urlpatterns = [
    path('', views.index, name="index_view"), 
    path('login/', views.login_view, name="login_view"),
    path('logout/', views.logout_view, name="logout_view"),
    path('signup/', views.signup , name='signup_view')
]
