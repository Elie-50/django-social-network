from .models import *
from users.serializer import UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)  # To show author details, or you can use PrimaryKeyRelatedField if you need to accept the author ID in the input.
    likers = UserSerializer(many=True, read_only=True)  # List of users who liked the post

    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'post_date', 'image', 'likers', 'edited']

    # Override save method to handle foreign key relationship
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Ensure the logged-in user is the author before updating the post
        if instance.author != self.context['request'].user:
            raise PermissionDenied("You cannot edit other users' posts")

        # Proceed with the update if the author matches the logged-in user
        instance = super().update(instance, validated_data)
        return instance


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'post', 'comment_date', 'edited']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Ensure the logged-in user is the author before updating the post
        if instance.author != self.context['request'].user:
            raise PermissionDenied("You cannot edit other users' comments")

        # Proceed with the update if the author matches the logged-in user
        instance = super().update(instance, validated_data)
        return instance


class ReplySerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comment = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all())

    class Meta:
        model = Reply
        fields = ['id', 'content', 'author', 'comment', 'reply_date', 'edited']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Ensure the logged-in user is the author before updating the post
        if instance.author != self.context['request'].user:
            raise PermissionDenied("You cannot edit other users' replies")

        # Proceed with the update if the author matches the logged-in user
        instance = super().update(instance, validated_data)
        return instance