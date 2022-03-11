from rest_framework import serializers
from newsfeeds.models import NewsFeed
from dynamic.api.serializers import DynamicSerializer, DynamicWithComment


class NewsFeedSerializer(serializers.ModelSerializer):
    dynamic = DynamicWithComment()

    class Meta:
        model = NewsFeed
        fields = ('id', 'created_at', 'user', 'dynamic')