from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from dynamic.models import Dynamic


class TestCase(DjangoTestCase):
    def create_user(self, username, email, password=None):
        if password is None:
            password = 'generic password'
        # 不能写成 User.objects.create()
        # 因为 password 需要被加密, username 和 email 需要进行一些 normalize 处理
        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default tweet content'
        return Dynamic.objects.create(user=user, content=content)