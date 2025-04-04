from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.parsers import MultiPartParser, FormParser
from .models import *
from .serializer import *

# All the get methods are handled with the GraphQL endpoint
class BaseView(APIView):
    permission_classes = [IsAuthenticated]
    Serializer = None
    Model = None

    def post(self, request, *args, **kwargs):
        serializer = self.Serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        try:
            id = kwargs.get('id')
            obj = self.Model.objects.get(id=id)
        except self.Model.DoesNotExist:
            raise NotFound()
        except KeyError:
            raise ParseError()
        
        serializer = self.Serializer(obj, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        try:
            id = kwargs.get('id')
            obj = self.Model.objects.get(id=id)

            if obj.author != request.user:
                raise PermissionDenied(f"You cannot delete other users' {self.Model.__name__}")
            
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except self.Model.DoesNotExist:
            raise NotFound()
        except KeyError:
            raise ParseError()
        

class PostView(BaseView):
    Model = Post
    Serializer = PostSerializer


class CommentView(BaseView):
    Model = Comment
    Serializer = CommentSerializer

class ReplyView(BaseView):
    Model = Reply
    Serializer = ReplySerializer

class LikeView(APIView):
    permission_classes = [IsAuthenticated]
    Model = None

    def post(self, request, *args, **kwargs):
        try:
            id = kwargs.get('id')
            obj = self.Model.objects.get(id=id)

            obj.likers.add(request.user)

            return Response({"message": f"{self.Model.__name__} liked!"}, status=status.HTTP_201_CREATED)
        except self.Model.DoesNotExist:
            raise NotFound()
        except KeyError:
            raise ParseError()
        
    def delete(self, request, *args, **kwargs):
        try:
            id = kwargs.get('id')
            obj = self.Model.objects.get(id=id)

            obj.likers.remove(request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except self.Model.DoesNotExist:
            raise NotFound()
        except KeyError:
            raise ParseError()
        
class PostLikeView(LikeView):
    Model = Post

class CommentLikeView(LikeView):
    Model = Comment

class ReplyLikeView(LikeView):
    Model = Reply