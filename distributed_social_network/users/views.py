from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render
from .models import User
from .forms import CustomUserCreationForm
from django.views.generic import ListView
from django.views import View

from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin

import json

class UserList(LoginRequiredMixin, ListView):
    """Lists all users on the server."""
    model = User
    context_object_name = "my_user_list"
    template_name = "user_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True)


class FriendList(LoginRequiredMixin, ListView):
    """This view lists all friends of logged in user."""
    model = User
    template_name = "friends_list.html"
    context_object_name = "my_friends_list"
    def get_queryset(self):
        return self.request.user.friends.all()


class AddFriend(LoginRequiredMixin, View):

    def post(self, **kwargs):
        body_unicode = self.request.body.decode('utf-8')
        body = json.loads(body_unicode)
        friend_id = body['id']
        friend = get_object_or_404(User, id=friend_id)
        self.request.user.friends.add(friend)
        self.request.user.save()



        pass


def addFriend(request):
    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        friend_id = body['id']

        friend = get_object_or_404(User, id = friend_id )
        request.user.friends.add(friend)
        request.user.save()
        
    return render(request, 'user_list.html')



class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
    success_message = "Congratulations, you've successfully signed up! Wait to be approved."

class DeleteFriend(LoginRequiredMixin, View):
    def post(self):
        pass
