from django.urls import include, path
from django.conf.urls import url
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    
    path("list", views.UserList.as_view()),
    path("friends/add/", views.AddFriend.as_view()),
    # url("friends/add/", views.addFriend),
    path("friends/delete/", views.DeleteFriend.as_view()),
    path("friends", views.FriendList.as_view()),
    path('logout/', auth_views.LogoutView.as_view(template_name="logout.html"), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html')),
    path('signup/', views.SignUp.as_view()),
]
