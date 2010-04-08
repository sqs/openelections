import unittest
from openelections.tests import OETestCase
from openelections.ballot.models import Ballot
from openelections.issues.models import Electorate, Issue
from test_utils.utils import twill_runner as twill
from openelections.webauth.stanford_webauth import make_secret_hash
from django.conf import settings

settings.DEBUG = True

def issue(slug):
    return Issue.objects.get(slug=slug).get_typed()

def elec(slug):
    if slug is None: return None
    return Electorate.objects.get(slug=slug)

ugfrosh = dict(undergrad_class_year='undergrad-2', assu_populations=['undergrad'])
ugsoph = dict(undergrad_class_year='undergrad-3', assu_populations=['undergrad'])
ugjunior = dict(undergrad_class_year='undergrad-4', assu_populations=['undergrad'])
ugsenior = dict(undergrad_class_year='undergrad-5plus', assu_populations=['undergrad'])

gsc_earthsci = dict(assu_populations=['graduate'], gsc_district='gsc-earthsci')
gsc_edu = dict(assu_populations=['graduate'], gsc_district='gsc-edu')
gsc_eng = dict(assu_populations=['graduate'], gsc_district='gsc-eng')
gsc_gsb = dict(assu_populations=['graduate'], gsc_district='gsc-gsb')
gsc_hs_hum = dict(assu_populations=['graduate'], gsc_district='gsc-hs-hum')
gsc_hs_natsci = dict(assu_populations=['graduate'], gsc_district='gsc-hs-natsci')
gsc_hs_socsci = dict(assu_populations=['graduate'], gsc_district='gsc-hs-socsci')
gsc_law = dict(assu_populations=['graduate'], gsc_district='gsc-law')
gsc_med = dict(assu_populations=['graduate'], gsc_district='gsc-med', smsa_class_year='smsa-2', smsa_population='smsa-preclinical')

smsa1pc = dict(assu_populations=['graduate'], gsc_district='gsc-med', smsa_class_year='smsa-2', smsa_population='smsa-preclinical')
smsa2pc = dict(assu_populations=['graduate'], gsc_district='gsc-med', smsa_class_year='smsa-3', smsa_population='smsa-preclinical')
smsa4c = dict(assu_populations=['graduate'], gsc_district='gsc-med', smsa_class_year='smsa-5plus', smsa_population='smsa-clinical')

def make_ballot(sunetid, assu_populations=None, undergrad_class_year=None, gsc_district=None, smsa_class_year=None, smsa_population=None):
    b, created = Ballot.get_or_create_by_sunetid(sunetid)
    
    b.assu_populations = map(elec, assu_populations)    
    b.undergrad_class_year = elec(undergrad_class_year)
    b.gsc_district = elec(gsc_district)
    b.smsa_class_year = elec(smsa_class_year)
    b.smsa_population = elec(smsa_population)
    
    b.save()
    return b

def ballot(sunetid):
    b, created = Ballot.get_or_create_by_sunetid(sunetid)
    assert not created
    return b

class OEBallotTestCase(OETestCase):
    fixtures = ['2010ballot.json']
    
    def webauthLoginAndMakeBallot(self, sunetid, ballotargs):
        self.webauthLogin(sunetid)
        make_ballot(sunetid, **ballotargs)

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

