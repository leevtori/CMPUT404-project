from django.urls import include, path
from django.conf.urls import url
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    
    path("search", views.UserList.as_view(), name='users'),
    path("friends/add/", views.AddFriend.as_view()),
    path("friends/delete/", views.DeleteFriend.as_view()),
    path("followers/confirm", views.ConfirmFriend.as_view()),
    path("friends", views.FriendList.as_view(), name='friends'),
    path("followers", views.FollowerList.as_view() , name='followers'),
    path('logout/', auth_views.LogoutView.as_view(template_name="logout.html"), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('account_settings/', views.AccountSettingsView.as_view(), name='account_settings')
]
