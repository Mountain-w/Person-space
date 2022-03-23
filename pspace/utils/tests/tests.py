import time
from unittest import TestCase
import base64
from utils.auth.authhelper import (
    checkout_token,
    generate_token,
    generate_token_for_test,
    get_user_for_test,
)
from utils.exceptions.exceptions import TokenInvalid, TokenOutDate


class UtilsTest(TestCase):
    def test_generate_checkout(self):
        self.username = 'ruize'
        token = generate_token(self.username, 1)
        # 检查正确 token
        checkout_token(token)
        username = get_user_for_test(token)
        self.assertEqual(username, self.username)
        # 错误 token
        token1 = token + 'xxx'
        try:
            checkout_token(token1)
        except TokenInvalid as e:
            print(e)
        # 超时 token
        token = generate_token_for_test(username, 9)
        try:
            checkout_token(token)
        except TokenOutDate as e:
            print(e)
