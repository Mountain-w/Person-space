from testing.testcases import TestCase

# Create your tests here.
class CommentModelTests(TestCase):
    def setUp(self):
        self.user = self.create_user('ruize')
        self.dynamic = self.create_dynamic(self.user)
        self.comment = self.create_comment(self.user, self.dynamic)

    def test_comment(self):
        self.assertNotEqual(self.comment.__str__(), None)

    def test_like_set(self):
        self.create_like(self.user, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        self.create_like(self.user, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        laopo = self.create_user('laopo')
        self.create_like(laopo, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)