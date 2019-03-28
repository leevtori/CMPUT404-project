from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.FeedView.as_view(), name='feed'),
    path('profile/<str:username>', views.ProfileView.as_view(), name='profile'),
    path('posts/<uuid:pk>', views.PostDetailView.as_view(), name='postdetail'),
    path('posts/create', views.create_post, name='createpost'),
    path('posts/delete/<uuid:pk>', views.delete_post, name='deletepost'),
    path('comment', views.add_comment, name='comment'),
    # path('newComment/', views.create_comment, name='new_comment'),
    # path('posts/delete/', views.delete_comment, name='delete-post'),
    # path('author/posts/', views.visible_to_user, name='visiable-to-user')
]