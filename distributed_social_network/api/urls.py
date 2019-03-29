from django.urls import path, include
from rest_framework import routers
from . import views

routers = routers.DefaultRouter()
routers.register('posts', views.PostViewSet, base_name="api-posts")
routers.register('author', views.AuthorViewset, base_name="api-author")

urlpatterns = [
    path('author/<uuid:pk>/friends/', views.FriendsView.as_view(), name="api-author-friends"),
    path('posts/<uuid:pk>/comments/', views.CommentView.as_view(), name="api-comments"),
    path('author/posts/', views.AuthorPostView.as_view(), name="api-author-post"),
    path('', include(routers.urls)),
]
