from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'bio', 'password', 'first_name', 'last_name', 'email', 'profile_picture', 'private_account', 'is_staff', 'is_active', 'phone_number']

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user