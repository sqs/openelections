#from selenium import selenium
#import unittest
from openelections.tests import OETestCase
from openelections.ballot.models import Ballot
from openelections.issues.models import Electorate, Issue

# class OESeleniumTestCase(unittest.TestCase):
#     def setUp(self):
#         self.verificationErrors = []
#         self.selenium = selenium("localhost", 32146, "*firefox", "http://corn16.stanford.edu:32145/")
#         self.selenium.start()
#         
#     def tearDown(self):
#         self.selenium.stop()
#         self.assertEqual([], self.verificationErrors)

def issue(slug):
    return Issue.objects.get(slug=slug)

def votes(voter_id, kind):
    return None
    #return Vote.objects.filter(voter_id=voter_id, issue__kind=kind).order_by('pk').all()

class UndergradBallotDisplayTest(OETestCase):
    def test_has_undergrad_senators(self):
        self.webauthLogin('xyz')
        res = self.client.get('/ballot/')
        self.assertContains(res, 'Leland Q. Senator')
        
    def test_has_class_pres(self):
        self.webauthLogin('xyz')
        res = self.client.get('/ballot/')
        self.assertContains(res, 'Super Sophomores')
        
    def test_has_exec(self):
        self.webauthLogin('xyz')
        res = self.client.get('/ballot/')
        self.assertContains(res, 'Obama/Biden')
        self.assertContains(res, 'Clinton/Bloomberg')
        self.assertContains(res, 'McCain/Palin')    

   
class UndergradVoteTest(OETestCase):
    def test_vote_for_senators(self):
        self.webauthLogin('xyz')
        tsowell = issue('thomas-sowell')
        tsowell_id = str(tsowell.pk)
        res = self.client.post('/ballot/vote', {'votes_us': [tsowell_id]})
        v = votes('xyz', 'US')
        self.assertTrue(len(v) == 1)
        self.assertTrue(v[0].issue == tsowell)
    
    def test_ranked_vote_for_exec(self):
        self.webauthLogin('xyz')
        obama = issue('obama-biden')
        mccain = issue('mccain-palin')
        clinton = issue('clinton-bloomberg')
        res = self.client.post('/ballot/vote', {'votes_exec': (obama.pk, clinton.pk, mccain.pk)})
        v = votes('xyz', 'Exec')
        self.assertTrue(len(v) == 3)
        issues = (v[0].issue, v[1].issue, v[2].issue)
        self.assertTrue(obama in issues)
        self.assertTrue(mccain in issues)
        self.assertTrue(clinton in issues)
        
# class BallotTest(OESeleniumTestCase):
#     def testLoad(self):
#         sel = self.selenium
#         sel.open('/ballot/')