from django.contrib.auth.models import User
# from testing.testcases import TestCase
from django.test import TestCase
from dynamic.models import Dynamic
from datetime import timedelta
from utils.time_helpers import utc_now


class DynamicTest(TestCase):
    def test_hours_to_now(self):
        ruize = User.objects.create_user(username='ruize')
        dynamic = Dynamic.objects.create(user=ruize, content="This is my first time")
        dynamic.created_at = utc_now() - timedelta(hours=10)
        dynamic.save()
        self.assertEqual(dynamic.hours_to_now, 10)