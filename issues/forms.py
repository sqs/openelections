from django import forms
from openelections.constants import ISSUE_TYPES
from openelections.ballot.models import Vote
from openelections.issues.models import Issue, CandidateUS, CandidateGSC, SlateExec, SlateClassPresident

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue

class NewIssueForm(IssueForm):
    kind = forms.ChoiceField(choices=ISSUE_TYPES, widget=forms.HiddenInput)
    
class EditIssueForm(IssueForm):
    class Meta:
        pass

class EditCandidateForm(EditIssueForm):
    class Meta:
        pass # include specified in subclasses

class EditCandidateUSForm(EditCandidateForm):
    class Meta:
        model = CandidateUS
        fields = ('profile', 'summary', 'image',)
        

issues_forms = {
    'CandidateUS': EditCandidateUSForm,
    'Issue': EditIssueForm
}
def form_class_for_issue(issue):
    return issues_forms[issue.__class__.__name__]