import simplejson, markdown
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseForbidden
from django.conf import settings
from django.template import RequestContext
from django.db import transaction
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, get_object_or_404
from openelections import constants as oe_constants
from openelections.issues.models import Electorate, Issue, ExecutiveSlate, ClassPresidentSlate
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

def get_cp_slates(ballot):
    return ClassPresidentSlate.objects.filter(kind=oe_constants.ISSUE_CLASSPRES, electorates=ballot.undergrad_class_year).order_by('?').all()
    

@transaction.commit_on_success
@webauth_required
def index(request):
    sunetid = request.session.get('webauth_sunetid')
    ballot, c = Ballot.get_or_create_by_sunetid(sunetid)
    
    if ballot.needs_ballot_choice():
        return HttpResponseRedirect('/ballot/choose')
    
    ballotform = ballot_form_factory(ballot)(instance=ballot)
    return render_to_response('ballot/ballot.html', {'ballotform': ballotform, 'ballot': ballot, 'issues_json': make_issues_json(), 'cp_slates': get_cp_slates(ballot), 'csac_members': get_csac_members(), 'exec_slates': get_exec_slates()},
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
    return render_to_response('ballot/choose.html', {'form': form, 'ballot': ballot},
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
    # protect against XSS
    if settings.DEBUG:
        h = request.META.get('HTTP_REFERER', 'not')
        if not (
                h.startswith('http://sqs-koi.stanford.edu') or \
                h.startswith('http://ballot.stanford.edu') or \
                h.startswith('http://ballot')):
           return HttpResponseForbidden()
       
    form = None
    ballot = get_object_or_404(Ballot, voter_id=get_voter_id(request))
    if request.method == 'POST':
        ballotform = ballot_form_factory(ballot)(request.POST, instance=ballot)
        if ballotform.is_valid():
            ballotform.save()
        else:
            return render_to_response('ballot/ballot.html', {'ballotform': ballotform, 'ballot': ballot, 'issues_json': make_issues_json(), 'cp_slates': get_cp_slates(ballot), 'csac_members': get_csac_members(),  'exec_slates': get_exec_slates()},
                                      context_instance=RequestContext(request))
    
    sunetid = request.session.get('webauth_sunetid')
    record = render_to_string('ballot/ballot_record.txt', {'ballot': ballot, 'request': request, 'form': form, 'sunetid': sunetid})
    
    f = open('/tmp/ballot/%s' % sunetid, 'a')
    f.write(record)
    f.write("\nPOSTDATA: %s\n\n" % request.POST.copy())
    f.close()
    
    do_logout(request)
    return render_to_response('ballot/done.html', {'ballot': ballot, 'request': request,}, context_instance=RequestContext(request))
