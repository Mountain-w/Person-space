from testing.testcases import TestCase
from rest_framework.test import APIClient
from django.utils import timezone
from comments.models import Comment

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

    def test_destroy(self):
        comment = self.create_comment(self.ruize, self.dynamic)
        url = f"{COMMENT_URL}{comment.id}/"
        # 匿名不可删除
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)
        # 非本人不能删除
        response = self.laopo_client.delete(url)
        self.assertEqual(response.status_code, 403)
        # 本人可以删除
        count = Comment.objects.count()
        response = self.ruize_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count-1, Comment.objects.count())

    def test_update(self):
        comment = self.create_comment(self.ruize, self.dynamic)
        another_dynamic = self.create_dynamic(self.laopo)
        url = f"{COMMENT_URL}{comment.id}/"
        # 使用 put 的情况下
        # 匿名不可以更新
        response = self.anonymous_client.put(url, {'content': 'new'})
        self.assertEqual(response.status_code, 403)
        # 非本人不可更新
        response = self.laopo_client.put(url, {'content':'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')
        # 不能更新conten以外的东西
        before_updated = comment.updated_at
        before_created = comment.created_at
        now = timezone.now()
        response = self.ruize_client.put(url, {
            'content':'new',
            'user_id':self.laopo.id,
            'dynamic_id':another_dynamic.id,
            'created_at': now,
        })
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.ruize)
        self.assertEqual(comment.dynamic, self.dynamic)
        self.assertEqual(comment.created_at, before_created)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_updated)