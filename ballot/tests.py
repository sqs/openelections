from openelections.tests import OETestCase
from openelections.issues.models import Electorate, Issue

def issue(slug):
    return Issue.objects.get(slug=slug).get_typed()

class UndergradBallotDisplayTest(OETestCase):
    def test_has_undergrad_senators(self):
        res = self.client.get('/ballot/')
        self.assertContains(res, 'Leland Q. Senator')
        
class UndergradVoteTest(OETestCase):
    def test_vote_for_senators(self):
        tsowell = issue('thomas-sowell')
        tsowell_id = str(tsowell.pk)
        res = self.client.post('/ballot/vote', {'candidates_us': [tsowell_id]})
        self.assertTrue(False)