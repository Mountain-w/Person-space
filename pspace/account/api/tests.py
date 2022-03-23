from testing.testcases import TestCase
from rest_framework.test import APIClient

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'


class AccountApiTests(TestCase):
    def setUp(self):
        self.user = self.create_user(
            username='admin',
            email='admin@qq.com',
            password='correct password'
        )

    def test_login(self):
        client = APIClient()
        # 每个函数必须以 test_ 开头，才会被自动调用进行测试
        # 1.测试登录是 post 方法
        response = client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # 用 get 方法应该返回的状态码为 405
        self.assertEqual(response.status_code, 405)

        # 2.用 post 方法但是密码错误
        response = client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)
        # 因为密码错误所以没有登录
        response = client.get(LOGIN_STATUS_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.data['has_logged_in'], False)
        # 正确的密码
        response = client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': "correct password",
        })
        self.assertEqual(response.status_code, 200)
        client.credentials(HTTP_AUTHORIZATION=response.data['token'])
        response = client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'admin@qq.com')

    def test_logout(self):
        client = APIClient()
        # 先登录
        response = client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # 验证用户已经登录
        client.credentials(HTTP_AUTHORIZATION=response.data['token'])
        response = client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # 测试必须用 post
        response = client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # 改用 post 成功 logout
        response = client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)
        # 验证用户已经登出
        client.credentials()
        response = client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        client = APIClient()
        data = {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        }
        # 测试 get 请求失败
        response = client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # 测试错误的邮箱
        response = client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password'
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # 测试密码太短
        response = client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': '123',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # 测试用户名太长
        response = client.post(SIGNUP_URL, {
            'username': 'username is tooooooooooooooooo loooooooong',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # 成功注册
        response = client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')
        # 验证用户已经登入
        client.credentials(HTTP_AUTHORIZATION=response.data['token'])
        response = client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)
