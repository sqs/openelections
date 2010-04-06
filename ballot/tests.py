import unittest
from openelections.tests import OETestCase
from openelections.ballot.models import Ballot
from openelections.issues.models import Electorate, Issue
from test_utils.utils import twill_runner as twill
from openelections.webauth.stanford_webauth import make_secret_hash

def issue(slug):
    return Issue.objects.get(slug=slug).get_typed()

def elec(slug):
    if slug is None: return None
    return Electorate.objects.get(slug=slug)

ugfrosh = dict(undergrad_class_year='undergrad-1', assu_populations=['undergrad'])
ugsoph = dict(undergrad_class_year='undergrad-2', assu_populations=['undergrad'])
ugjunior = dict(undergrad_class_year='undergrad-3', assu_populations=['undergrad'])
ugsenior = dict(undergrad_class_year='undergrad-4', assu_populations=['undergrad'])
ugfifth = dict(undergrad_class_year='undergrad-5plus', assu_populations=['undergrad'])
smsa1 = dict(assu_populations=['graduate'], gsc_district='gsc-med', smsa_class_year='smsa-1', smsa_population='smsa-preclinical')

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

class UndergradBallotDisplayTest(OEBallotTestCase):
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
        
    def test_ugfifth(self):
        self.webauthLoginAndMakeBallot('ugfifth', ugfifth)
        res = self.client.get('/ballot/')
        self.assertContains(res, 'undergraduate fifth year and above')
        
class BallotTest(OETwillTestCase):
    def testLoad(self):
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

class BallotChoiceTest(OEBallotTestCase):
    def test_ug_no_class_year(self):
        self.webauthLoginAndMakeBallot('abc1', dict(assu_populations=['undergrad']))
        res = self.client.get('/ballot/')
        self.assertRedirects(res, '/ballot/choose')

    def test_ug_ok(self):
        self.webauthLoginAndMakeBallot('xyz1', dict(assu_populations=['undergrad'], undergrad_class_year='undergrad-1'))
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

class RealSMSABallotTest(OEBallotTestCase):
    def test_shows_smsa_schoolwide_candidates(self):
        self.webauthLoginAndMakeBallot('smsa1', smsa1)
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
        