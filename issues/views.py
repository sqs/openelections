import random
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponseForbidden
from django.core.urlresolvers import reverse
from openelections import constants as oe_constants
from openelections.webauth.stanford_webauth import webauth_required
from openelections.issues.models import Issue
from openelections.issues.forms import IssueForm, form_class_for_issue

index_filters = {
    'exec': (oe_constants.ISSUE_EXEC,),
    'gsc': (oe_constants.ISSUE_GSC,),
    'senate': (oe_constants.ISSUE_US,),
    'class-presidents': (oe_constants.ISSUE_CLASSPRES,),
    
    'special-fee-requests': (oe_constants.ISSUE_SPECFEE,),
    
    'smsa-president': ('SMSA-P', 'SMSA-ExecP'),
    'smsa-vice-president': ('SMSA-VP',),
    'smsa-secretary': ('SMSA-S',),
    'smsa-treasurer': ('SMSA-T',),
    'smsa-class-reps': ('SMSA-ClassRep',),
    'smsa-chairs': ('SMSA-PAC', 'SMSA-MC', 'SMSA-PSRC', 'SMSA-SocChair', 'SMSA-CSAC', 'SMSA-OSS-OSR'),
    'smsa-ccap': ('SMSA-CCAP',),
    
    'petitioning': [],
}

def index(request, show=None):
    issues = None
    if show:
        kind_filter = index_filters.get(show, None)
        if kind_filter is None:
            return HttpResponseNotFound()
        issues = Issue.filter_by_kinds(kind_filter).filter(public=True).all()
    else:
        issues = Issue.objects.filter(public=True).all()
    issues = map(Issue.get_typed, issues)
    random.shuffle(issues)
    return render_to_response('issues/index.html', {'issues': issues, 'detail': False}, context_instance=RequestContext(request))

def detail(request, issue_slug):
    issue = get_object_or_404(Issue, slug=issue_slug).get_typed()
    sunetid = request.session.get('webauth_sunetid', None)
    can_manage = issue.sunetid_can_manage(sunetid)
    return render_to_response('issues/detail.html', {'issue': issue, 'can_manage': can_manage, 'detail': True}, context_instance=RequestContext(request))

@webauth_required
def manage_index(request):
    sunetid = request.session['webauth_sunetid']
    issues = map(Issue.get_typed, Issue.filter_by_sponsor(sunetid))
    return render_to_response('issues/manage/index.html', {'issues': issues}, context_instance=RequestContext(request))

@webauth_required
def manage_new(request, issue_kind):
    sunetid = request.session['webauth_sunetid']
    new_issue = Issue(kind=issue_kind, sunetid1=sunetid).get_typed()
    form = form_class_for_issue(new_issue)(instance=new_issue)
    return render_to_response('issues/manage/new.html', {'new_issue': new_issue, 'form': form}, context_instance=RequestContext(request))

@webauth_required
def create(request):
    sunetid = request.session['webauth_sunetid']
    attrs = request.POST.copy()
    new_issue = Issue(kind=attrs['kind'], sunetid1=sunetid).get_typed()
    form = form_class_for_issue(new_issue)(attrs, instance=new_issue)
    if form.is_valid() and new_issue.can_declare():
        form.save()
        return HttpResponseRedirect(reverse('openelections.issues.views.manage_index'))
    else:
        return render_to_response('issues/manage/new.html', {'new_issue': new_issue, 'form': form}, context_instance=RequestContext(request))

@webauth_required
def manage_edit(request, issue_slug):
    issue = get_object_or_404(Issue, slug=issue_slug).get_typed()
    
    # only sponsors of an issue may edit it
    sunetid = request.session['webauth_sunetid']
    if not issue.sunetid_can_manage(sunetid):
        return HttpResponseForbidden()
    
    form = None
    if request.method == 'POST':
        form = form_class_for_issue(issue)(request.POST, request.FILES, instance=issue)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('openelections.issues.views.manage_edit', None, [issue.slug]))
    else:
        form = form_class_for_issue(issue)(instance=issue)
    
    return render_to_response('issues/manage/edit.html', {'issue': issue, 'form': form}, context_instance=RequestContext(request))