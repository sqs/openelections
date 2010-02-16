from django.test import TestCase
from django.contrib.sessions.models import Session
from openelections.issues.models import Issue
from openelections.petitions.models import Signature

class IssueAdditionsTest(TestCase):
    fixtures = ['fixture1.json']
    
    def test_signed_by_sunetid_false(self):
        self.assertFalse(Issue.objects.get(slug='leland-senator').signed_by_sunetid('xyzhang'))
        
    def test_signed_by_sunetid_true(self):
        self.assertTrue(Issue.objects.get(slug='leland-senator').signed_by_sunetid('jsmith'))

class UnauthenticatedVisitorTest(TestCase):
    fixtures = ['fixture1.json']
    
    def assertResponseRequiresWebAuth(self, res):
        self.assertTrue(res['Location'].startswith('http://stanford.edu/'))
    
    def assertPathRequiresWebAuth(self, path):
        res = self.client.get(path)
        self.assertResponseRequiresWebAuth(res)
    
    def test_index_requires_webauth(self):
        self.assertPathRequiresWebAuth('/petitions/')
        
    def test_detail_requires_webauth(self):
        self.assertPathRequiresWebAuth('/petitions/leland-senator')

    def test_get_sign_requires_webauth(self):
        self.assertPathRequiresWebAuth('/petitions/leland-senator/sign')

    def test_post_sign_requires_webauth(self):
        res = self.client.post('/petitions/leland-senator/sign')
        self.assertResponseRequiresWebAuth(res)

class AuthenticatedVisitorTest(TestCase):
    fixtures = ['fixture1.json']
    
    def webauthLogin(self, sunetid):
        # must log in for session to be instantiated as real session
        self.client.login(username='sqs', password='q')
        self.client.get('/petitions/')
        s = self.client.session
        s['webauth_sunetid'] = sunetid
        s.save()
    
    def test_index(self):
        self.webauthLogin('jsmith')
        res = self.client.get('/petitions/')
        self.assertTemplateUsed(res, 'petitions/index.html')
        self.assertContains(res, 'Leland Senator')