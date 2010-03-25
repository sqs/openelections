from django.shortcuts import render_to_response
from django.http import HttpResponse
from openelections import constants as oe_constants
from openelections.issues.models import Issue#, CandidateUS, CandidateGSC, SlateExec, SlateClassPresident
from openelections.ballot.forms import ballot_form_factory

def index(request):
    return render_to_response('ballot/ballot.html', {})

def vote(request, issue_id):
    postdata = request.POST
    return HttpResponse("%r" % postdata)

def results(request):
    issues = Issue.objects.all()
    return render_to_response('ballot/results.html', {'issues': issues})
    