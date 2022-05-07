
from newsfeeds.models import NewsFeed
from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase


NEWSFEEDS_URL = '/api/newsfeeds/'
POST_DYNAMIC_URL = '/api/dynamics/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTest(TestCase):
    def setUp(self):
        self.ruize = self.create_user('ruize')
        self.ruize_client = APIClient()
        self.ruize_client.force_authenticate(self.ruize)

        self.laopo = self.create_user('laopo')
        self.laopo_client = APIClient()
        self.laopo_client.force_authenticate(self.laopo)

        for i in range(2):
            follower = self.create_user('laopo_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.laopo)
        for i in range(3):
            following = self.create_user('laopo_following{}'.format(i))
            Friendship.objects.create(from_user=self.laopo, to_user=following)

    def test_list(self):
        # 需要登录
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)
        # 不能用 post
        response = self.ruize_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)
        # 一开始啥都没
        response = self.ruize_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 0)
        # 自己发布的信息是能看到的
        self.ruize_client.post(POST_DYNAMIC_URL, {'content':"Hello world"})
        response = self.ruize_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 1)
        self.ruize_client.post(FOLLOW_URL.format(self.laopo.id))
        response = self.laopo_client.post(POST_DYNAMIC_URL, {'content':"Hello personalspace"})
        posted_dynamic_id = response.data['id']
        response = self.ruize_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['dynamic']['id'], posted_dynamic_id)