class BallotDisplayTest(OEBallotTestCase):
    def test_has_undergrad_senators(self):
        self.webauthLoginAndMakeBallot('ugfrosh', ugfrosh)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'Sastry')
        self.assertContains(res, 'Siegel')
        self.assertContains(res, 'Jang')
        self.assertContains(res, 'Walzebuck')
        self.assertContains(res, 'Saeid')
        
    def test_has_class_pres(self):
        self.webauthLoginAndMakeBallot('ugfrosh', ugfrosh)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'Sophs 4 More')
        self.assertContains(res, 'iThirteen')
        self.assertContains(res, 'Think Thirteen!')
        self.assertContains(res, 'So-phresh')
        
    def test_has_exec(self):
        self.webauthLoginAndMakeBallot('ugfrosh', ugfrosh)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'Thom and Stephanie')
        self.assertContains(res, 'Caddylack')
        self.assertContains(res, 'G-MRDA')
        self.assertContains(res, 'Peacock and Bakke')
        self.assertContains(res, 'The No-Rain Campaign')
        self.assertContains(res, 'Cardona and Wharton')
    
    def test_ugfrosh(self):
        self.webauthLoginAndMakeBallot('ugfrosh', ugfrosh)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'undergraduate freshman')
    
    def test_ugsoph(self):
        self.webauthLoginAndMakeBallot('ugsoph', ugsoph)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'undergraduate sophomore')
    
    def test_ugjunior(self):
        self.webauthLoginAndMakeBallot('ugjunior', ugjunior)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'undergraduate junior')
        
    def test_ugsenior(self):
        self.webauthLoginAndMakeBallot('ugsenior', ugsenior)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'undergraduate senior')

    # GSC
    def test_gsc_earthsci(self):
        self.webauthLoginAndMakeBallot('gsc_earthsci', gsc_earthsci)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'grad student in the School of Earth Sciences')
        
    def test_gsc_edu(self):
        self.webauthLoginAndMakeBallot('gsc_edu', gsc_edu)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'grad student in the School of Education')
    
    def test_gsc_eng(self):
        self.webauthLoginAndMakeBallot('gsc_eng', gsc_eng)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'grad student in the School of Engineering')    
    
    def test_gsc_gsb(self):
        self.webauthLoginAndMakeBallot('gsc_gsb', gsc_gsb)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'grad student in the GSB')
        
    def test_gsc_hs_hum(self):
        self.webauthLoginAndMakeBallot('gsc_hs_hum', gsc_hs_hum)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'grad student in the School of Humanities and Sciences, Humanities')
        
    def test_gsc_hs_natsci(self):
        self.webauthLoginAndMakeBallot('gsc_hs_natsci', gsc_hs_natsci)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'grad student in the School of Humanities and Sciences, Natural Sciences')
        
    def test_gsc_hs_socsci(self):
        self.webauthLoginAndMakeBallot('gsc_hs_socsci', gsc_hs_socsci)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'grad student in the School of Humanities and Sciences, Social Sciences')
        
    def test_gsc_law(self):
        self.webauthLoginAndMakeBallot('gsc_law', gsc_law)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'grad student in the School of Law')
        
    def test_gsc_med(self):
        self.webauthLoginAndMakeBallot('gsc_med', gsc_med)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'med student in the School of Medicine')
    
    def test_smsa1pc(self):
        self.webauthLoginAndMakeBallot('smsa1pc', smsa1pc)
        res = self.client.get('/ballot/')
        self.assertContains(res, '1st year, Pre-clinical med student in the School of Medicine')
        
    def test_smsa2pc(self):
        self.webauthLoginAndMakeBallot('smsa2pc', smsa2pc)
        res = self.client.get('/ballot/')
        self.assertContains(res, '2nd year, Pre-clinical med student in the School of Medicine')
        
    def test_smsa4c(self):
        self.webauthLoginAndMakeBallot('smsa4c', smsa4c)
        res = self.client.get('/ballot/')
        self.assertContains(res, '4th year and above, Clinical med student in the School of Medicine')
        


class BallotChoiceTest(OEBallotTestCase):
    def test_ug_no_class_year(self):
        self.webauthLoginAndMakeBallot('abc1', dict(assu_populations=['undergrad']))
        res = self.client.get('/ballot/')
        self.assertRedirects(res, '/ballot/choose')

    def test_ug_ok(self):
        self.webauthLoginAndMakeBallot('xyz1', dict(assu_populations=['undergrad'], undergrad_class_year='undergrad-2'))
        res = self.client.get('/ballot/')
        self.assertTemplateUsed(res, 'ballot/ballot.html')
    
    def test_gsc_no_district(self):
        self.webauthLoginAndMakeBallot('abc2', dict(assu_populations=['graduate']))
        res = self.client.get('/ballot/')
        self.assertRedirects(res, '/ballot/choose')
        
    def test_smsa_no_class_year(self):
        self.webauthLoginAndMakeBallot('abc3', dict(assu_populations=['graduate'], gsc_district='gsc-med', smsa_population='smsa-clinical'))
        res = self.client.get('/ballot/')
        self.assertRedirects(res, '/ballot/choose')
        
    def test_smsa_no_population(self):
        self.webauthLoginAndMakeBallot('abc4', dict(assu_populations=['graduate'], gsc_district='gsc-med', smsa_class_year='smsa-3'))
        res = self.client.get('/ballot/')
        self.assertRedirects(res, '/ballot/choose')
            
    def test_new_user(self):
        self.webauthLogin('newuser')
        res = self.client.get('/ballot/')
        self.assertRedirects(res, '/ballot/choose')

