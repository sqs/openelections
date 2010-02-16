from openelections.tests import OETestCase
from openelections.issues.models import Electorate, Issue
from openelections.petitions.models import Signature


class VisitorTest(TestCase):
    fixtures = ['2009ballot.json']
    
    def test_index(self):
        res = self.client.get('/issues/zack-warma')
        self.failUnlessEqual(res.status_code, 200)