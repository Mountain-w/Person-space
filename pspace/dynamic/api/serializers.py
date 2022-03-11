from account.api.serializers import UserSerializer
from rest_framework import serializers
from dynamic.models import Dynamic
from comments.api.serializers import CommentSerializer


class DynamicSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Dynamic
        fields = ('id', 'user', 'created_at', 'content')


class DynamicCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)

    class Meta:
        model = Dynamic
        fields = ("content",)

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        dynamic = Dynamic.objects.create(user=user, content=content)
        return dynamic

class DynamicWithComment(serializers.ModelSerializer):
    user = UserSerializer()
    comments = CommentSerializer(source='comment_set', many=True)

    class Meta:
        model = Dynamic
        fields = ('id', 'user', 'content',  'comments', 'created_at')