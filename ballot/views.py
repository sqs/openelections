from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.conf import settings
from django.template import RequestContext
from django.db import transaction
from django.shortcuts import render_to_response, get_object_or_404
from openelections import constants as oe_constants
from openelections.issues.models import Electorate, Issue
from openelections.ballot.forms import ballot_form_factory, BallotElectorateForm
from openelections.ballot.models import Ballot, make_voter_id
from openelections.webauth.stanford_webauth import webauth_required
from openelections.webauth.views import do_logout

def get_voter_id(request):
    return make_voter_id(request.session.get('webauth_sunetid'))

@transaction.commit_on_success
@webauth_required
def index(request):
    ballot = get_object_or_404(Ballot, voter_id=get_voter_id(request))
    
    if ballot.needs_ballot_choice():
        return HttpResponseRedirect('/ballot/choose')
    
    ballotform = ballot_form_factory(ballot)(instance=ballot)
    return render_to_response('ballot/ballot.html', {'ballotform': ballotform, 'ballot': ballot},
                              context_instance=RequestContext(request))

@transaction.commit_on_success
@webauth_required
def choose_ballot(request):
    ballot = get_object_or_404(Ballot, voter_id=get_voter_id(request))
    form = None
    if request.method == 'POST':
        form = BallotElectorateForm(request.POST, instance=ballot)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/ballot/')
    else:
        form = BallotElectorateForm(instance=ballot)
    return render_to_response('ballot/choose.html', {'form': form},
                              context_instance=RequestContext(request))

@transaction.commit_on_success
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
            print ballotform.errors
            return render_to_response('ballot/ballot.html', {'ballotform': ballotform, 'ballot': ballot},
                                      context_instance=RequestContext(request))
    do_logout(request)
    return render_to_response('ballot/done.html', {'ballot': ballot}, context_instance=RequestContext(request))
