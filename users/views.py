from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser, FormParser
from users.models import User
from users.serializer import UserSerializer

class BasicUserView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        """
        Create a new User.
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Set password securely after user creation
            user.set_password(request.data.get('password'))
            user.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request, *args, **kwargs):
        """
        Retrieve an user by ID.
        """
        user_id = kwargs.get('id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound(detail="user not found")
        
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """
        Update an user by ID.
        """
        if not request.user.is_authenticated:
            return Response({'error': 'You must be authenticated'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = kwargs.get('id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound(detail="user not found")
        
        if request.user.id != user.id:
            return Response({'error': 'You do not have permission to edit this profile'}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        Delete a user by ID.
        """
        if not request.user.is_authenticated:
            return Response({'error': 'You do not have permission to edit this profile'}, status=status.HTTP_403_FORBIDDEN)
        
        
        user_id = kwargs.get('id')
        try:
            user = User.objects.get(id=user_id)
            if request.user.id != user.id:
                return Response({'error': 'You do not have permission to delete this profile'}, status=status.HTTP_403_FORBIDDEN)
            user.delete()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            raise NotFound(detail="User not found")
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Follow a user"""
        id = kwargs.get('id')

        try:
            user_to_follow = User.objects.get(id=id)
        except User.DoesNotExist:
            raise NotFound
        
        user_to_follow.followers.add(request.user)
        return Response({'message': 'User followed successfully'}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """ Unfollow a user """
        id = kwargs.get('id')

        try:
            user_to_unfollow = User.objects.get(id=id)
        except User.DoesNotExist:
            raise NotFound
        
        user_to_unfollow.followers.remove(request.user)
        return Response({'message': 'User unfollowed successfully'}, status=status.HTTP_204_NO_CONTENT)


class BlockView(APIView):
    def post(self, request, *args, **kwargs):
        """ Block a user """
        id = kwargs.get('id')

        try:
            user_to_block = User.objects.get(id=id)
        except User.DoesNotExist:
            raise NotFound
        
        request.user.blocked_users.add(user_to_block)
        return Response({'message': 'User blocked successfully'}, status=status.HTTP_200_OK)
    
    def delete(self, request, *args,**kwargs):
        """ Unblock a user """
        id = kwargs.get('id')

        try:
            user_to_unblock = User.objects.get(id=id)
        except User.DoesNotExist:
            raise NotFound
        
        request.user.blocked_users.remove(user_to_unblock)
        return Response({'message': 'User unblocked successfully'}, status=status.HTTP_204_NO_CONTENT)
