from django.urls import include, path
from django.conf.urls import url
# from django.contrib.auth.views import login

from . import views

urlpatterns = [
    path('', views.index, name="index_view"), 
    path('login/', views.my_view, name="my_view"),
    path('signup/', views.signup , name='signup_view')
]
