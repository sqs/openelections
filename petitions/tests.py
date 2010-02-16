from openelections.tests import OETestCase
from openelections.issues.models import Electorate, Issue
from openelections.petitions.models import Signature

class IssueAdditionsTest(OETestCase):
    def test_signed_by_sunetid_false(self):
        self.assertFalse(Issue.objects.get(slug='leland-senator').signed_by_sunetid('xyzhang'))
        
    def test_signed_by_sunetid_true(self):
        self.assertTrue(Issue.objects.get(slug='leland-senator').signed_by_sunetid('jsmith'))

class UnauthenticatedVisitorTest(OETestCase):    
    def test_index_requires_webauth(self):
        self.assertPathRequiresWebAuth('/petitions/')
        
    def test_detail_requires_webauth(self):
        self.assertPathRequiresWebAuth('/petitions/leland-senator')

    def test_get_sign_requires_webauth(self):
        self.assertPathRequiresWebAuth('/petitions/leland-senator/sign')

    def test_post_sign_requires_webauth(self):
        res = self.client.post('/petitions/leland-senator/sign')
        self.assertResponseRequiresWebAuth(res)

class AuthenticatedVisitorTest(OETestCase):
    def test_index(self):
        self.webauthLogin('jsmith')
        res = self.client.get('/petitions/')
        self.assertTemplateUsed(res, 'petitions/index.html')
        self.assertContains(res, 'Leland Senator')
    
    def test_detail_for_user_who_already_signed(self):
        self.webauthLogin('jsmith')
        res = self.client.get('/petitions/leland-senator')
        self.assertTemplateUsed(res, 'petitions/detail.html')
        self.assertContains(res, 'Leland Senator')
        self.assertContains(res, 'already signed')
        self.assertNotContains(res, "You're signing a petition for")
        # does not contain signatures
        self.assertNotContains(res, 'Signatures')
        self.assertNotContains(res, 'jsmith')
        
    def test_detail_for_user_who_has_not_already_signed(self):
        self.webauthLogin('xyzhang')
        res = self.client.get('/petitions/leland-senator')
        self.assertTemplateUsed(res, 'petitions/detail.html')
        self.assertContains(res, 'Leland Senator')
        self.assertNotContains(res, 'already signed')
        self.assertContains(res, "You're signing a petition for")
        # does not contain signatures
        self.assertNotContains(res, 'Signatures')
        self.assertNotContains(res, 'jsmith')
    
    def test_sign_with_method_get_redirects_to_detail(self):
        self.webauthLogin('xyzhang')
        res = self.client.get('/petitions/leland-senator/sign')
        self.assertRedirects(res, '/petitions/leland-senator')
        
    def test_sign(self):
        lelandsen = Issue.objects.get(slug='leland-senator')
        self.assertFalse(lelandsen.signed_by_sunetid('xyzhang'))
        self.webauthLogin('xyzhang')
        postdata = {
            'name': 'Xiao Zhang',
            'electorate': Electorate.objects.get(name='Undergrad').pk,
        }
        res = self.client.post('/petitions/leland-senator/sign', postdata)
        self.assertTrue(lelandsen.signed_by_sunetid('xyzhang'))
    
    def test_sign_with_different_sunetid_than_authenticated_with(self):
        lelandsen = Issue.objects.get(slug='leland-senator')
        self.webauthLogin('xyzhang')
        postdata = {
            'name': 'Xiao Zhang',
            'electorate': Electorate.objects.get(name='Undergrad').pk,
            'sunetid': 'attacker',
        }
        res = self.client.post('/petitions/leland-senator/sign', postdata)
        self.assertTrue(lelandsen.signed_by_sunetid('xyzhang'))
        self.assertFalse(lelandsen.signed_by_sunetid('attacker'))
    
def PetitionOwnerVisitorTest(OETestCase):
    def test_can_view_signatures(self):
        self.webauthLogin('lsenator')
        res = self.client.get('/petitions/leland-senator')
        self.assertTemplateUsed(res, 'petitions/detail.html')
        # contains signatures
        self.assertContains(res, 'Signatures')
        self.assertContains(res, 'jsmith')
        