from django.db import models
from users.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

def validate_file_size(value):
    file_size = value.size  # File size in bytes
    max_size = 10 * 1024 * 1024  # 10MB (in bytes)
    if file_size > max_size:
        raise ValidationError(_('File size should not exceed 10MB.'))

def validate_file_type(value):
    # Check file extension (basic, but works well for common formats)
    ext = value.name.split('.')[-1].lower()
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'avi']

    if ext not in allowed_extensions:
        raise ValidationError(_('Unsupported file type. Only images and videos are allowed.'))

# Create your models here.
class Post(models.Model):
    content = models.TextField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    post_date = models.DateTimeField(auto_now_add=True)
    likers = models.ManyToManyField(User, related_name="post_likes", blank=True)
    edited = models.BooleanField(default=False)

    def __str__(self):
        return f"Post {self.id}"
    

class PostFile(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(
        upload_to='posts_files',
        null=True,
        blank=True,
        validators=[validate_file_size, validate_file_type]
    )

    def __str__(self):
        return f"File for post {self.post.id}"


class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    likers = models.ManyToManyField(User, related_name="comment_likes", blank=True)
    comment_date = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment {self.id}"

class Reply(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="replies")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="replies")
    likers = models.ManyToManyField(User, related_name="reply_likes", blank=True)
    reply_date = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)

    def __str__(self):
        return f"Reply {self.id}"


