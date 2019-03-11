from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect
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
        # get user object based on username in url
        user = get_object_or_404(User, username=self.kwargs['username'])
        #put user object in context
        context['user'] = user
        context['friend_count'] = self.request.user.friends.count
        context['follower_count'] = self.request.user.followers.count
        
        # pass context to template
        return context

    # overwrite get_queryset() to filter for posts by that user
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(author=user)


class FeedView(TemplateView):
    template_name = 'feed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_posts'] = Post.objects.all()[:5]
        return context


def create(request):
    # creates a post and redirects back to main page
    print(request.POST['content'])
    print(request.POST['visibility'])
    print(request.user.id)

    if request.method == "POST":
        new_post = Post(author=request.user,
                        title=request.POST['title'],
                        content=request.POST['content'],
                        description=request.POST['description'],
                        content_type=request.POST['type'])
        new_post.save()

    return HttpResponseRedirect('/')
