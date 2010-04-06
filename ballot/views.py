from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from openelections import constants as oe_constants
from openelections.issues.models import Electorate, Issue
from openelections.ballot.forms import ballot_form_factory
from openelections.ballot.models import Ballot, make_voter_id
from openelections.webauth.stanford_webauth import webauth_required

def get_voter_id(request):
    return make_voter_id(request.session.get('webauth_sunetid'))

@webauth_required
def index(request):
    ballot = get_object_or_404(Ballot, voter_id=get_voter_id(request))
    ballotform = ballot_form_factory(ballot)(instance=ballot)
    return render_to_response('ballot/ballot.html', {'ballotform': ballotform, 'electorate_names': ballot.electorates})

@webauth_required
def vote_all(request):
    # TODO: XSS
    form = None
    if request.method == 'POST':
        ballot = get_object_or_404(Ballot, voter_id=get_voter_id(request))
        ballotform = ballot_form_factory(ballot)(request.POST, instance=ballot)
        if ballotform.is_valid():
            ballotform.save()
            #return HttpResponse("vote saved: %s" % (ballot))
        else:
            #return HttpResponse("vote error: %r" % postdata)
            return render_to_response('ballot/ballot.html', {'ballotform': ballotform, 'electorate_names': ballot.electorates})
    return HttpResponseRedirect('/ballot/')

@webauth_required
def vote_one(request, issue_id):
    postdata = request.POST
    return HttpResponse("%r" % postdata)

@webauth_required
def results(request):
    issues = Issue.objects.all()
    return render_to_response('ballot/results.html', {'issues': issues})
    