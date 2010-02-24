from openelections.tests import OETestCase
from openelections.issues.models import Electorate, Issue
from openelections.petitions.models import Signature

def issue(slug):
    return Issue.objects.get(slug=slug).get_typed()

class SMSACandidateTest(OETestCase):
    def test_class_rep_elected_name(self):
        self.assertEquals(issue('cheryl-david').kind_name(), 'SMSA 1st Year Class Rep candidate')
        self.assertEquals(issue('bart-simpson').kind_name(), 'SMSA 2nd Year Class Rep candidate')
        self.assertEquals(issue('monty-burns').kind_name(), 'SMSA 3rd Year Class Rep candidate')
        self.assertEquals(issue('ned-flanders').kind_name(), 'SMSA 4th Year Class Rep candidate')
        self.assertEquals(issue('michael-bluth').kind_name(), 'SMSA 5th-Plus Year Class Rep candidate')
    
    def test_social_chair_elected_name(self):
        self.assertEquals(issue('george-costanza').kind_name(), 'SMSA Pre-clinical Social Chair candidate')
        self.assertEquals(issue('jerry-lewis').kind_name(), 'SMSA Clinical Social Chair candidate')
    
    def test_ccap_elected_name(self):
        self.assertEquals(issue('joe-biden').kind_name(), 'SMSA Clinical CCAP Rep candidate')
        self.assertEquals(issue('timothy-geithner').kind_name(), 'SMSA Pre-clinical CCAP Rep candidate')
        self.assertEquals(issue('kevin-spacey').kind_name(), 'SMSA MD-PhD CCAP Rep candidate')

    def test_ccap_elected_name(self):
        self.assertEquals(issue('joe-biden').kind_name(), 'SMSA Clinical CCAP Rep candidate')
        self.assertEquals(issue('timothy-geithner').kind_name(), 'SMSA Pre-clinical CCAP Rep candidate')
        self.assertEquals(issue('kevin-spacey').kind_name(), 'SMSA MD-PhD CCAP Rep candidate')
        
    def test_chair_elected_name(self):
        self.assertEquals(issue('howard-dean').kind_name(), 'SMSA Mentorship Chair candidate')
        self.assertEquals(issue('john-kerry').kind_name(), 'SMSA Advocacy Chair candidate')
        self.assertEquals(issue('rahm-emanuel').kind_name(), 'SMSA Policy Chair candidate')
        
    def test_presvpsectreas(self):
        self.assertEquals(issue('jane-stanford').kind_name(), 'SMSA President candidate')
        self.assertEquals(issue('mary-smith').kind_name(), 'SMSA Vice President candidate')
        self.assertEquals(issue('larry-david').kind_name(), 'SMSA Treasurer candidate')    

class UnauthenticatedVisitorManageTest(OETestCase):    
    def test_manage_index_requires_webauth(self):
        self.assertPathRequiresWebAuth('/issues/manage/')
        
    def test_manage_new_requires_webauth(self):
        self.assertPathRequiresWebAuth('/issues/manage/new/US')

    def test_manage_create_requires_webauth(self):
        res = self.client.post('/issues/manage/create')
        self.assertResponseRequiresWebAuth(res)

class AuthenticatedIssuesManageTest(OETestCase):
    def test_index_jsmith(self):
        self.webauthLogin('jsmith')
        res = self.client.get('/issues/manage')
        self.assertContains(res, 'Super Sophomores')
        
    def test_index_ldavid(self):
        self.webauthLogin('ldavid')
        res = self.client.get('/issues/manage')
        self.assertContains(res, 'Larry David')
        self.assertContains(res, 'Treasurer')
        self.assertNotContains(res, 'Generic issue')
    
    def test_index_smsa_has_public_profile_no_petition(self):
        self.webauthLogin('ldavid')
        res = self.client.get('/issues/manage')
        self.assertContains(res, 'public profile')
        self.assertNotContains(res, '/petitions/larry-david')
    
    def test_index_assu_has_no_public_profile_but_has_petition(self):
        self.webauthLogin('jsmith')
        res = self.client.get('/issues/manage')
        self.assertNotContains(res, 'public profile')
        self.assertContains(res, '/petitions/super-sophomores')
       
    def test_edit_ldavid(self):
        self.webauthLogin('ldavid')
        res = self.client.get('/issues/issue/larry-david/edit')
        self.assertContains(res, 'Larry David')
        self.assertContains(res, 'SMSA Treasurer')
        
    def test_update(self):
        self.webauthLogin('ldavid')
        res = self.client.post('/issues/issue/larry-david/edit', {'bio': 'Hello! New bio.'})
        self.assertRedirects(res, '/issues/issue/larry-david/edit')      
        res = self.client.get('/issues/issue/larry-david')
        self.assertContains(res, 'Hello! New bio.')
        
    def test_only_sponsor_can_edit(self):
        self.webauthLogin('jsmith')
        res = self.client.get('/issues/issue/larry-david/edit')
        self.assertEquals(res.status_code, 403)
        
    def test_only_sponsor_can_update(self):
        self.webauthLogin('jsmith')
        res = self.client.post('/issues/issue/larry-david/edit', {'bio': 'Hello! New bio.'})
        self.assertEquals(res.status_code, 403)
        res = self.client.get('/issues/issue/larry-david')
        self.assertNotContains(res, 'Hello! New bio.')
        

class UnauthenticatedVisitorIssuesTest(OETestCase):    
    def test_index(self):
        res = self.client.get('/issues/')
        self.assertContains(res, 'Stanford Test Society')
        self.assertContains(res, 'Super Sophomores')
        self.assertContains(res, 'Leland Q. Senator')
    
    def test_index_filtered_senators(self):
        res = self.client.get('/issues/exec')
        self.assertNotContains(res, 'Stanford Test Society')
        self.assertNotContains(res, 'Super Sophomores')
        # TODO: contains for exec
        
    def test_index_senators_no_public_profile(self):
        res = self.client.get('/issues/senate')
        self.assertNotContains(res, 'profile')
    
    def test_index_senators_hides_non_public(self):
        res = self.client.get('/issues/senate')
        self.assertNotContains(res, 'John Q. Private')
    
    def test_index_petitioning(self):
        self.webauthLogin('jsmith')
        res = self.client.get('/issues/petitioning')
        self.assertTemplateUsed(res, 'issues/index.html')
        self.assertContains(res, 'Leland Q. Senator')
        self.assertContains(res, 'Stanford Test Society')
        self.assertNotContains(res, 'Larry David') # no SMSA
    
    def test_index_omits_non_public_petitions(self):
        self.webauthLogin('jsmith')
        res = self.client.get('/issues/petitioning')
        self.assertNotContains(res, 'John Q. Private')
    
    def test_index_filtered_gsc(self):
        res = self.client.get('/issues/gsc')
        self.assertNotContains(res, 'Stanford Test Society')
        self.assertNotContains(res, 'Super Sophomores')
        # TODO: contains for GSC
    
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
        
    def test_index_filtered_smsa_secretary_none(self):
        res = self.client.get('/issues/smsa-secretary')
        self.assertContains(res, '<!-- empty list -->')
        
    def test_index_filtered_smsa_treasurer(self):
        res = self.client.get('/issues/smsa-treasurer')
        self.assertContains(res, 'Larry David')
        self.assertContains(res, 'SMSA Treasurer')
        self.assertNotContains(res, 'Generic issue')
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
        
