from datetime import datetime
from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from openelections.petitions.models import Signature
from openelections.petitions.forms import SignatureForm
from openelections.issues.models import Issue
from openelections.auth.stanford_webauth import webauth_required

def index(request):
    issues = Issue.objects.all()
    return render_to_response('petitions/index.html', {'issues': issues})

@webauth_required
def detail(request, issue_id):
    issue = get_object_or_404(Issue, pk=issue_id).get_typed()
    newsig = Signature()
    newsig.issue = issue
    form = None
    if not issue.signed_by_sunetid('sqs'):
        form = SignatureForm(instance=newsig)
    return render_to_response('petitions/detail.html', {'issue': issue, 'form': form})
    
def sign(request, issue_id):
    issue = get_object_or_404(Issue, pk=issue_id)
    attrs = request.POST.copy()
    attrs['issue'] = issue.id
    attrs['ip_address'] = request.META['REMOTE_ADDR']
    attrs['signed_at'] = datetime.now()
    form = SignatureForm(attrs)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('openelections.petitions.views.detail', None, [issue_id]))
    else:
        return render_to_response('petitions/detail.html', {'issue': issue, 'form': form})