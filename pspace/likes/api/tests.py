from testing.testcases import TestCase


LIKE_BASE_URL = '/api/likes/'
LIKE_CANCEL_URL = '/api/likes/cancel/'
COMMENT_LIST_API = '/api/comments/'
DYNAMIC_LIST_API = '/api/dynamics/'
DYNAMIC_DETAIL_API = '/api/dynamics/{}/'
NEWSFEED_LIST_API = '/api/newsfeeds/'

class LikeApiTest(TestCase):
    def setUp(self):
        self.ruize, self.ruize_client = self.create_user_and_client('ruize')
        self.dynamic = self.create_dynamic(self.ruize)
        self.laopo, self.laopo_client = self.create_user_and_client('laopo')
        self.comment = self.create_comment(self.laopo, self.dynamic)

    def test_dynamic_likes(self):
        data = {
            'content_type': 'dynamic',
            'object_id': self.dynamic.id
        }
        # 测试未登录用户不能点赞
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        # 测试get方法无效
        response = self.ruize_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # 成功点赞
        response = self.ruize_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.dynamic.like_set.count(), 1)

        # 重复点赞静默处理
        response = self.ruize_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.dynamic.like_set.count(), 1)
        # 不重复点赞，点赞数加 1
        response = self.laopo_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.dynamic.like_set.count(), 2)

    def test_comment_likes(self):
        data = {
            'content_type': 'comment',
            'object_id': self.comment.id
        }
        # 测试未登录用户不能点赞
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 403)

        # 测试get方法无效
        response = self.ruize_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 405)

        # 成功点赞
        response = self.ruize_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.comment.like_set.count(), 1)

        # 重复点赞静默处理
        response = self.ruize_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.comment.like_set.count(), 1)
        # 不重复点赞，点赞数加 1
        response = self.laopo_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.comment.like_set.count(), 2)

    def test_cancel(self):
        dynamic = self.create_dynamic(self.ruize)
        comment = self.create_comment(self.laopo, dynamic)
        like_comment_data = {'content_type': 'comment', 'object_id':comment.id}
        like_dynamic_data = {'content_type':'dynamic', 'object_id':dynamic.id}
        self.ruize_client.post(LIKE_BASE_URL, like_dynamic_data)
        self.laopo_client.post(LIKE_BASE_URL, like_comment_data)
        # 需要登录
        response = self.anonymous_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 403)
        # get 方法无效
        response = self.laopo_client.get(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 405)
        # 错误的参数
        response = self.laopo_client.post(LIKE_CANCEL_URL, {
            'content_type': 'wrong',
            'object_id':1
        })
        self.assertEqual(response.status_code, 400)
        response = self.laopo_client.post(LIKE_CANCEL_URL, {
            'content_type': 'comment',
            'object_id': -1
        })
        self.assertEqual(response.status_code, 400)
        # 没有点赞
        response = self.laopo_client.post(LIKE_CANCEL_URL, like_dynamic_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dynamic.like_set.count(), 1)
        self.assertEqual(comment.like_set.count(), 1)
        # 成功取消点赞
        response = self.laopo_client.post(LIKE_CANCEL_URL, like_comment_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.like_set.count(), 0)
        response = self.ruize_client.post(LIKE_CANCEL_URL, like_dynamic_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dynamic.like_set.count(), 0)

    def test_likes_in_comments_api(self):
        dynamic = self.create_dynamic(self.ruize)
        comment = self.create_comment(self.laopo, dynamic)

        response = self.anonymous_client.get(COMMENT_LIST_API, {
            'dynamic_id': dynamic.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)

        response = self.laopo_client.get(COMMENT_LIST_API, {
            'dynamic_id': dynamic.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], False)
        self.assertEqual(response.data['comments'][0]['likes_count'], 0)
        self.create_like(self.laopo, comment)
        response = self.laopo_client.get(COMMENT_LIST_API, {
            'dynamic_id': dynamic.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 1)
        self.create_like(self.ruize, comment)
        response = self.ruize_client.get(COMMENT_LIST_API, {
            'dynamic_id': dynamic.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['comments'][0]['has_liked'], True)
        self.assertEqual(response.data['comments'][0]['likes_count'], 2)

    def test_likes_in_dynamics_api(self):
        dynamic = self.create_dynamic(self.ruize)

        url = DYNAMIC_DETAIL_API.format(dynamic.id)
        response = self.laopo_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_liked'], False)
        self.assertEqual(response.data['likes_count'], 0)
        self.create_like(self.laopo, dynamic)
        response = self.laopo_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['has_liked'], True)
        self.assertEqual(response.data['likes_count'], 1)

        response = self.laopo_client.get(DYNAMIC_LIST_API, {
            'user_id' : self.ruize.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['Dynamics'][0]['has_liked'], True)
        self.assertEqual(response.data['Dynamics'][0]['likes_count'], 1)

        self.create_like(self.ruize, dynamic)
        self.create_newsfeed(self.laopo, dynamic)
        response = self.laopo_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['newsfeeds'][0]['dynamic']['has_liked'], True)
        self.assertEqual(response.data['newsfeeds'][0]['dynamic']['likes_count'], 2)

        url = DYNAMIC_DETAIL_API.format(dynamic.id)
        response = self.laopo_client.get(url)
        self.assertEqual(len(response.data['likes']), 2)
        self.assertEqual(response.data['likes'][0]['user']['id'], self.ruize.id)
        self.assertEqual(response.data['likes'][1]['user']['id'], self.laopo.id)