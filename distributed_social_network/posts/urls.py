from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.FeedView.as_view(), name='feed'),
    path('profile/<str:username>', views.ProfileView.as_view(), name='profile'),
    path('create/', views.create, name='create'),
    path('posts/<uuid:pk>', views.PostView.as_view(), name='post-detail'),
    path('newComment/', views.create_comment, name='new_comment')
]
