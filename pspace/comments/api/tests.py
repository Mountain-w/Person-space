from testing.testcases import TestCase
from rest_framework.test import APIClient



COMMENT_URL = '/api/comments/'


class CommentApiTests(TestCase):
    def setUp(self):
        self.ruize = self.create_user('ruize')
        self.ruize_client = APIClient()
        self.ruize_client.force_authenticate(self.ruize)
        self.laopo = self.create_user('laopo')
        self.laopo_client = APIClient()
        self.laopo_client.force_authenticate(self.laopo)
        self.dynamic = self.create_dynamic(self.ruize)

    def test_create(self):
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # 测试啥参数都不带
        response = self.ruize_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)
        # 没有评论不行
        response = self.ruize_client.post(COMMENT_URL, {'dynamic_id':self.dynamic.id})
        self.assertEqual(response.status_code, 400)
        # 没有动态不行
        response = self.ruize_client.post(COMMENT_URL, {'content':'1'})
        self.assertEqual(response.status_code, 400)
        # 评论太长不行
        response = self.ruize_client.post(
            COMMENT_URL,
            {'dynamic_id': self.dynamic.id,
             'content': '1'*145}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)
        # 正常创建
        response = self.ruize_client.post(
            COMMENT_URL,
            {
                'dynamic_id':self.dynamic.id,
                'content':'oh yeah',
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.ruize.id)
        self.assertEqual(response.data['dynamic_id'], self.dynamic.id)
        self.assertEqual(response.data['content'], 'oh yeah')