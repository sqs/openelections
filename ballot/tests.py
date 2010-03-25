from openelections.tests import OETestCase
from openelections.issues.models import Electorate, Issue

def issue(slug):
    return Issue.objects.get(slug=slug).get_typed()

class UndergradBallotTest(OETestCase):
    pass