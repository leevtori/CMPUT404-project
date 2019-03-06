from django.urls import include, path
from django.conf.urls import url
from django.contrib.auth import views as auth_views


from . import views

urlpatterns = [

    url(r'^logout/$', auth_views.LogoutView.as_view(template_name="logout.html")),
    url(r'^signup/$', views.signup , name='signup_view'),
    # path('signup/', views.SignUp.as_view(), name='signup'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='login.html'))
]
