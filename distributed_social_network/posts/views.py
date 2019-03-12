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
        context['latest_posts'] = Post.objects.filter(unlisted=False)[:5]
        return context





def create(request):
    # creates a post and redirects back to main page
    if request.method == "POST":
        # i dont know if i need to do this if statement yet, just gonna leave this here in case
        if request.POST['type'] == 'text/plain':
            new_post = Post(author=request.user,
                            title=request.POST['title'],
                            content=request.POST['content'],
                            description=request.POST['description'],
                            content_type=request.POST['type'])
            new_post.save()
        elif request.POST['type'] == 'image/jpeg' or request.POST['type'] == 'image/png':
            picture_location = request.FILES['content']
            picture = picture_location.read()
            #saves the picture
            new_post = Post(author=request.user,
                            title=request.POST['title'],
                            content=picture,
                            description=request.POST['description'],
                            content_type=request.POST['type'],
                            unlisted=True)
            new_post.save()

            #the next 3 lines were meant as a test, assuming that the image uploaded is a jpg
            #this will create a copy of it in the folder of this project
            # just going to leave this here in case something breaks

            #f=open('testimg.jpg','wb')
            #f.write(picture)
            #f.close()

    return HttpResponseRedirect('/')
