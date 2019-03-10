from django.shortcuts import render, HttpResponse, get_object_or_404
from django.views.generic import ListView
from .models import Post
from django.contrib.auth import get_user_model
from django.views.generic.base import TemplateView



User = get_user_model()

class ProfileView(ListView):
    # model = Post
    template_name = 'profile.html'
    ordering = ['-created']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #get user object based on username in url
        user = get_object_or_404(User,username=self.kwargs['username'])
        context['user'] = user
        # pass user object to template
        return context
    
    #overwrite get_queryset() to filter for posts by that user
    def get_queryset(self):
        user = get_object_or_404(User,username=self.kwargs['username'])
        return Post.objects.filter(author=user)


class FeedView(TemplateView):
    template_name = 'feed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_posts'] = Post.objects.all()[:5]
        return context

