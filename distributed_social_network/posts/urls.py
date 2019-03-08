from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.FeedView.as_view()), 
    path('profile/<str:username>', views.ProfileView.as_view()),
]
