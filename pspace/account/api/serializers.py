from django.contrib.auth.models import User, Group
from rest_framework import serializers, exceptions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=20, min_length=6)
    password = serializers.CharField(max_length=20, min_length=6)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate(self, data):
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                "message": "This username has been occupied."
            })
        if User.objects.filter(username=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                "message": "This email address has been occupied."
            })
        return data

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()