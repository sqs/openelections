from django.test import TestCase

class VisitorTest(TestCase):
    def test_index(self):
        res = self.client.get('/issues/1')
        self.failUnlessEqual(res.status_code, 200)