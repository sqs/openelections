from django.shortcuts import render_to_response, get_object_or_404
from django.core.files.uploadedfile import SimpleUploadedFile
from openelections import constants as oe_constants
from openelections.issues.models import Issue, CandidateUS, CandidateGSC, SlateExec, SlateClassPresident
from openelections.issues.forms import IssueForm, form_class_for_issue

def index(request):
    show = request.GET.get('show', 'us,gsc,exec,classpres,specialfee')
    issues = {
        'us': 'us' in show and CandidateUS.objects.all(),
        'gsc': 'gsc' in show and CandidateGSC.objects.all(),
        'exec': 'exec' in show and SlateExec.objects.all(),
        'classpres_sophomore': 'classpres' in show and SlateClassPresident.by_class_year(oe_constants.CLASS_YEAR_SOPHOMORE),
        'classpres_junior': 'classpres' in show and SlateClassPresident.by_class_year(oe_constants.CLASS_YEAR_JUNIOR),
        'classpres_senior': 'classpres' in show and SlateClassPresident.by_class_year(oe_constants.CLASS_YEAR_SENIOR),
        'specialfee': 'specialfee' in show and SpecialFeeRequest.objects.all()
    }
    return render_to_response('issues/index.html', {'issues_by_kind': issues})

def detail(request, issue_id):
    issue = get_object_or_404(Issue, pk=issue_id)
    return render_to_response('issues/detail.html', {'issue': issue})
    
def edit(request, issue_id):
    issue = get_object_or_404(Issue, pk=issue_id)
    issue = issue.get_typed()
    form = None
    
    if request.method == 'POST':
        form = form_class_for_issue(issue)(request.POST, request.FILES, instance=issue)
        if form.is_valid():
            form.save()
    else:
        form = form_class_for_issue(issue)(instance=issue)
    
    return render_to_response('issues/edit.html', {'issue': issue, 'form': form})