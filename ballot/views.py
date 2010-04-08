import simplejson, markdown
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.conf import settings
from django.template import RequestContext
from django.db import transaction
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, get_object_or_404
from openelections import constants as oe_constants
from openelections.issues.models import Electorate, Issue, ExecutiveSlate
from openelections.ballot.forms import ballot_form_factory, BallotElectorateForm
from openelections.ballot.models import Ballot, make_voter_id
from openelections.webauth.stanford_webauth import webauth_required
from openelections.webauth.views import do_logout

def get_voter_id(request):
    return make_voter_id(request.session.get('webauth_sunetid'))

def make_issues_json():
    issues = {}
    for o in Issue.objects.all():
        issues[str(o.pk)] = { 'statement': render_to_string('ballot/info.html', {'issue': o.get_typed(), 'detail': True, 'hidepdfs': True}) }
    return simplejson.dumps(issues)
    
def get_exec_slates():
    return ExecutiveSlate.objects.filter(kind='Exec').order_by('?').all()
    
def get_csac_members():
    return Issue.objects.filter(kind='SMSA-CSAC').order_by('title').all()
    
@transaction.commit_on_success
@webauth_required
def index(request):
    sunetid = request.session.get('webauth_sunetid')
    ballot, c = Ballot.get_or_create_by_sunetid(sunetid)
    
    if ballot.needs_ballot_choice():
        return HttpResponseRedirect('/ballot/choose')
    
    ballotform = ballot_form_factory(ballot)(instance=ballot)
    return render_to_response('ballot/ballot.html', {'ballotform': ballotform, 'ballot': ballot, 'issues_json': make_issues_json(), 'csac_members': get_csac_members(), 'exec_slates': get_exec_slates()},
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

@webauth_required
def record(request):
    ballot = get_object_or_404(Ballot, voter_id=get_voter_id(request))
    form = BallotElectorateForm(instance=ballot)
    return render_to_response('ballot/ballot_record.txt', {'ballot': ballot, 'request': request, 'form': form},
                              mimetype='text/plain', context_instance=RequestContext(request))

@transaction.commit_on_success
@webauth_required
def vote_all(request):
    # TODO: XSS
    form = None
    ballot = get_object_or_404(Ballot, voter_id=get_voter_id(request))
    if request.method == 'POST':
        ballotform = ballot_form_factory(ballot)(request.POST, instance=ballot)
        if ballotform.is_valid():
            ballotform.save()
        else:
            return render_to_response('ballot/ballot.html', {'ballotform': ballotform, 'ballot': ballot, 'issues_json': make_issues_json(),'csac_members': get_csac_members(),  'exec_slates': get_exec_slates()},
                                      context_instance=RequestContext(request))
    return render_to_response('ballot/done.html', {'ballot': ballot, 'request': request,}, context_instance=RequestContext(request))
