from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from dynamic.models import Dynamic
from comments.models import Comment
from newsfeeds.models import NewsFeed
from likes.models import Like
from django.contrib.contenttypes.models import ContentType
from utils.auth.authhelper import generate_token


class TestCase(DjangoTestCase):
    @property
    def anonymous_client(self):
        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client

    def create_user(self, username, email=None, password=None):
        if email is None:
            email = f'{username}@qq.com'
        if password is None:
            password = 'generic password'
        # 不能写成 User.objects.create()
        # 因为 password 需要被加密, username 和 email 需要进行一些 normalize 处理
        return User.objects.create_user(username, email, password)

    def create_dynamic(self, user, content=None):
        if content is None:
            content = 'default dynamic content'
        return Dynamic.objects.create(user=user, content=content)

    def create_comment(self, user, dynamic, content=None):
        if not content:
            content = "very good"
        return Comment.objects.create(user=user, dynamic=dynamic, content=content)

    def create_like(self, user, target):
        instance, _ = Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
            user=user
        )
        return instance

    def create_user_and_client(self, *args, **kwargs):
        user = self.create_user(*args, **kwargs)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=generate_token(user.username))
        return user, client

    def create_newsfeed(self, user, dynamic):
        return NewsFeed.objects.create(
            user=user,
            dynamic=dynamic
        )
