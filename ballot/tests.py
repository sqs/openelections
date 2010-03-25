from openelections.tests import OETestCase
from openelections.ballot.models import Vote
from openelections.issues.models import Electorate, Issue

def issue(slug):
    return Issue.objects.get(slug=slug)

def votes(voter_id, kind):
    return Vote.objects.filter(voter_id=voter_id, issue__kind=kind).all()

class UndergradBallotDisplayTest(OETestCase):
    def test_has_undergrad_senators(self):
        self.webauthLogin('xyz')
        res = self.client.get('/ballot/')
        self.assertContains(res, 'Leland Q. Senator')
        
class UndergradVoteTest(OETestCase):
    def test_vote_for_senators(self):
        self.webauthLogin('xyz')
        tsowell = issue('thomas-sowell')
        tsowell_id = str(tsowell.pk)
        res = self.client.post('/ballot/vote', {'votes_us': [tsowell_id]})
        v = votes('xyz', 'US')
        self.assertTrue(len(v) == 1)
        self.assertTrue(v[0].issue == tsowell)