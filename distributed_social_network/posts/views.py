import json

from django.shortcuts import HttpResponse, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Post, Comment
from django.contrib.auth import get_user_model
from django.views.generic.base import TemplateView
from users.views import FriendRequests
import uuid


from users.models import Node
from posts.forms import PostForm
from posts.serializers import requestPosts

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
        # get public posts from other hosts, using https://connectifyapp.herokuapp.com/ as test
        nodes = Node.objects.all()
        for node in nodes:
            requestPosts(node, 'posts',self.request.user.id)
            requestPosts(node, 'author/posts', self.request.user.id)

        context = super().get_context_data(**kwargs)
        context['post_count'] = Post.objects.filter(author=self.request.user).count
        context['friend_count'] = self.request.user.friends.count
        context['follower_count'] = self.request.user.followers.count
        q = list(set(self.request.user.followers.all()).difference(set(self.request.user.friends.all())))
        context['requestCount'] = len(q)
        context['form'] = PostForm()

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
        context = super().get_context_data(**kwargs)
        context['post_comments'] = self.object.comment_set.all().order_by("-published")
        return context


def create_post(request):
    if (request.method == "POST"):
        f = PostForm(request.POST)
        new_post = f.save(commit=False)
        new_post.author = request.user
        new_post.save()
        print("@@@@@@",new_post)
        return redirect('feed')
        
    else:
        return HttpResponse(status=404)

def delete_post(request, pk):
    if (request.method == "GET"):
        post = Post.objects.get(id=pk)
        post.delete()
        return redirect('feed')
    else: 
        return HttpResponse(status=404)

def add_comment(request):
    if request.method == "POST":
        post_id=request.POST['post']
        select_post = Post.objects.get(id=post_id)
        new_comment = Comment(
            post=select_post,
            comment=request.POST['comment'],
            author=request.user
        )
        new_comment.save()
        return redirect('postdetail', pk=post_id)
    else:
        return HttpResponse(status=404)





























# def postapi(request, rid):
#     # creates a post and redirects back to main page
#     if request.method == "POST":
#         data = json.loads(request.body.decode("utf-8"))
#         if Post.objects.filter(id=data["id"]).count() != 0:
#             return HttpResponse(status=400)
#         if data["id"] != str(rid):
#             return HttpResponse(status=400)
#         new_post = Post(id=data["id"],
#                         author=request.user,
#                         title=data["title"],
#                         content=data['content'],
#                         description=data['description'],
#                         content_type=data['type'],
#                         visibility=data['visibility'])

#         new_post.source = 'http://127.0.0.1:8000/posts/' + str(getattr(new_post, 'id'))
#         new_post.origin = new_post.source

#         new_post.save()
#         return HttpResponse(status=200)
#     elif request.method == "GET":
#         if "python" in request.META['HTTP_USER_AGENT'].lower():
#             # TODO:
#             # if the node is authenticated
#             if True:
#                 desired_post = get_object_or_404(Post, id=rid)
#                 post_author = desired_post.author
#                 post_comments=Comment.objects.filter(post_id=rid).order_by('-published')
#                 send_comments=[]
#                 #counter=5
#                 for comment in post_comments:
#                     #if counter==0:
#                         #break
#                     #TODO:
#                     #add the url back once we get that, also our host
#                     comment_data={
#                         "author": {
#                             "id": str(comment.author.id),
#                             #"url": comment.author.url,
#                             "host": comment.author.host,
#                             "displayName": comment.author.display_name,
#                             "github": comment.author.github
#                         },
#                         "comment": comment.comment,
#                         "contentType": comment.content_type,
#                         "published": str(comment.published),
#                         "id": str(comment.id)
#                     }
#                     send_comments.append(comment_data)
#                     #counter=counter-1


#                 #TODO:
#                 #when users get an url, add url here
#                 response = {
#                     "title": desired_post.title,
#                     "source": desired_post.source,
#                     "origin": desired_post.origin,
#                     "description": desired_post.description,
#                     "contentType":"text/plain",
#                     "author":{
#                         "id": str(post_author.id),
#                         "host":post_author.host,
#                         "displayName":post_author.display_name,
#                         #"url":,
#                         "github":post_author.github
#                     },
#                     "count":post_comments.count(),
#                     "size":5,
#                     #"next":"",
#                     "comments":send_comments,
#                     "published":str(desired_post.published),
#                     "id":str(desired_post.id),
#                     "visibility":desired_post.visibility,
#                     #"visibleTo":desired_post.visibleTo,
#                     "unlisted":desired_post.unlisted,
#                 }
#                 return HttpResponse(json.dumps(response),content_type="application/json")

#             else:
#                 return HttpResponse(status=404)

#         else:
#             # browser
#             # leaving space for visibility checks
#             if True:
#                 post = get_object_or_404(Post, id=rid)
#                 postcomments = Comment.objects.filter(post_id=rid).order_by('-published')
#                 return render(request, "postview.html", {'post': post, 'post_comments': postcomments})


# def create_comment(request):
#     if request.method == "POST":
#         select_post = get_object_or_404(Post, id=request.POST['post'])
#         new_comment = Comment(
#             post=select_post,
#             comment=request.POST['comment'],
#             author=request.user
#         )
#         new_comment.save()
#     return HttpResponseRedirect(select_post.source)


# def delete_comment(request):
#     if request.method == "DELETE":
#         post_id = request.META['HTTP_POSTID']
#         to_be_deleted = get_object_or_404(Post, id=post_id)
#         post_author = get_object_or_404(User, id=to_be_deleted.author.id)
#         if post_author.id == request.user.id:
#             to_be_deleted.delete()
#             return HttpResponse('')

#     return HttpResponseNotFound("hello")

# def visible_to_user(request):
#     pass