from django.shortcuts import render, HttpResponse
from django.views.generic import ListView
from .models import Post

class ProfileView(ListView):
    model = Post
