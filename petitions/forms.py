from django import forms
from openelections import constants as oe_constants
from openelections.issues.models import Issue, Electorate
from openelections.petitions.models import Signature

class SignatureForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs=dict(size=45)), required=True,
                           help_text='Use your real name or else your signature won\'t count.')
    sunetid = forms.CharField(widget=forms.TextInput(attrs=dict(size=12)), required=True)
    ip_address = forms.CharField()
    signed_at = forms.DateField()
    issue = forms.ModelChoiceField(queryset=Issue.objects)
    
    def __init__(self, issue, *args, **kwargs):
        super(SignatureForm, self).__init__(*args, **kwargs)
        electorates = issue.petition_electorates()
        if electorates:
            self.fields['electorate'] = forms.ModelChoiceField(queryset=electorates,
                                                     widget=forms.RadioSelect,
                                                     empty_label=None)
        else:
            self.fields['electorate'] = None
        
        
    def clean_sunetid(self):
        '''Checks that the provided SUNet ID is alphanumeric and 3-8 chars long
           Ref: https://sunetid.stanford.edu/'''
        sunetid = self.cleaned_data.get('sunetid')
        if sunetid and sunetid.isalnum() and \
           len(sunetid) >= 3 and len(sunetid) <= 8:
            return sunetid
        else:
            raise forms.ValidationError("The SUNet ID '%s' is invalid." % sunetid)
            
    
    def clean(self):
        '''Ensures that this SUNet ID has not already signed this petition'''
        
        if not self.cleaned_data.get('sunetid'):
            return
        
        # SUNet ID uniqueness - TODOsqs: test
        existing_sig = Signature.objects.filter(sunetid=self.cleaned_data['sunetid'],
                                                issue=self.cleaned_data['issue'])
        if existing_sig:
            raise forms.ValidationError("User '%s' has already signed this petition." % self.cleaned_data['sunetid'])
        else:
            return self.cleaned_data
    
    class Meta:
        model = Signature