from django.urls import path, include
from rest_framework import routers
from . import views

routers = routers.DefaultRouter()

urlpatterns = [
    path('', include(routers.urls))
]