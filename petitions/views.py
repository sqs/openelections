from datetime import datetime
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from openelections.petitions.models import Signature
from openelections.petitions.forms import SignatureForm
from openelections.issues.models import Issue
from openelections.auth.stanford_webauth import webauth_required

@webauth_required
def index(request):
    issues = Issue.objects.filter(public_petition=True).order_by('-kind').all()
    return render_to_response('petitions/index.html', {'issues': issues})

@webauth_required
def detail(request, issue_slug):
    issue = get_object_or_404(Issue, slug=issue_slug).get_typed()
    sunetid = request.session['webauth_sunetid']
    newsig = Signature()
    newsig.issue = issue
    newsig.sunetid = sunetid
    form = None
    if not issue.signed_by_sunetid(sunetid):
        form = SignatureForm(issue, instance=newsig)
    return render_to_response('petitions/detail.html', {
        'issue': issue,
        'form': form,
        'sunetid': sunetid,
        'viewing_own_petition': sunetid in issue.sunetids(),
    })

@webauth_required
def sign(request, issue_slug):
    issue = get_object_or_404(Issue, slug=issue_slug).get_typed()
    
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('openelections.petitions.views.detail', None, [issue_slug]))
    
    sunetid = request.session['webauth_sunetid']
    attrs = request.POST.copy()
    attrs['sunetid'] = sunetid
    attrs['issue'] = issue.id
    attrs['ip_address'] = request.META['REMOTE_ADDR']
    attrs['signed_at'] = datetime.now()
    form = SignatureForm(issue, attrs)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('openelections.petitions.views.detail', None, [issue_slug])+'#sign')
    else:
        return render_to_response('petitions/detail.html', {'issue': issue, 'form': form, 'sunetid': sunetid, 'jumptosign':True})
