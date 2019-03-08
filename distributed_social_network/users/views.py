from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import User
from .forms import CustomUserCreationForm
from django.views.generic import ListView
from django.views import View

from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin

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

class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
    success_message = "Congratulations, you've successfully signed up! Wait to be approved."

class DeleteFriend(LoginRequiredMixin, View):
    def post(self):
        pass
