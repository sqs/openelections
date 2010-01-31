from django import forms
from openelections import constants as oe_constants
from openelections.issues.models import Issue
from openelections.petitions.models import Signature

class SignatureForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs=dict(size=45)))
    sunetid = forms.CharField(widget=forms.TextInput(attrs=dict(size=12)))
    studentid = forms.IntegerField(widget=forms.TextInput(attrs=dict(size=12)))
    enrollment_status = forms.ChoiceField(choices=oe_constants.ENROLLMENT_STATUSES, widget=forms.RadioSelect)
    ip_address = forms.CharField()
    signed_at = forms.DateField()
    issue = forms.ModelChoiceField(queryset=Issue.objects)
    
    def clean(self):
        '''Ensures that this SUNet ID has not already signed this petition'''
        
        # SUNet ID uniqueness - TODOsqs: test
        existing_sig = Signature.objects.get(sunetid=self.cleaned_data['sunetid'],
                                             issue=self.cleaned_data['issue'])
        if existing_sig:
            raise forms.ValidationError("User '%s' has already signed this petition." % self.cleaned_data['sunetid'])
    
    class Meta:
        model = Signature