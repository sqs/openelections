from django.test import TestCase
from openelections.issues.models import Issue
from openelections.petitions.models import Signature


class VisitorTest(TestCase):
    fixtures = ['2009ballot.json']
    
    def test_index(self):
        res = self.client.get('/issues/zack-warma')
        self.failUnlessEqual(res.status_code, 200)