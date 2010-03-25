from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from openelections import constants as oe_constants
from openelections.issues.models import Electorate, Issue
from openelections.ballot.forms import ballot_form_factory

def index(request, electorate_name='Freshman'):
    electorate = get_object_or_404(Electorate, name=electorate_name)
    ballotform = ballot_form_factory(electorate)
    return render_to_response('ballot/ballot.html', {'electorate': electorate, 'form': ballotform})

def vote_all(request):
    postdata = dict(request.POST)
    return HttpResponse("%r" % postdata)

def vote_one(request, issue_id):
    postdata = request.POST
    return HttpResponse("%r" % postdata)

def results(request):
    issues = Issue.objects.all()
    return render_to_response('ballot/results.html', {'issues': issues})
    