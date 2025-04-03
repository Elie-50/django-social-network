from django.urls import path
from .views import *

urlpatterns = [
    path('', BasicUserView.as_view(), name='user-details'),
    path('<int:id>/', BasicUserView.as_view(), name='user-details'),
    path('follow/<int:id>', FollowUserView.as_view(), name='follow'),
    path('block/<int:id>', BlockView.as_view(), name='block')
]
