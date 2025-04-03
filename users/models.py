from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

phone_number_validator = RegexValidator(regex=r'^\+?1?\d{9,20}$', message="Phone number must be entered in the format: '+ 999999999'. Up to 20 digits allowed.")
# Create your models here.
class User(AbstractUser):
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        validators=[phone_number_validator]
    )

    bio = models.TextField(null=True, blank=True)
    followers = models.ManyToManyField("User", related_name='following', blank=True)
    blocked_users = models.ManyToManyField("User", related_name='blocking', blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    private_account = models.BooleanField(default=False)

    def __str__(self):
        return self.username