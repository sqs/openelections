from django.shortcuts import render_to_response
from django.http import HttpResponse
from openelections import constants as oe_constants
from openelections.issues.models import Issue#, CandidateUS, CandidateGSC, SlateExec, SlateClassPresident
from openelections.ballot.forms import ballot_form_factory

def index(request):
    # issues = dict()
    # issues[oe_constants.ISSUE_US] = CandidateUS.objects.all()
    # issues[oe_constants.ISSUE_GSC] = CandidateGSC.objects.all()
    # issues[oe_constants.ISSUE_EXEC] = SlateExec.objects.all()
    # issues[oe_constants.ISSUE_CLASSPRES] = SlateClassPresident.objects.all()
    ballotform = ballot_form_factory('a')
    return render_to_response('ballot/ballot.html', {'voter_type': 'U', 'form': ballotform})

def vote(request, issue_id):
    return HttpResponse("type=%s id=%s" % (issue_type, issue_id))

def results(request):
    issues = Issue.objects.all()
    return render_to_response('ballot/results.html', {'issues': issues})
    