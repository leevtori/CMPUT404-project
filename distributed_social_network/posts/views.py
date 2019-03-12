from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect
from django.views.generic import ListView
from .models import Post, Comment
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
        # put user object in context
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
        # context['latest_posts'] = Post.objects.filter(unlisted=False)[:5]
        context['latest_posts'] = Post.objects.all()[:5]
        return context


class PostView(TemplateView):
    template_name = 'postview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, id=self.kwargs['postid'])
        context['post'] = post
        context['post_comments'] = Comment.objects.filter(post=post)
        return context


def create(request):
    print(request.POST['type'])
    # creates a post and redirects back to main page
    if request.method == "POST":
        # i dont know if i need to do this if statement yet, just gonna leave this here in case
        if request.POST['type'] == 'text/plain':
            new_post = Post(author=request.user,
                            title=request.POST['title'],
                            content=request.POST['content'],
                            description=request.POST['description'],
                            content_type=request.POST['type'])
            new_post.source = 'http://127.0.0.1:8000/posts/' + str(getattr(new_post,'id'))
            new_post.save()

        # turns out forms the request type as "picture/png" but the specs requires us to save as "image/png"
        elif request.POST['type'] == 'image/jpeg' or request.POST['type'] == 'picture/png':
            print('saving picture')
            picture_location = request.FILES['content']
            picture = picture_location.read()
            # saves the picture
            if request.POST['type'] == 'image/jpeg':
                new_post = Post(author=request.user,
                                title=request.POST['title'],
                                content=picture,
                                description=request.POST['description'],
                                content_type='image/jpeg;base64',
                                unlisted=True)
            else:
                new_post = Post(author=request.user,
                                title=request.POST['title'],
                                content=picture,
                                description=request.POST['description'],
                                content_type='image/png;base64',
                                unlisted=True)
            new_post.save()

            # the next 3 lines were meant as a test, assuming that the image uploaded is a jpg
            # this will create a copy of it in the folder of this project
            # just going to leave this here in case something breaks

            # f=open('testimg.png','wb')
            # f.write(picture)
            # f.close()

    return HttpResponseRedirect('/')


def create_comment(request):
    if request.method == "POST":
        select_post = get_object_or_404(Post, id=request.POST['post'])
        new_comment = Comment(
            post=select_post,
            comment=request.POST['comment'],
            author=request.user
        )
        new_comment.save()
    return HttpResponseRedirect(select_post.source)
