from django.urls import include, path
from django.conf.urls import url
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [
    path('logout/', auth_views.LogoutView.as_view(template_name="logout.html"), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html')),
    path('signup/', views.SignUp.as_view()),
]
