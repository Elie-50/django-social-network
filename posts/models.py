from django.db import models
from users.models import User

# Create your models here.
class Post(models.Model):
    content = models.TextField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    post_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    likers = models.ManyToManyField(User, related_name="likes", blank=True)
    edited = models.BooleanField(default=False)
    
class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    comment_date = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)

class Reply(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="replies")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="replies")
    reply_date = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)


