from django.test import TestCase

class OETestCase(TestCase):
    fixtures = ['fixture1.json']
    
    def webauthLogin(self, sunetid):
        # must log in for session to be instantiated as real session
        self.client.login(username='sqs', password='q')
        self.client.get('/petitions/')
        s = self.client.session
        s['webauth_sunetid'] = sunetid
        s.save()