class RealSMSABallotTest(OEBallotTestCase):
    def test_shows_smsa_schoolwide_candidates(self):
        self.webauthLoginAndMakeBallot('smsa1pc', smsa1pc)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'Agnieszka')
        self.assertContains(res, 'Chloe')
        self.assertContains(res, 'Deepa')
        self.assertContains(res, 'Aria')
        self.assertContains(res, 'Carr')
        self.assertContains(res, 'Harris')
        self.assertContains(res, 'Luo')
        self.assertContains(res, 'Kerry')
        self.assertContains(res, 'Roxana')
        
    def test_shows_csac(self):
        self.webauthLoginAndMakeBallot('smsa1pc', smsa1pc)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'Eisenhut')
        self.assertContains(res, 'Harrysson')
        self.assertContains(res, 'Stein')

class BallotCandidatesChoiceTest(OEBallotTestCase):
    def test_only_15_senators(self):
        self.webauthLoginAndMakeBallot('ugfrosh', ugfrosh)
        votes_senate = [s.pk for s in Issue.objects.filter(kind='US').all()[:19]]
        res = self.client.post('/ballot/vote', {'votes_senate': votes_senate})
        self.assertTemplateUsed(res, 'ballot/ballot.html')
        self.assertContains(res, 'may only cast 15 votes for Senate')
        self.assertEquals(0, ballot('ugfrosh').votes_senate.count())
        
    def test_only_5_gsc_atlarge(self):
        self.webauthLoginAndMakeBallot('gsc_med', gsc_med)
        votes = [s.pk for s in Issue.objects.filter(kind='GSC').all()[:9]]
        res = self.client.post('/ballot/vote', {'votes_gsc_atlarge': votes})
        self.assertTemplateUsed(res, 'ballot/ballot.html')
        self.assertContains(res, 'may only cast 5 at-large votes for GSC')
        self.assertEquals(0, ballot('gsc_med').votes_gsc_atlarge.count())
        
    def test_only_1_gsc_district(self):
        self.webauthLoginAndMakeBallot('gsc_med', gsc_med)
        votes = [issue('krystal-st-julien').pk, issue('jessica-tsai').pk]
        res = self.client.post('/ballot/vote', {'votes_gsc_district': votes})
        self.assertTemplateUsed(res, 'ballot/ballot.html')
        self.assertContains(res, 'may only cast 1 vote(s) for GSC School of Medicine District')
        self.assertEquals(0, ballot('gsc_med').votes_gsc_district.count())
    
    def test_gsc_district_eng_2_votes_ok(self):
        self.webauthLoginAndMakeBallot('gsc_eng', gsc_eng)
        votes = [issue('y7ding').pk, issue('tao-chu').pk]
        res = self.client.post('/ballot/vote', {'votes_gsc_district': votes})
        self.assertTemplateUsed(res, 'ballot/done.html')
        self.assertEquals(2, ballot('gsc_eng').votes_gsc_district.count())
    
    def test_only_2_gsc_district_eng(self):
        self.webauthLoginAndMakeBallot('gsc_eng', gsc_eng)
        votes = [issue('y7ding').pk, issue('tao-chu').pk, issue('drew-kennedy').pk]
        res = self.client.post('/ballot/vote', {'votes_gsc_district': votes})
        self.assertTemplateUsed(res, 'ballot/ballot.html')
        self.assertContains(res, 'may only cast 2 vote(s) for GSC School of Engineering District')
        self.assertEquals(0, ballot('gsc_eng').votes_gsc_district.count())
      
class BallotTest(OETwillTestCase):
    def test_load(self):
        make_ballot('ugsenior', **ugsenior)
        twill.go('/ballot/?%s' % self.webauth_querystring('ugsenior'))
        twill.code(200)
        twill.find('Thom and Stephanie')
        twill.find('Caddylack')
        twill.find('G-MRDA')
        twill.find('Peacock and Bakke')
        twill.find('The No-Rain Campaign')
        twill.find('Cardona and Wharton')
        twill.find('Sastry')
        twill.find('Siegel')
        twill.find('Jang')
        twill.find('Walzebuck')
        twill.find('Saeid')
