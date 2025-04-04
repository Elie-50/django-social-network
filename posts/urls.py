from django.urls import path
from .views import *

urlpatterns = [
    path('', PostView.as_view(), name='post-details'),
    path('<int:id>/', PostView.as_view(), name='post-details'),
    path('comment/<int:id>/', CommentView.as_view(), name='comment-details'),
    path('comment/', CommentView.as_view(), name='comment-details'),
    path('reply/<int:id>/', ReplyView.as_view(), name='reply-details'),
    path('reply/', ReplyView.as_view(), name='reply-details'),
    path('like/<int:id>/', PostLikeView.as_view(), name='post-like'),
    path('comment/like/<int:id>/', CommentLikeView.as_view(), name='comment-like'),
    path('reply/like/<int:id>/', ReplyLikeView.as_view(), name='reply-like'),
    path('file/<int:id>/', PostFileView.as_view(), name='post-file'),
    path('file/', PostFileView.as_view(), name='post-file')
]
