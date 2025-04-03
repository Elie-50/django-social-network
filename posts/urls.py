from django.urls import path
from .views import *

urlpatterns = [
    path('', PostView.as_view(), name='post-details'),
    path('<int:id>', PostView.as_view(), name='post-details'),
    path('comment/<int:id>', CommentView.as_view(), name='comment-details'),
    path('comment/', CommentView.as_view(), name='comment-details'),
    path('reply/<int:id>', ReplyView.as_view(), name='reply-details'),
    path('reply/', ReplyView.as_view(), name='reply-details'),
]
