from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):
    def setUp(self):
        self.anonymous_client = APIClient()
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

    def test_follow(self):
        url = FOLLOW_URL.format(self.ruize.id)

        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # 要用 get 来 follow
        response = self.laopo_client.get(url)
        self.assertEqual(response.status_code, 405)
        # 不可以 follow 自己
        response = self.ruize_client.post(url)
        self.assertEqual(response.status_code, 400)
        # follow 成功
        response = self.laopo_client.post(url)
        self.assertEqual(response.status_code, 201)
        # 重复 follow 静默成功
        response = self.laopo_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicate'], True)
        # 反向关注会创建新的数据
        count = Friendship.objects.count()
        response = self.ruize_client.post(FOLLOW_URL.format(self.laopo.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

        def test_unfollow(self):
            url = UNFOLLOW_URL.format(self.ruize.id)

            # 需要登录才能 unfollow 别人
            response = self.anonymous_client.post(url)
            self.assertEqual(response.status_code, 403)
            # 不能用 get 来 unfollow 别人
            response = self.laopo_client.get(url)
            self.assertEqual(response.status_code, 405)
            # 不能用 unfollow 自己
            response = self.ruize_client.post(url)
            self.assertEqual(response.status_code, 400)
            # unfollow 成功
            Friendship.objects.create(from_user=self.laopo, to_user=self.ruize)
            count = Friendship.objects.count()
            response = self.laopo_client.post(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['deleted'], 1)
            self.assertEqual(Friendship.objects.count(), count - 1)
            # 未 follow 的情况下 unfollow 静默处理
            count = Friendship.objects.count()
            response = self.laopo_client.post(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['deleted'], 0)
            self.assertEqual(Friendship.objects.count(), count)

        def test_followings(self):
            url = FOLLOWINGS_URL.format(self.laopo.id)
            # post is not allowed
            response = self.anonymous_client.post(url)
            self.assertEqual(response.status_code, 405)
            # get is ok
            response = self.anonymous_client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data['followings']), 3)
            # 确保按照时间倒序
            ts0 = response.data['followings'][0]['created_at']
            ts1 = response.data['followings'][1]['created_at']
            ts2 = response.data['followings'][2]['created_at']
            self.assertEqual(ts0 > ts1, True)
            self.assertEqual(ts1 > ts2, True)
            self.assertEqual(
                response.data['followings'][0]['user']['username'],
                'laopo_following2',
            )
            self.assertEqual(
                response.data['followings'][1]['user']['username'],
                'laopo_following1',
            )
            self.assertEqual(
                response.data['followings'][2]['user']['username'],
                'laopo_following0',
            )

        def test_followers(self):
            url = FOLLOWERS_URL.format(self.laopo.id)
            # post is not allowed
            response = self.anonymous_client.post(url)
            self.assertEqual(response.status_code, 405)
            # get is ok
            response = self.anonymous_client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.data['followers']), 2)
            # 确保按照时间倒序
            ts0 = response.data['followers'][0]['created_at']
            ts1 = response.data['followers'][1]['created_at']
            self.assertEqual(ts0 > ts1, True)
            self.assertEqual(
                response.data['followers'][0]['user']['username'],
                'laopo_follower1',
            )
            self.assertEqual(
                response.data['followers'][1]['user']['username'],
                'laopo_follower0',
            )

