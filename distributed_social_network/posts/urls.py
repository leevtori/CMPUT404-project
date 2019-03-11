from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.FeedView.as_view(), name='feed'), 
    path('profile/<str:username>', views.ProfileView.as_view(), name='profile'),
    path('create/', views.create, name='create'),
]
