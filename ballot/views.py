from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from openelections import constants as oe_constants
from openelections.issues.models import Electorate, Issue
from openelections.ballot.forms import ballot_form_factory
from openelections.ballot.models import Ballot
from openelections.webauth.stanford_webauth import webauth_required



SAMPLE_VOTER_ID = 'frosh1'

@webauth_required
def index(request, voter_id=SAMPLE_VOTER_ID):
    ballot = get_object_or_404(Ballot, voter_id=voter_id)
    ballotform = ballot_form_factory(ballot)(instance=ballot)
    return render_to_response('ballot/ballot.html', {'ballotform': ballotform, 'electorate_names': ballot.electorates})

@webauth_required
def vote_all(request, voter_id=SAMPLE_VOTER_ID):
    # TODO: XSS
    form = None
    if request.method == 'POST':
        voter_id = SAMPLE_VOTER_ID# request.session['webauth_sunetid'] TODO: replace
        ballot = get_object_or_404(Ballot, voter_id=voter_id)
        ballotform = ballot_form_factory(ballot)(request.POST, instance=ballot)
        if ballotform.is_valid():
            ballotform.save()
            #return HttpResponse("vote saved: %s" % (ballot))
        else:
            #return HttpResponse("vote error: %r" % postdata)
            return render_to_response('ballot/ballot.html', {'ballotform': ballotform, 'electorate_names': ballot.electorates})
    return HttpResponseRedirect('/ballot/?ok')


@webauth_required
def vote_one(request, issue_id):
    postdata = request.POST
    return HttpResponse("%r" % postdata)

@webauth_required
def results(request):
    issues = Issue.objects.all()
    return render_to_response('ballot/results.html', {'issues': issues})
    