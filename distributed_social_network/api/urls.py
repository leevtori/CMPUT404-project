from django.urls import path, include
from rest_framework import routers
from . import views

routers = routers.DefaultRouter()
routers.register('posts', views.PostViewSet)
routers.register('author', views.AuthorViewset)

urlpatterns = [
    path('', include(routers.urls))
]