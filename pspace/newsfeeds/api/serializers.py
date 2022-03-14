from rest_framework import serializers
from newsfeeds.models import NewsFeed
from dynamic.api.serializers import DynamicSerializer


class NewsFeedSerializer(serializers.ModelSerializer):
    dynamic = DynamicSerializer()

    class Meta:
        model = NewsFeed
        fields = ('id', 'created_at', 'user', 'dynamic')