from django.test import TestCase
from openelections.issues.models import Issue
from openelections.petitions.models import Signature

class IssueAdditionsTest(TestCase):
    fixtures = ['fixture1.json']
    
    def test_signed_by_sunetid_false(self):
        self.assertFalse(Issue.objects.get(slug='leland-senator').signed_by_sunetid('xyzhang'))
        
    def test_signed_by_sunetid_true(self):
        self.assertTrue(Issue.objects.get(slug='leland-senator').signed_by_sunetid('jsmith'))
