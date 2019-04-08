import json
from urllib.parse import urljoin
import asyncio

from django.shortcuts import HttpResponse, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from requests.auth import HTTPBasicAuth

from .models import Post, Comment
from django.contrib.auth import get_user_model
from django.views.generic.base import TemplateView
from users.views import FriendRequests
from django.conf import settings
import uuid
import requests
import urllib
import asyncio

from users.models import Node
from posts.forms import PostForm
from posts.serializers import requestPosts, requestSinglePost, request_single_user, friend_checking

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

        foaf = [item[0] for item in foaf]
        query_list.append(Q(author__id__in=foaf, visibility=Visibility.FOAF))
        query_list.append(Q(author__id__in=user.friends.all(), visibility=Visibility.FOAF))

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
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        for node in nodes:
            if node.active:
                loop.run_until_complete(requestPosts(node, 'posts',self.request.user.id))
                loop.run_until_complete(requestPosts(node, 'author/posts', self.request.user.id))
            #requestPosts(node, 'author/posts', self.request.user.id)
        loop.close()
        for frand in self.request.user.outgoingRequests.all():
            try:
                check_friend_url=frand.get_url()+'/friends/'+urllib.parse.quote(self.request.user.get_url(),safe="~()*!.'")
                print(check_friend_url)
                frand_check=requests.get(check_friend_url,headers={"X-AUTHOR-ID": str(self.request.user.id)},
                         auth=HTTPBasicAuth(frand.node.send_username, frand.node.send_password))
                if friend_checking(frand_check):
            #means the other guy accepted
                    self.request.user.friends.add(frand)
                    frand.followers.add(self.request.user)
                    self.request.user.following.add(frand)
                    frand.outgoingRequests.remove(self.request.user)
                    self.request.user.incomingRequests.remove(frand)
            #needs to be tested
            except:
                pass




        context = super().get_context_data(**kwargs)
        context['post_count'] = Post.objects.filter(author=self.request.user).count
        context['friend_count'] = self.request.user.friends.count
        context['follower_count'] = self.request.user.followers.count
        context['following_count']= self.request.user.following.count
        q = list(set(self.request.user.followers.all()).difference(set(self.request.user.friends.all())))
        context['requestCount'] = len(q)
        p = PostForm()
        # p.fields['visible_to'].queryset = self.request.user.friends.all()
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
        # if settings.HOSTNAME not in post.origin:
        #     node_url1 = post.origin.split('posts')[0]
        #     node_url = node_url1.split('api')[0]
        #     node= get_object_or_404(Node, hostname=node_url)
        #     requestSinglePost(post.origin, self.request.user.id,node)
        if post.author.host is not None:
            requestSinglePost(post.origin, self.request.user.id, post.author.host)

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
    #can't let someone else delete your post!
    if(post.author == request.user):
        post.delete()
        return redirect('feed')
    else:
        return HttpResponse(status=404)


def edit_post(request, pk):
    if request.method == "POST":
        post = get_object_or_404(Post, id=pk)
        #can't let someone else edit your post!
        if (post.author == request.user):
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


def github_activity(request):
    if request.method=="POST":
        f = PostForm(request.POST)
        if f.is_valid():
            new_post = f.save(commit=False)
            new_post.author = request.user

            git_username=request.user.github.split('/')[-1]
            print(git_username)
            git_api_url='https://api.github.com/users/{}/events?per_page=1'.format(git_username)
            github_request = requests.get(git_api_url)
            if github_request.status_code==200:
                a=json.loads(github_request.content)
                latest_activity = a[0]
                if latest_activity['type']=="ForkEvent":
                    new_post.content = "I just forked the repository {}, check out the original at {}".format(
                        latest_activity["forkee"]["name"],
                        latest_activity["forkee"]["url"]
                    )
                elif latest_activity['type']=="PushEvent":
                    new_post.content = "I just pushed {} commits to {} Branch, check it out at {}".format(
                        len(latest_activity["payload"]["commits"]),
                        latest_activity["repo"]["name"],
                        latest_activity["repo"]["url"]
                    )
                elif latest_activity['type'] == "ReleaseEvent":
                    new_post.content = "I just released my {} repository, check it out at {}".format(
                        latest_activity["repo"]["name"],
                        latest_activity["release"]["url"]
                    )
                elif latest_activity['type'] == "RepositoryEvent":
                    new_post.content = "I just {} a repository, {}".format(
                        latest_activity["action"],
                        latest_activity["repo"]["full_name"]
                    )

                elif latest_activity['type'] == "CreateEvent":
                    new_post.content = "I just added a {} to my {} repository, check it out at {}".format(
                        latest_activity["ref_type"],
                        latest_activity["repo"]["name"],
                        latest_activity["repo"]["url"]
                    )

                elif latest_activity['type'] == "DeleteEvent":
                    new_post.content = "I just deleted a {} from my {} repository, F to pay respect".format(
                        latest_activity["ref_type"],
                        latest_activity["repo"]["name"]
                    )
                else:
                    new_post.content="I just pull a {} to my {} repository and this server doesn't know how to handle that, that is unfortunate".format(
                        latest_activity["type"],
                        latest_activity['repo']['name']
                    )
            new_post.source = urljoin(settings.HOSTNAME, '/api/posts/%s' % new_post.id)
            new_post.origin = urljoin(settings.HOSTNAME, '/api/posts/%s' % new_post.id)
            new_post.save()
            return redirect('feed')
        else:
            print(f.errors)
            return redirect('feed')
