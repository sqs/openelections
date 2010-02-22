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

    def test_index_filtered_404(self):
        res = self.client.get('/issues/non-existent')
        self.assertEquals(res.status_code, 404)
        
