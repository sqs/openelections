from django.test import TestCase

class VisitorTest(TestCase):
    fixtures = ['2009ballot.json']
    
    def test_index(self):
        res = self.client.get('/issues/zack-warma')
        self.failUnlessEqual(res.status_code, 200)