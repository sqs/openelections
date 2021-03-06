from django import forms
from openelections.constants import ISSUE_TYPES
from openelections.issues.models import Electorate, Issue, SpecialFeeRequest, Slate, ExecutiveSlate, ClassPresidentSlate, Candidate, SenateCandidate, GSCCandidate, SMSACandidate

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue

class NewIssueForm(IssueForm):
    kind = forms.ChoiceField(choices=ISSUE_TYPES, widget=forms.HiddenInput)
    slug = forms.RegexField(label='URL name', help_text='Your petition will be at petitions.stanford.edu/petitions/your-url-name. Use only lowercase letters, numbers, and hyphens.',
                            regex=r'^[a-z\d-]+$', widget=forms.TextInput(attrs={'size':'25'}))
    
    def __init__(self, *args, **kwargs):
        super(NewIssueForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            self.fields['sunetid1'].widget.attrs['readonly'] = True
    
    def clean_sunetid1(self):
        """Always use the sunetid set on the instance instead of taking the first sunetid
        from the form POSTdata, since we don't verify that."""
        return self.instance.sunetid1
    
    def clean_slug(self):
        '''Ensure slug is unique'''
        slug = self.cleaned_data.get('slug')
        if slug:
            sameslugs = Issue.objects.filter(slug=slug).count()
            if sameslugs != 0:
                raise forms.ValidationError("Your desired URL name is already in use. Choose another.")
        return slug
    
class NewSlateForm(NewIssueForm):
    title = forms.CharField(label='Slate name', widget=forms.TextInput(attrs={'size':'40'}),
                            help_text='You can change this anytime until the start of Spring Quarter.')

class NewExecutiveSlateForm(NewSlateForm):
    class Meta:
        model = ExecutiveSlate
        fields = ('title', 'kind', 'name1', 'sunetid1', 'name2', 'sunetid2', 'slug')
    
    name1 = forms.CharField(label='President\'s name (you)', widget=forms.TextInput(attrs={'size':'40'}))
    sunetid1 = forms.CharField(label='President\'s SUNet ID @stanford.edu (you)', widget=forms.TextInput(attrs={'size':'12'}))
    name2 = forms.CharField(label='Vice President\'s name', widget=forms.TextInput(attrs={'size':'40'}))
    sunetid2 = forms.CharField(label='Vice President\'s SUNet ID @stanford.edu', widget=forms.TextInput(attrs={'size':'12'}))

class NewClassPresidentSlateForm(NewSlateForm):
    class Meta:
        model = ClassPresidentSlate
        fields = ('title', 'kind', 'electorate', 'name1', 'sunetid1', 'name2', 'sunetid2', 'name3', 'sunetid3', 
                               'name4', 'sunetid4', 'name5', 'sunetid5', 'slug')
    
    electorate = forms.ModelChoiceField(label='Class year',
                                        queryset=Electorate.UNDERGRAD_CLASS_YEARS,
                                        widget=forms.RadioSelect,
                                        empty_label=None,
                                        help_text="Select the class whose presidency you're seeking. For example, if you're running for Sophomore Class President, choose Sophomore.")
    
    name1 = forms.CharField(label='1st member\'s name (you)', widget=forms.TextInput(attrs={'size':'40'}),
                            help_text='The order of slate members (who\'s #1, #2, etc.) doesn\'t matter.')
    sunetid1 = forms.CharField(label='1st member\'s SUNet ID @stanford.edu (you)', widget=forms.TextInput(attrs={'size':'12'}))
    name2 = forms.CharField(label='2nd member\'s name', widget=forms.TextInput(attrs={'size':'40'}))
    sunetid2 = forms.CharField(label='2nd member\'s SUNet ID @stanford.edu', widget=forms.TextInput(attrs={'size':'12'}))
    name3 = forms.CharField(label='3rd member\'s name', widget=forms.TextInput(attrs={'size':'40'}))
    sunetid3 = forms.CharField(label='3rd member\'s SUNet ID @stanford.edu', widget=forms.TextInput(attrs={'size':'12'}))
    name4 = forms.CharField(label='4th member\'s name', widget=forms.TextInput(attrs={'size':'40'}))
    sunetid4 = forms.CharField(label='4th member\'s SUNet ID @stanford.edu', widget=forms.TextInput(attrs={'size':'12'}))
    name5 = forms.CharField(label='5th member\'s name', widget=forms.TextInput(attrs={'size':'40'}),
                            help_text='Only Junior Class President slates can have 5 members (if one member is abroad each quarter).',
                            required=False)
    sunetid5 = forms.CharField(label='5th member\'s SUNet ID @stanford.edu', widget=forms.TextInput(attrs={'size':'12'}),
                               required=False)
    
    def clean_electorate(self):
        electorate = self.cleaned_data.get('electorate')
        if electorate:
            return [electorate]
  
class NewCandidateForm(NewIssueForm):
    class Meta:
        model = Candidate
        fields = ('title', 'kind', 'name1', 'sunetid1', 'slug')
    
    name1 = forms.CharField(label='Your name', help_text='(as you would want it to appear on the ballot)',
                            widget=forms.TextInput(attrs={'size':'40'}))
    sunetid1 = forms.CharField(label='SUNet ID', widget=forms.TextInput(attrs={'size':'12'}))
    title = forms.CharField(widget=forms.HiddenInput, required=False)
    
    def clean(self):
        self.cleaned_data['title'] = self.cleaned_data.get('name1')
        return self.cleaned_data
    

class NewSenateCandidateForm(NewCandidateForm):
    pass
    
class NewGSCCandidateForm(NewCandidateForm):
    class Meta:
        model = GSCCandidate
        fields = ('title', 'kind', 'name1', 'sunetid1', 'electorate', 'slug')
    
    electorate = forms.ModelChoiceField(label='GSC district',
                                        help_text='Choose At-Large if you want to run ONLY as an At-Large candidate. All school-specific candidates are also considered as At-Large candidates, unless they choose otherwise.',
                                        queryset=Electorate.GSC_DISTRICTS,
                                        widget=forms.RadioSelect,
                                        empty_label=None,)
    
    def clean_electorate(self):
        electorate = self.cleaned_data.get('electorate')
        if electorate:
            return [electorate]
            
    def __init__(self, *args, **kwargs):
        super(NewGSCCandidateForm, self).__init__(*args, **kwargs)
        self.fields['slug'].help_text = 'Your candidate statement will be at voterguide.stanford.edu/your-url-name. Use only lowercase letters, numbers, and hyphens.'

class NewSMSACandidateForm(NewCandidateForm):
    class Meta:
        model = SMSACandidate
        fields = ('title', 'kind', 'name1', 'electorate', 'sunetid1', 'slug')
                                        
    electorate = forms.ModelChoiceField(label='SMSA',
                                        queryset=None,
                                        widget=forms.RadioSelect,
                                        empty_label=None,)
    
    def __init__(self, *args, **kwargs):
        super(NewSMSACandidateForm, self).__init__(*args, **kwargs)
        self.fields['slug'].help_text = 'Your candidate statement will be at voterguide.stanford.edu/your-url-name. Use only lowercase letters, numbers, and hyphens.'
        instance = getattr(self, 'instance', None)
        if instance:
            electorate_label = instance.candidate_electorate_label()
            if electorate_label == 'SMSA class year':
                self.fields['electorate'].label = 'SMSA class year'
                self.fields['electorate'].queryset = instance.candidate_electorates()
                self.fields['electorate'].help_text = 'Reminder: These are positions for next year. For example, if you are a 1st year, run for 2nd-Year Class Rep.'
            elif electorate_label == 'SMSA population':
                self.fields['electorate'].label = 'SMSA population'
                self.fields['electorate'].queryset = instance.candidate_electorates()
            else:
                del self.fields['electorate']
    
    
    def clean_electorate(self):
        electorate = self.cleaned_data.get('electorate')
        if electorate:
            return [electorate]                                

class EditIssueForm(IssueForm):
    class Meta:
        model = Issue
        fields = ('statement', 'image',)
    
    statement = forms.CharField(widget=forms.Textarea(attrs={'rows':15, 'cols':70, 'style':'width:98%'}), required=False)

    def __init__(self, *args, **kwargs):
        super(EditIssueForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            if instance.image:
                self.fields['image'].label = 'Replace existing image with another image'

class EditSpecialFeeRequestForm(EditIssueForm):
    class Meta:
        model = SpecialFeeRequest
        fields = ('statement', 'image', 'account_statement')

issue_edit_forms = {
    #'CandidateUS': EditCandidateUSForm,
    'Issue': EditIssueForm,
    'SpecialFeeRequest': EditSpecialFeeRequestForm,
}

issue_new_forms = {
    'Issue': NewIssueForm,
    'SenateCandidate': NewSenateCandidateForm,
    'ClassPresidentSlate': NewClassPresidentSlateForm,
    'ExecutiveSlate': NewExecutiveSlateForm,
    'GSCCandidate': NewGSCCandidateForm,
    'SMSACandidate': NewSMSACandidateForm,
    'SMSAClassRepCandidate': NewSMSACandidateForm,
    'SMSACCAPRepCandidate': NewSMSACandidateForm,
    'SMSASocialChairCandidate': NewSMSACandidateForm,
    'SMSAPolicyAndAdvocacyChairCandidate': NewSMSACandidateForm,
}

def form_class_for_issue(issue):
    issue_class_name = issue.__class__.__name__
    if issue.pk:
        return issue_edit_forms.get(issue_class_name, EditIssueForm)
    else:
        return issue_new_forms.get(issue_class_name, NewIssueForm)