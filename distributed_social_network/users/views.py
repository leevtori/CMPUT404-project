from django.contrib.auth import authenticate, login
# from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404

from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import User
from .forms import CustomUserCreationForm
from django.views.generic import ListView
from django.views import View

from django.contrib.auth.mixins import LoginRequiredMixin


def signup(request):
    if request.method == "POST":
        # form = UserCreationForm(request.POST)
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # username = form.cleaned_data.get('username')
            # raw_password = form.cleaned_data.get('password1')
            # user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


class UserList(LoginRequiredMixin, ListView):
    """Lists all users on the server."""
    model = User
    template_name = "user_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True)


class FriendList(LoginRequiredMixin, ListView):
    """This view lists all friends of logged in user."""
    model = User
    template_name = "friends_list.html"

    def get_queryset(self):
        return self.request.user.friends.all()


class AddFriend(LoginRequiredMixin, View):
    def post(self):
        pass


class DeleteFriend(LoginRequiredMixin, View):
    def post(self):
        pass
