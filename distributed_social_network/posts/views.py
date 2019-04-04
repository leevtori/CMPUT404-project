import json
from urllib.parse import urljoin

from django.shortcuts import HttpResponse, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Comment
from django.contrib.auth import get_user_model
from django.views.generic.base import TemplateView
from users.views import FriendRequests
from django.conf import settings
import uuid


from users.models import Node
from posts.forms import PostForm
from posts.serializers import requestPosts, requestSinglePost, request_single_user

from django.db import connection
from django.db.models import Q
from django.conf import settings
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

        query_list.append(Q(visibility=Visibility.SERVERONLY))

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

        # updates the user from nodes if foreign:
        if user.local == False:
            print('not local user, hope its not boom')
            request_single_user(user.host, user, self.request.user.id)

        # put user object in context
        context['user'] = user
        context['post_count'] = Post.objects.filter(author=user).count
        context['following_count']= user.following.count
        context['friend_count'] = user.friends.count
        context['follower_count'] = user.followers.count
        context['friends'] = user.friends.all()
        context['followers'] = user.followers.all()
        context['incomingFriendRequest'] = user.incomingRequests.all()


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
    paginate_by = 20

    def get_context_data(self, **kwargs):
        # get public posts from other hosts, using https://connectifyapp.herokuapp.com/ as test
        nodes = Node.objects.all()
        for node in nodes:
            if node.active:
                requestPosts(node, 'posts',self.request.user.id)
            #requestPosts(node, 'author/posts', self.request.user.id)

        context = super().get_context_data(**kwargs)
        context['post_count'] = Post.objects.filter(author=self.request.user).count
        context['friend_count'] = self.request.user.friends.count
        context['follower_count'] = self.request.user.followers.count
        context['following_count']= self.request.user.following.count
        q = list(set(self.request.user.followers.all()).difference(set(self.request.user.friends.all())))
        context['requestCount'] = len(q)
        p = PostForm()
        p.fields['visible_to'].queryset = self.request.user.friends.all()
        context['form'] = p


        following_posts = []
        qs = super().get_queryset()
        for post in qs:
            if post.author in self.request.user.following.all():
                following_posts.append(post)
        context['following_posts'] = following_posts

        return context


class PostDetailView(PostVisbilityMixin, DetailView):
    template_name = 'postview.html'
    model = Post

    def get_context_data(self, **kwargs):
        post=kwargs['object']
        #fetch the post
        if settings.HOSTNAME not in post.origin:
            node_url1 = post.origin.split('posts')[0]
            node_url = node_url1.split('api')[0]
            node= get_object_or_404(Node, hostname=node_url)
            requestSinglePost(post.origin, self.request.user.id,node)


        context = super().get_context_data(**kwargs)
        context['post_comments'] = self.object.comment_set.all().order_by("-published")
        context['form'] = PostForm(instance=post)

        return context


def create_post(request):
    if (request.method == "POST"):
        f = PostForm(request.POST)
        new_post = f.save(commit=False)
        new_post.author = request.user
        new_post.source = urljoin(settings.HOSTNAME, '/api/posts/%s' % new_post.id)
        new_post.origin = urljoin(settings.HOSTNAME, '/api/posts/%s' % new_post.id)

        new_post.save()
        new_post = f.save_m2m()

        return redirect('feed')

    else:
        return HttpResponse(status=404)

def delete_post(request, pk):
    post = Post.objects.get(id=pk)
    post.delete()
    return redirect('feed')


def edit_post(request, pk):
    if (request.method == "POST"):
        post = get_object_or_404(Post, id=pk)
        f = PostForm(request.POST, instance=post)
        f.save()
        return redirect('postdetail', pk=pk)
    else:
        return HttpResponse(status=404)

def add_comment(request):
    if request.method == "POST":
        post_id=request.POST['post']
        # select_post = Post.objects.get(id=post_id)
        select_post = get_object_or_404(Post, id=post_id)
        new_comment = Comment(
            post=select_post,
            comment=request.POST['comment'],
            author=request.user
        )
        new_comment.save()
        return redirect('postdetail', pk=post_id)
    else:
        return HttpResponse(status=404)


