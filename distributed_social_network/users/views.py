from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render, HttpResponse, HttpResponseRedirect
from .models import User
from .forms import CustomUserCreationForm
from django.views.generic import ListView
from django.views.generic.edit import UpdateView
from django.views import View

from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin

import json

class UserList(LoginRequiredMixin, ListView):
    """Lists all users on the server."""
    model = User
    template_name = "user_list.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_user'] = self.request.user
        context['friends'] = self.request.user.friends.all()

        return context

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(is_active=True).order_by("username")


class FriendList(LoginRequiredMixin, ListView):
    """This view lists all friends of logged in user."""
    model = User
    template_name = "friends_list.html"
    
    def get_queryset(self):
        return self.request.user.friends.all()

class FollowerList(LoginRequiredMixin, ListView):
    """This view lists all the followers of logged in user. """
    model = User
    template_name = "followers_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['friends'] = self.request.user.friends.all()
        return context

    def get_queryset(self):
        return self.request.user.followers.all()

class SendFriendRequest(LoginRequiredMixin, View):

    def post(self, request):
        body_unicode = self.request.body.decode('utf-8')
        body = json.loads(body_unicode)
        friend_id = body['id']
        print("added ", friend_id)
        friend = get_object_or_404(User, id=friend_id)
        friend.followers.add(self.request.user)

        return HttpResponse('added')


class ConfirmRequest(LoginRequiredMixin, View):

    def post(self, requst):
        body_unicode = self.request.body.decode('utf-8')
        body = json.loads(body_unicode)
        friend_id = body['id']
        friend = get_object_or_404(User, id=friend_id)
        self.request.user.friends.add(friend)
        friend.followers.add(self.request.user)
        return HttpResponseRedirect('/profile/'+self.request.username)

class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
    success_message = "Congratulations, you've successfully signed up! Wait to be approved."

class DeleteFriend(LoginRequiredMixin, View):    
    model = User

    def delete(self, request):
        body_unicode = self.request.body.decode('utf-8')
        body = json.loads(body_unicode)
        friend_id = body['id']
        friend = get_object_or_404(User, id=friend_id)
        self.request.user.friends.remove(friend_id)
        self.request.user.followers.remove(friend_id)
        friend.followers.remove(self.request.user.id)
        context = {'object_list': self.request.user.friends.all()}
        return render(request, 'friends_list.html', context)


class AccountSettingsView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name','last_name', 'display_name', 'github', 'bio', 'is_active']
    template_name = 'account_settings.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('profile', kwargs={'username':self.request.user.username})
        
