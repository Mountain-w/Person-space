from django.contrib.auth.models import User, Group
from rest_framework import serializers, exceptions
from friendships.services import FriendshipService
from account.models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserProfile
        fields = ('nickname', 'avatar', 'introduction')

class UserProfileForUpdate(serializers.ModelSerializer):
    nickname = serializers.CharField(max_length=100, min_length=2)
    avatar = serializers.FileField()
    introduction = serializers.CharField()

    class Meta:
        model = UserProfile
        fields = ("nickname", "avatar", "introduction")
    
    def update(self, instance, validated_data):
        instance.nickname = validated_data['nickname']
        instance.avatar = validated_data['avatar']
        instance.introduction = validated_data['introduction']
        instance.save()
        return instance

class UserSerializer(serializers.ModelSerializer):
    has_followed = serializers.SerializerMethodField()
    profile = UserProfileSerializer()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'has_followed', 'profile']
    
    def get_has_followed(self, obj):
        current_user = self.context['request'].user
        return FriendshipService.has_followed(current_user, obj)

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

