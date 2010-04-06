from openelections.tests import OETestCase
from openelections.issues.models import Electorate, Issue
from openelections.petitions.models import Signature

class IssueAdditionsTest(OETestCase):
    def test_signed_by_sunetid_false(self):
        self.assertFalse(Issue.objects.get(slug='leland-senator').signed_by_sunetid('xyzhang'))
        
    def test_signed_by_sunetid_true(self):
        self.assertTrue(Issue.objects.get(slug='leland-senator').signed_by_sunetid('jsmith'))

class UnauthenticatedVisitorTest(OETestCase):
    def test_index(self):
        self.webauthLogin('jsmith')
        res = self.client.get('/petitions/')
        self.assertRedirects(res, '/issues/petitioning')
        
    def test_detail_requires_webauth(self):
        self.assertPathRequiresWebAuth('/petitions/leland-senator')

    def test_get_sign_requires_webauth(self):
        self.assertPathRequiresWebAuth('/petitions/leland-senator/sign')

    def test_post_sign_requires_webauth(self):
        res = self.client.post('/petitions/leland-senator/sign')
        self.assertResponseRequiresWebAuth(res)

class AuthenticatedVisitorTest(OETestCase):
    def test_detail_for_user_who_already_signed(self):
        self.webauthLogin('jsmith')
        res = self.client.get('/petitions/leland-senator')
        self.assertTemplateUsed(res, 'petitions/detail.html')
        self.assertContains(res, 'Leland Senator')
        self.assertContains(res, 'signed')
        self.assertNotContains(res, "You're signing a petition for")
        # does not contain signatures
        self.assertNotContains(res, 'Signatures')
        self.assertNotContains(res, 'John Smith')
    
    def test_detail_hides_signature_count_for_candidates(self):
        self.webauthLogin('xyzhang')
        res = self.client.get('/petitions/leland-senator')
        self.assertNotContains(res, "along with those of the other")
        
    def test_detail_shows_signature_count_for_sf_requests(self):
        self.webauthLogin('xyzhang')
        res = self.client.get('/petitions/sts')
        self.assertContains(res, "along with those of the other 0")
    
    def test_detail_after_signing_hides_signature_count_for_candidates(self):
        self.webauthLogin('jsmith')
        res = self.client.get('/petitions/leland-senator')
        self.assertNotContains(res, "along with")
    
    def test_detail_after_signing_shows_signature_count_for_sf_requests(self):
        self.webauthLogin('xyzhang')
        res = self.client.get('/petitions/stanford-joint-society')
        self.assertContains(res, "along with 1 other signer")
        
    def test_detail_for_user_who_has_not_already_signed(self):
        self.webauthLogin('xyzhang')
        res = self.client.get('/petitions/leland-senator')
        self.assertTemplateUsed(res, 'petitions/detail.html')
        self.assertContains(res, 'Leland Senator')
        self.assertNotContains(res, 'signed')
        self.assertContains(res, "You're signing a petition for")
        # does not contain signatures
        self.assertNotContains(res, 'Signatures')
        self.assertNotContains(res, 'John Smith')
    
    def test_detail_undergrad_fee_has_ug_and_coterm_enrollment_status_options(self):
        self.webauthLogin('xyzhang')
        res = self.client.get('/petitions/sts')
        self.assertTemplateUsed(res, 'petitions/detail.html')
        self.assertContains(res, 'Undergrad</label')
        self.assertNotContains(res, 'Grad</label>')
    
    def test_detail_joint_fee_has_grad_enrollment_status_option(self):
        self.webauthLogin('jsmith')
        res = self.client.get('/petitions/stanford-joint-society')
        self.assertTemplateUsed(res, 'petitions/detail.html')
        self.assertContains(res, 'Undergrad</label')
        self.assertContains(res, 'Grad</label>')
    
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
        res = self.client.post('/petitions/leland-senator/sign', postdata, HTTP_REFERER='http://petitions.stanford.edu/')
        self.assertTrue(lelandsen.signed_by_sunetid('xyzhang'))
    
    def test_sign_with_different_sunetid_than_authenticated_with(self):
        lelandsen = Issue.objects.get(slug='leland-senator')
        self.webauthLogin('xyzhang')
        postdata = {
            'name': 'Xiao Zhang',
            'electorate': Electorate.objects.get(name='Undergrad').pk,
            'sunetid': 'attacker',
        }
        res = self.client.post('/petitions/leland-senator/sign', postdata, HTTP_REFERER='http://petitions.stanford.edu/')
        self.assertTrue(lelandsen.signed_by_sunetid('xyzhang'))
        self.assertFalse(lelandsen.signed_by_sunetid('attacker'))
        
    # def test_sign_from_bad_referer(self):
    #     lelandsen = Issue.objects.get(slug='leland-senator')
    #     self.webauthLogin('xyzhang')
    #     postdata = {
    #         'name': 'Xiao Zhang',
    #         'electorate': Electorate.objects.get(name='Undergrad').pk,
    #     }
    #     res = self.client.post('/petitions/leland-senator/sign', postdata, HTTP_REFERER='http://attacker.com/abc')
    #     self.assertRedirects(res, '/petitions/leland-senator')
    #     self.assertFalse(lelandsen.signed_by_sunetid('xyzhang'))
        

class SpecialFeePetitionTest(OETestCase):
    def test_description(self):
        self.webauthLogin('xyzhang')
        res = self.client.get('/petitions/sts')
        self.assertContains(res, 'Special Fee request')
        self.assertContains(res, 'BUDGET SUMMARY')

class PetitionOwnerVisitorTest(OETestCase):
    def test_can_view_signatures(self):
        self.webauthLogin('lsenator')
        res = self.client.get('/petitions/leland-senator')
        self.assertTemplateUsed(res, 'petitions/detail.html')
        # contains signatures
        self.assertContains(res, 'Signatures')
        self.assertContains(res, 'jsmith')
        