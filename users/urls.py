from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', BasicUserView.as_view(), name='user-details'),
    path('<int:id>/', BasicUserView.as_view(), name='user-details'),
    path('follow/<int:id>', FollowUserView.as_view(), name='follow'),
    path('block/<int:id>', BlockView.as_view(), name='block')
]
