from django.urls import include, path
from . import views

urlpatterns = [
    # path('', views.index, name="index_view"), 
    path('profile/<str:username>', views.ProfileView.as_view()),
]
