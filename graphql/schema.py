import graphene
from graphene_django import DjangoObjectType
from users.models import User
from posts.models import Post, Comment, Reply

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'bio', 'first_name', 'last_name', 'private_profile', 'followers', 'blocked_users')

    following = graphene.List(lambda: UserType)

    def resolve_following(self, info):
        return self.following.all()

    posts = graphene.List(lambda: PostType)

    def resolve_posts(self, info):
        return self.posts.all()

    likes = graphene.List(lambda: PostType)

    def resolve_likes(self, info):
        return self.likes.all()

    profile_image_url = graphene.String()

    def resolve_profile_image_url(self, info):
        request = info.context
        if self.profile_picture:
            return request.build_absolute_uri(self.profile_picture.url)
        return None

class ReplyType(DjangoObjectType):
    class Meta:
        model = Reply
        fields = ('id', 'content', 'author', 'reply_date', 'comment')

class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ('id', 'content', 'author', 'comment_date', 'post')

    replies = graphene.List(ReplyType)

    def resolve_replies(self, info):
        return self.replies.all()

class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = ('id', 'content', 'author', 'post_date', 'image', 'likers')

    post_image = graphene.String()

    def resolve_post_image(self, info):
        request = info.context
        if self.image:
            return request.build_absolute_uri(self.image.url)
        return None
    
    comments = graphene.List(CommentType)

    def resolve_comments(self, info):
        return self.comments.all()

class Query(graphene.ObjectType):
    user_by_username = graphene.Field(UserType, name=graphene.String(required=True))
    post_by_id = graphene.Field(PostType, id=graphene.Int(required=True))
    users_search = graphene.List(UserType, name=graphene.String(required=True))

    def resolve_user_by_username(self, info, name):
        try:
            return User.objects.get(username=name)
        except User.DoesNotExist:
            return None

    def resolve_users_search(self, info, name):
        return User.objects.filter(username__icontains=name)

    def resolve_post_by_id(self, info, id):
        try:
            return Post.objects.get(id=id)
        except Post.DoesNotExist:
            return None

schema = graphene.Schema(query=Query)
