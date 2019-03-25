from django.http import HttpResponseNotFound
from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Comment
from django.contrib.auth import get_user_model
from django.views.generic.base import TemplateView
from users.views import FriendRequests
import uuid
import requests
import base64

from django.db import connection
from django.db.models import Q
from .utils import Visibility

from functools import reduce
from operator import __or__

User = get_user_model()


class PostVisbilityMixin(LoginRequiredMixin):
    def filter_user_visible(self, user, qs):
        query_list = []

        # the user's own posts
        query_list.append(Q(author=user))

        #  Public posts
        query_list.append(Q(visibility=Visibility.PUBLIC))

        # Friends' posts
        query_list.append(Q(author__in=user.friends.all(), visibility=Visibility.FRIENDSONLY))

        # Friend of Friend
        # HACK: The ORM probably has a better way for doing this...
        with connection.cursor() as cursor:
            raw_sql = """SELECT DISTINCT from_user_id
                FROM users_user_friends
                WHERE to_user_id in (
                    SELECT to_user_id
                    FROM users_user_friends
                    WHERE from_user_id = %s
                ) AND from_user_id <> %s;"""
            cursor.execute(raw_sql, (user.id.hex, user.id.hex))
            foaf = cursor.fetchall()

        foaf = [uuid.UUID(item[0]) for item in foaf]
        query_list.append(Q(author__id__in=foaf, visibility=Visibility.FOAF))

        visible = user.visible_posts.all()

        # add unlisted, but don't show it in the feed
        query_list.append(Q(visibility=Visibility.UNLISTED))

        qs = qs.filter(reduce(__or__, query_list))
        # qs = qs.union(visible).distinct()  # this doesn't filter properly afterwards
        qs = (qs | visible).distinct()  # But this works... somehow?

        return qs

    """Filters posts to those viewable by the logged in user only."""
    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        qs = self.filter_user_visible(user, qs)

        return qs


class ProfileView(PostVisbilityMixin, ListView):
    model = Post
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get user object based on username in url
        user = get_object_or_404(User, username=self.kwargs['username'])
        # put user object in context
        context['user'] = user
        context['post_count'] = Post.objects.filter(author=user).count
        context['friend_count'] = user.friends.count
        context['follower_count'] = user.followers.count

        # pass context to template
        return context

    # overwrite get_queryset() to filter for posts by that user
    def get_queryset(self):
        qs = super().get_queryset()
        user = get_object_or_404(User, username=self.kwargs['username'])
        return qs.filter(author=user).order_by("-published")


class FeedView(PostVisbilityMixin, ListView):
    template_name = 'feed.html'
    model = Post
    ordering = '-published'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_count'] = Post.objects.filter(author=self.request.user).count
        context['friend_count'] = self.request.user.friends.count
        context['follower_count'] = self.request.user.followers.count
        q = list(set(self.request.user.followers.all()).difference(set(self.request.user.friends.all())))
        context['requestCount'] = len(q)

        #get all users who have me in their followers list
        followings = []
        for user in User.objects.all():
            if self.request.user in user.followers.all():
                followings.append(user)
        #get list of posts from user's followings
        following_posts = []
        qs = super().get_queryset()
        for post in qs:
            if post.author in followings:
                following_posts.append(post)
        context['following_posts'] = following_posts

        return context


class PostView(PostVisbilityMixin, DetailView):
    template_name = 'postview.html'
    model = Post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_comments'] = self.object.comment_set.all().order_by("-published")
        return context


def create(request):
    # creates a post and redirects back to main page
    if request.method == "POST":
        print(request.POST['visibility'])
        # i dont know if i need to do this if statement yet, just gonna leave this here in case
        if request.POST['type'] == 'text/plain':
            new_post = Post(author=request.user,
                            title=request.POST['title'],
                            content=request.POST['content'],
                            description=request.POST['description'],
                            content_type=request.POST['type'],
                            visibility=request.POST['visibility'])
            new_post.source = 'http://127.0.0.1:8000/posts/' + str(getattr(new_post, 'id'))
            new_post.save()

        # turns out forms the request type as "picture/png" but the specs requires us to save as "image/png"
        elif request.POST['type'] == 'image/jpeg' or request.POST['type'] == 'image/png':
            #print(request.POST['content'])
            picture = request.POST['content']
            print(type(picture))
            print(request.POST['visibility'])
            # saves the picture
            if request.POST['type'] == 'image/jpeg':
                new_post = Post(author=request.user,
                                title=request.POST['title'],
                                content=picture,
                                description=request.POST['description'],
                                content_type='image/jpeg;base64',
                                visibility=request.POST['visibility'],
                                unlisted=True)
            else:
                new_post = Post(author=request.user,
                                title=request.POST['title'],
                                content=picture,
                                description=request.POST['description'],
                                content_type='image/png;base64',
                                visibility=request.POST['visibility'],
                                unlisted=True)
            new_post.source = 'http://127.0.0.1:8000/posts/' + str(getattr(new_post, 'id'))

            # the next 3 lines were meant as a test, assuming that the image uploaded is a jpg
            # this will create a copy of it in the folder of this project
            # just going to leave this here in case something breaks

            new_post.save()
        elif request.POST['type'] == 'link':
            print('get picture')
            print(request.POST['visibility'])
            response = requests.get(request.POST['content'])
            encoded = base64.b64encode(response.content)
            sample_string = "data:{};base64,{}".format(response.headers['Content-Type'], encoded.decode())
            print(sample_string)
            if response.headers['Content-Type'] == 'image/jpeg':
                new_post = Post(author=request.user,
                                title=request.POST['title'],
                                content=sample_string,
                                description=request.POST['description'],
                                content_type='image/jpeg;base64',
                                visibility=request.POST['visibility'],
                                unlisted=True)
                new_post.source = 'http://127.0.0.1:8000/posts/' + str(getattr(new_post, 'id'))
                new_post.save()

            elif response.headers['Content-Type'] == 'image/png':
                new_post = Post(author=request.user,
                                title=request.POST['title'],
                                content=sample_string,
                                description=request.POST['description'],
                                content_type='image/png;base64',
                                visibility=request.POST['visibility'],
                                unlisted=True)
                new_post.source = 'http://127.0.0.1:8000/posts/' + str(getattr(new_post, 'id'))
                new_post.save()

                # testing purposes
                # f=open('testimg.png','wb')
                # f.write(response.content)
                # f.close()

        elif request.POST['type'] == 'text/markdown':
            print(request.POST['visibility'])
            new_post = Post(author=request.user,
                            title=request.POST['title'],
                            content=request.POST['content'],
                            description=request.POST['description'],
                            visibility=request.POST['visibility'],
                            content_type=request.POST['type'])
            new_post.source = 'http://127.0.0.1:8000/posts/' + str(getattr(new_post, 'id'))
            new_post.save()

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


def delete_comment(request):
    if request.method == "DELETE":
        post_id=request.META['HTTP_POSTID']
        to_be_deleted = get_object_or_404(Post, id=post_id)
        post_author = get_object_or_404(User, id=to_be_deleted.author.id)
        if post_author.id == request.user.id:
            to_be_deleted.delete()
            return HttpResponse('')

    return HttpResponseNotFound("hello")

