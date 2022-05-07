from account.api.serializers import UserSerializer
from rest_framework import serializers
from dynamic.models import Dynamic
from comments.api.serializers import CommentSerializer
from likes.api.serializers import LikeSerializer
from likes.services import LikeService


class DynamicSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    photo_urls = serializers.SerializerMethodField()
    class Meta:
        model = Dynamic
        fields = ('id', 'user', 'created_at', 'content', 'comments_count', 'likes_count', 'has_liked', 'photo_urls')

    def get_comments_count(self, obj):
        return obj.comment_set.count()

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)

    def get_photo_urls(self, obj):
        photos = []
        for photo in obj.photo_set.all().order_by('created_at'):
            photos.append(photo.file.url)
        return photos

class DynamicCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)
    files = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=True,
        required=False
    )

    class Meta:
        model = Dynamic
        fields = ("content", 'files')
    

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        dynamic = Dynamic.objects.create(user=user, content=content)
        if validated_data.get('files'):
            from dynamic.services import DynamicService
            DynamicService.create_photos_from_files(dynamic, validated_data['files'])
        return dynamic


class DynamicSerializerForDetail(DynamicSerializer):
    comments = CommentSerializer(source='comment_set', many=True)
    likes = LikeSerializer(source='like_set', many=True)

    class Meta:
        model = Dynamic
        fields = ('id', 'user', 'content', 'comments', 'created_at', 'likes',
                  'likes_count',
                  'comments_count',
                  'has_liked',
                  'photo_urls')
