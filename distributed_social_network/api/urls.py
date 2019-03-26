from django.urls import path, include
from rest_framework import routers
from . import views

routers = routers.DefaultRouter()
routers.register('posts', views.PostViewSet, base_name="api-posts")
routers.register('author', views.AuthorViewset, base_name="api-author")

urlpatterns = [
    path('', include(routers.urls)),
]
