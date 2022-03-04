from account.api.serializers import UserSerializer
from rest_framework import serializers
from dynamic.models import Dynamic


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
