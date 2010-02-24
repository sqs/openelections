from openelections.tests import OETestCase

class WebAuthTest(OETestCase):
    def test_logout(self):
        self.webauthLogin('ldavid')
        res = self.client.get('/issues/issue/larry-david/edit')
        self.assertEquals(res.status_code, 200)
        self.client.get('/auth/logout')
        res = self.client.get('/issues/issue/larry-david/edit')
        self.assertEquals(res.status_code, 302) # redirects to stanford webauth login
