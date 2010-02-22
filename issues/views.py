from django.shortcuts import render_to_response, get_object_or_404
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.core.urlresolvers import reverse
from openelections import constants as oe_constants
from openelections.auth.stanford_webauth import webauth_required
from openelections.issues.models import Issue
from openelections.issues.forms import IssueForm, form_class_for_issue

def index(request, show=None):
    issues = Issue.objects.all()
    return render_to_response('issues/index.html', {'issues': issues})

def detail(request, issue_slug):
    issue = get_object_or_404(Issue, slug=issue_slug)
    return render_to_response('issues/detail.html', {'issue': issue})

@webauth_required
def manage_index(request):
    sunetid = request.session['webauth_sunetid']
    issues = map(Issue.get_typed, Issue.filter_by_sponsor(sunetid))
    return render_to_response('issues/manage/index.html', {'issues': issues, 'sunetid': sunetid})

@webauth_required
def manage_new(request, issue_kind):
    sunetid = request.session['webauth_sunetid']
    new_issue = Issue(kind=issue_kind, sunetid1=sunetid).get_typed()
    form = form_class_for_issue(new_issue)(instance=new_issue)
    return render_to_response('issues/manage/new.html', {'new_issue': new_issue, 'form': form})

@webauth_required
def create(request):
    sunetid = request.session['webauth_sunetid']
    attrs = request.POST.copy()
    new_issue = Issue(kind=attrs['kind'], sunetid1=sunetid).get_typed()
    form = form_class_for_issue(new_issue)(attrs, instance=new_issue)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('openelections.issues.views.manage_index'))
    else:
        return render_to_response('issues/manage/new.html', {'new_issue': new_issue, 'form': form})

@webauth_required
def edit(request, issue_id):
    issue = get_object_or_404(Issue, pk=issue_id)
    form = None
    
    if request.method == 'POST':
        form = form_class_for_issue(issue)(request.POST, request.FILES, instance=issue)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('openelections.issues.views.detail', None, [issue.slug]))
    else:
        form = form_class_for_issue(issue)(instance=issue)
    
    return render_to_response('issues/edit.html', {'issue': issue, 'form': form})