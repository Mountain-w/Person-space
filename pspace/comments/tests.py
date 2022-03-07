from testing.testcases import TestCase

# Create your tests here.
class CommentModelTests(TestCase):
    def test_comment(self):
        user = self.create_user('ruize')
        dynamic = self.create_dynamic(user)
        comment = self.create_comment(user, dynamic)
        self.assertNotEqual(comment.__str__(), None)