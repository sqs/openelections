from openelections.tests import OETestCase
from openelections.issues.models import Electorate, Issue
from openelections.petitions.models import Signature

class UnauthenticatedVisitorManageTest(OETestCase):    
    def test_manage_index_requires_webauth(self):
        self.assertPathRequiresWebAuth('/issues/manage/')
        
    def test_manage_new_requires_webauth(self):
        self.assertPathRequiresWebAuth('/issues/manage/new/US')

    def test_manage_create_requires_webauth(self):
        res = self.client.post('/issues/manage/create')
        self.assertResponseRequiresWebAuth(res)
    
class UnauthenticatedVisitorIssuesTest(OETestCase):    
    def test_index(self):
        res = self.client.get('/issues/')
        self.assertContains(res, 'Stanford Test Society')
        self.assertContains(res, 'Super Sophomores')
        self.assertContains(res, 'Leland Q. Senator')
    
    def test_index_filtered_special_fees(self):
        res = self.client.get('/issues/special-fee-requests')
        self.assertContains(res, 'Stanford Test Society')
        self.assertNotContains(res, 'Super Sophomores')
        self.assertNotContains(res, 'Leland Q. Senator')
        
    def test_index_filtered_senators(self):
        res = self.client.get('/issues/senate')
        self.assertNotContains(res, 'Stanford Test Society')
        self.assertNotContains(res, 'Super Sophomores')
        self.assertContains(res, 'Leland Q. Senator')
        
    def test_index_filtered_class_pres(self):
        res = self.client.get('/issues/class-presidents')
        self.assertNotContains(res, 'Stanford Test Society')
        self.assertContains(res, 'Super Sophomores')
        self.assertNotContains(res, 'Leland Q. Senator')
        
    def test_index_filtered_smsa_pres(self):
        res = self.client.get('/issues/smsa-president')
        self.assertContains(res, 'Jane Stanford')
        self.assertNotContains(res, 'Mary Smith')
        
    def test_index_filtered_smsa_vice_pres(self):
        res = self.client.get('/issues/smsa-vice-president')
        self.assertContains(res, 'Mary Smith')
        self.assertNotContains(res, 'Jane Stanford')
        
    def test_index_filtered_smsa_secretary(self):
        res = self.client.get('/issues/smsa-secretary')
        self.assertContains(res, 'Jerry Seinfeld')
        self.assertNotContains(res, 'Jane Stanford')
        
    def test_index_filtered_smsa_treasurer(self):
        res = self.client.get('/issues/smsa-treasurer')
        self.assertContains(res, 'Larry David')
        self.assertNotContains(res, 'Jane Stanford')
        
    def test_index_filtered_smsa_class_reps(self):
        res = self.client.get('/issues/smsa-class-reps')
        self.assertContains(res, 'Cheryl David')
        self.assertContains(res, 'Bart Simpson')
        self.assertContains(res, 'Monty Burns')
        self.assertContains(res, 'Ned Flanders')
        self.assertContains(res, 'Michael Bluth')
        self.assertNotContains(res, 'Jane Stanford')
    
    def test_index_filtered_smsa_social_chairs(self):
        res = self.client.get('/issues/smsa-social-chair')
        self.assertContains(res, 'George Costanza')
        self.assertContains(res, 'Jerry Lewis')
        self.assertNotContains(res, 'Jane Stanford')

    def test_index_filtered_smsa_ccap(self):
        res = self.client.get('/issues/smsa-ccap')
        self.assertContains(res, 'Kevin Spacey')
        self.assertContains(res, 'Timothy Geithner')
        self.assertContains(res, 'Joe Biden')
        self.assertNotContains(res, 'Jane Stanford')
        
    def test_index_filtered_smsa_chairs(self):
        res = self.client.get('/issues/smsa-chairs')
        self.assertContains(res, 'Rahm Emanuel')
        self.assertContains(res, 'John Kerry')
        self.assertContains(res, 'Howard Dean')
        self.assertNotContains(res, 'Jane Stanford')
        
    def test_index_filtered_404(self):
        res = self.client.get('/issues/non-existent')
        self.assertEquals(res.status_code, 404)
        
