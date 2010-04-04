from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from openelections import constants as oe_constants
from openelections.issues.models import Electorate, Issue
from openelections.ballot.forms import BallotFormSet
from openelections.webauth.stanford_webauth import webauth_required

@webauth_required
def index(request, electorate_name='Freshman'):
    electorate = get_object_or_404(Electorate, name=electorate_name)
    ballotformset = BallotFormSet(electorate)
    return render_to_response('ballot/ballot.html', {'electorate': electorate, 'formset': ballotformset})

@webauth_required
def vote_all(request, electorate_name='Freshman'):
    electorate = get_object_or_404(Electorate, name=electorate_name)
    # TODO: XSS
    form = None
    if request.method == 'POST':
        postdata = dict(request.POST.copy())
        postdata['voter_id'] = request.session['webauth_sunetid']
        form = BallotFormSet(electorate, postdata)
        if form.is_valid():
            form.save()
            return HttpResponse("vote saved")
    return HttpResponseRedirect('/ballot/')


@webauth_required
def vote_one(request, issue_id):
    postdata = request.POST
    return HttpResponse("%r" % postdata)

@webauth_required
def results(request):
    issues = Issue.objects.all()
    return render_to_response('ballot/results.html', {'issues': issues})
    