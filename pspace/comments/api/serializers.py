from rest_framework import serializers
from comments.models import Comment
from account.api.serializers import UserSerializer
from rest_framework.exceptions import ValidationError
from dynamic.models import Dynamic


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        fields = ('id', 'dynamic_id', 'user', 'content', 'created_at')

class CommentSerializerForCreate(serializers.ModelSerializer):
    dynamic_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    content = serializers.CharField(max_length=140)

    class Meta:
        model = Comment
        fields = ('content', 'dynamic_id', 'user_id')

    def validate(self, data):
        dynamic_id = data['dynamic_id']
        if not Dynamic.objects.filter(id=dynamic_id).exists():
            raise ValidationError({'message':'dynamic does not exists'})
        return data

    def create(self, validated_data):
        return Comment.objects.create(
            user_id=validated_data['user_id'],
            dynamic_id=validated_data['dynamic_id'],
            content=validated_data['content']
        )

class CommentSerializerForUpdate(serializers.ModelSerializer):
    content = serializers.CharField(max_length=140)
    class Meta:
        model = Comment
        fields = ('content',)
    def update(self, instance, validated_data):
        instance.content = validated_data['content']
        instance.save()
        return instance