from django.contrib.auth.models import User
# from testing.testcases import TestCase
# from django.test import TestCase
from testing.testcases import TestCase
from dynamic.models import Dynamic
from datetime import timedelta
from utils.time_helpers import utc_now


class DynamicTest(TestCase):
    def setUp(self):
        self.ruize = self.create_user('ruize')
        self.dynamic = self.create_dynamic(self.ruize)

    def test_hours_to_now(self):
        self.dynamic.created_at = utc_now() - timedelta(hours=10)
        self.assertEqual(self.dynamic.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.ruize, self.dynamic)
        self.assertEqual(self.dynamic.like_set.count(), 1)
        self.create_like(self.ruize, self.dynamic)
        self.assertEqual(self.dynamic.like_set.count(), 1)

        laopo = self.create_user('laopo')
        self.create_like(laopo, self.dynamic)
        self.assertEqual(self.dynamic.like_set.count(), 2)