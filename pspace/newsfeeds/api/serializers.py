from rest_framework import serializers
from newsfeeds.models import NewsFeed
from dynamic.api.serialzers import DynamicSerializer


class NewsFeedSerializer(serializers.ModelSerializer):
    dynamic = DynamicSerializer()

    class Meta:
        model = NewsFeed
        fields = ('id', 'created_at', 'user', 'dynamic')