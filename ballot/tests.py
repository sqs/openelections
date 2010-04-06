import unittest
from openelections.tests import OETestCase
from openelections.ballot.models import Ballot
from openelections.issues.models import Electorate, Issue
from test_utils.utils import twill_runner as twill
from openelections.webauth.stanford_webauth import make_secret_hash

class OEBallotTestCase(OETestCase):
    def webauthLoginAndMakeBallot(self, sunetid, electorates):
        self.webauthLogin(sunetid)
        make_ballot(sunetid, electorates)

class OETwillTestCase(OEBallotTestCase):
    def webauth_querystring(self, sunetid):
        return "webauth_sunetid=%s&hash=%s" % (sunetid, make_secret_hash(sunetid))
    
    def setUp(self):
        twill.setup()
        twill._testing_ = True
        super(OETwillTestCase, self).setUp()
        
    def tearDown(self):
        twill.teardown()
        super(OETwillTestCase, self).tearDown()
    
    def assertContains(self, a, b):
        self.assertTrue(b in a, "%s does not contain %s" % (a, b))

def issue(slug):
    return Issue.objects.get(slug=slug).get_typed()

def make_ballot(sunetid, electorates):
    b, created = Ballot.get_or_create_by_sunetid(sunetid)
    b.electorates = electorates
    b.save()
    return b

def ballot(sunetid):
    b, created = Ballot.get_or_create_by_sunetid(sunetid)
    assert not created
    return b

class UndergradBallotDisplayTest(OEBallotTestCase):
    def test_has_undergrad_senators(self):
        self.webauthLoginAndMakeBallot('ugfrosh', 'assu,undergrad-2,undergrad')
        res = self.client.get('/ballot/')
        self.assertContains(res, 'Leland Q. Senator')
        
    def test_has_class_pres(self):
        self.webauthLoginAndMakeBallot('ugfrosh', 'assu,undergrad-2,undergrad')
        res = self.client.get('/ballot/')
        self.assertContains(res, 'Super Sophomores')
        
    def test_has_exec(self):
        self.webauthLoginAndMakeBallot('ugfrosh', 'assu,undergrad-2,undergrad')
        res = self.client.get('/ballot/')
        self.assertContains(res, 'Obama/Biden')
        self.assertContains(res, 'Clinton/Bloomberg')
        self.assertContains(res, 'McCain/Palin')    

   
class UndergradVoteTest(OEBallotTestCase):
    def test_vote_for_senators(self):
        self.webauthLoginAndMakeBallot('ugsenior', 'assu,undergrad-5plus,undergrad')
        tsowell = issue('thomas-sowell')
        res = self.client.post('/ballot/vote', dict(votes_senate=tsowell.pk))
        b = ballot('ugsenior')
        self.assertTrue(tsowell, b.votes_senate.all())
    
    def test_ranked_vote_for_exec(self):
        self.webauthLoginAndMakeBallot('ugsenior', 'assu,undergrad-5plus,undergrad')
        obama = issue('obama-biden')
        mccain = issue('mccain-palin')
        clinton = issue('clinton-bloomberg')
        res = self.client.post('/ballot/vote', dict(vote_exec1=obama.pk, vote_exec2=clinton.pk, vote_exec3=mccain.pk))
        b = ballot('ugsenior')
        self.assertEquals(obama, b.vote_exec1)
        self.assertEquals(clinton, b.vote_exec2)
        self.assertEquals(mccain, b.vote_exec3)
        
class BallotTest(OETwillTestCase):
    def testLoad(self):
        make_ballot('ugsenior', 'assu,undergrad-5plus,undergrad')
        twill.go('/ballot/?%s' % self.webauth_querystring('ugsenior'))
        twill.code(200)
        twill.find('Obama/Biden')
        twill.find('Clinton/Bloomberg')
        twill.find('McCain/Palin')
        twill.find('Leland Q. Senator')
