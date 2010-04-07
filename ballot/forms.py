import random
from django import forms
from django.forms.formsets import formset_factory, BaseFormSet
from django.utils.safestring import mark_safe
from openelections import constants as c
from openelections.ballot.models import Ballot
from openelections.issues.models import Issue, SenateCandidate, GSCCandidate, ExecutiveSlate, Electorate, SpecialFeeRequest, ClassPresidentSlate, kinds_classes

def html_id(issue):
    return 'issue_%d' % issue.pk
Issue.html_id = html_id

def objs_to_pks(objs):
    return ','.join([str(o.pk) for o in objs])
    
def pks_to_objs(pks):
    return [Issue.objects.get(pk=pk) for pk in map(int, pks.split(','))]

class BallotElectorateForm(forms.ModelForm):
    class Meta:
        model = Ballot
        fields = ['assu_populations', 'undergrad_class_year', 'gsc_district', 'smsa_class_year', 'smsa_population']

    class ElectorateChoiceField(forms.ModelChoiceField):
        widget = forms.RadioSelect
        
        def label_from_instance(self, instance):
            return instance.voter_name

    class ElectorateMultipleChoiceField(forms.ModelMultipleChoiceField):
        widget = forms.CheckboxSelectMultiple
        
        def label_from_instance(self, instance):
            return instance.voter_name

    def __init__(self, *args, **kwargs):
        if not kwargs['instance']:
            raise Exception("no instance for BallotElectorateForm")
        super(BallotElectorateForm, self).__init__(*args, **kwargs)

    assu_populations = ElectorateMultipleChoiceField(
        queryset=Electorate.queryset_with_slugs(Electorate.ASSU_POPULATIONS), 
        label='ASSU populations', help_text="Choose both if you are a coterm and currently registered as both an undergrad and a grad.",
        required=True)
        
    undergrad_class_year = ElectorateChoiceField(
        queryset=Electorate.queryset_with_slugs(Electorate.UNDERGRAD_CLASS_YEARS),
        label='Undergraduate class year',
        help_text='If unsure, choose the class year that you currently (this year) socially identify as a member of.',
        empty_label='N/A', required=False)
    
    gsc_district = ElectorateChoiceField(
        queryset=Electorate.queryset_with_slugs(Electorate.GSC_DISTRICTS_NO_ATLARGE),
        label='GSC district', help_text='If you are in multiple GSC districts, choose the one in which you want to select your local GSC rep.',
        empty_label='N/A', required=False)
    
    smsa_class_year = ElectorateChoiceField(
        queryset=Electorate.queryset_with_slugs(Electorate.SMSA_CLASS_YEARS),
        label='School of Medicine class year',
        empty_label='N/A', required=False)
                                             
    smsa_population = ElectorateChoiceField(
        queryset=Electorate.queryset_with_slugs(Electorate.SMSA_ALL_POPULATIONS),
        label='School of Medicine population',
        empty_label='N/A', required=False)

def ballot_form_factory(ballot):
    class _BallotForm(forms.ModelForm):
        class Meta:
            model = Ballot
            exclude = ['voter_id', 'assu_populations', 'undergrad_class_year', 'gsc_district', 'smsa_class_year', 'smsa_population']
        
        def __init__(self, *args, **kwargs):
            if not kwargs['instance']:
                raise Exception("no instance for BallotForm")
            super(_BallotForm, self).__init__(*args, **kwargs)
        
        def clean(self):
            #self.cleaned_data = self.clean_exec_votes()
            #self.cleaned_data = self.clean_classpres_votes()
            self.cleaned_data = self.clean_special_fee_votes()
            return self.cleaned_data
        
        def clean_exec_votes(self):
            pass
            
        def clean_classpres_votes(self):
            pass
        
        def clean_votes_senate(self):
            v = self.cleaned_data['votes_senate']
            max_choices = self.fields['votes_senate'].max_choices
            if len(v) > max_choices:
                raise forms.ValidationError('You may only cast %d votes for Senate (you chose %d).' % (max_choices, len(v)))
            return self.cleaned_data['votes_senate']
            
        def clean_votes_gsc_district(self):
            v = self.cleaned_data['votes_gsc_district']
            max_choices = self.fields['votes_gsc_district'].max_choices
            if len(v) > max_choices:
                raise forms.ValidationError('You may only cast %d vote(s) for GSC %s District rep (you chose %d).' % \
                                            (max_choices, self.instance.gsc_district.name, len(v)))
            return self.cleaned_data['votes_gsc_district']
            
        def clean_votes_gsc_atlarge(self):
            v = self.cleaned_data['votes_gsc_atlarge']
            max_choices = self.fields['votes_gsc_atlarge'].max_choices
            if len(v) > max_choices:
                raise forms.ValidationError('You may only cast %d at-large votes for GSC reps (you chose %d).' % (max_choices, len(v)))
            return self.cleaned_data['votes_gsc_atlarge']
        
        def clean_special_fee_votes(self):
            yes_votes = []
            no_votes = []
            
            for k,v in self.cleaned_data.items():
                if k.startswith('vote_specfee'):
                    pk = int(k[len('vote_specfee')+1:])
                    sf = SpecialFeeRequest.objects.get(pk=pk)
                    if not v: continue
                    v = int(v)
                    if v == c.VOTE_YES:
                        yes_votes.append(sf)
                    elif v == c.VOTE_NO:
                        no_votes.append(sf)
            
            self.cleaned_data['votes_specfee_yes'] = yes_votes
            self.cleaned_data['votes_specfee_no'] = no_votes
            
            return self.cleaned_data
        
        def save(self, commit=True):            
            #print "cd: %s" % self.cleaned_data
            
            # special fees
            self.instance.votes_specfee_yes = self.cleaned_data['votes_specfee_yes']
            self.instance.votes_specfee_no = self.cleaned_data['votes_specfee_no']
            
            super(_BallotForm, self).save(commit)
    
    
    exec_qs = ExecutiveSlate.objects.filter(kind=c.ISSUE_EXEC).order_by('pk').all()
    for i in range(1, Ballot.N_EXEC_VOTES+1):
        f_id = 'vote_exec%d' % i
        f = SlateChoiceField(queryset=exec_qs, required=False)
        _BallotForm.base_fields[f_id] = f
        _BallotForm.base_fields[f_id+'_writein'] = forms.CharField(required=False)
    
    all_specfees_qs = SpecialFeeRequest.objects.filter(kind=c.ISSUE_SPECFEE).order_by('pk').all()
    _BallotForm.base_fields['votes_specfee_yes'] = forms.ModelMultipleChoiceField(queryset=all_specfees_qs, required=False)
    _BallotForm.base_fields['votes_specfee_no'] = forms.ModelMultipleChoiceField(queryset=all_specfees_qs, required=False)

    if ballot.is_undergrad():
        senate_qs = SenateCandidate.objects.filter(kind=c.ISSUE_US).order_by('?').all()
        _BallotForm.base_fields['votes_senate'] = SenateCandidatesField(queryset=senate_qs, required=False)
        _BallotForm.base_fields['votes_senate_writein'] = forms.CharField(required=False, widget=forms.Textarea(attrs=dict(rows=2, cols=40)))
        
        classpres_qs = ClassPresidentSlate.objects.filter(kind=c.ISSUE_CLASSPRES, electorates=ballot.undergrad_class_year).order_by('pk').all()
        n_classpres = min(len(classpres_qs), Ballot.N_CLASSPRES_VOTES)
        for i in range(1, n_classpres+1):
            f_id = 'vote_classpres%d' % i
            f = SlateChoiceField(queryset=classpres_qs, required=False)
            _BallotForm.base_fields[f_id] = f
            _BallotForm.base_fields[f_id+'_writein'] = forms.CharField(required=False)
        for j in range(n_classpres+1, Ballot.N_CLASSPRES_VOTES+1):
            f_id = 'vote_classpres%d' % j
            del _BallotForm.base_fields[f_id]
            del _BallotForm.base_fields[f_id+'_writein']
    else:
        del _BallotForm.base_fields['votes_senate']
        del _BallotForm.base_fields['vote_classpres1']
        del _BallotForm.base_fields['vote_classpres2']
        del _BallotForm.base_fields['vote_classpres3']
        del _BallotForm.base_fields['vote_classpres4']
    
    if ballot.is_grad():
        gsc_district_qs = GSCCandidate.objects.filter(kind=c.ISSUE_GSC, electorates=ballot.gsc_district).order_by('?').all()
        f = GSCDistrictCandidatesField(queryset=gsc_district_qs, required=False, ballot=ballot)
        _BallotForm.base_fields['votes_gsc_district'] = f
        _BallotForm.base_fields['votes_gsc_district_writein'] = forms.CharField(required=False, widget=forms.Textarea(attrs=dict(rows=1, cols=40)))
        
        gsc_atlarge_qs = GSCCandidate.objects.filter(kind=c.ISSUE_GSC).order_by('?').all()
        _BallotForm.base_fields['votes_gsc_atlarge'] = GSCAtLargeCandidatesField(queryset=gsc_atlarge_qs, required=False)
        _BallotForm.base_fields['votes_gsc_atlarge_writein'] = forms.CharField(required=False, widget=forms.Textarea(attrs=dict(rows=2, cols=40)))
    else:
        del _BallotForm.base_fields['votes_gsc_district']
        del _BallotForm.base_fields['votes_gsc_district_writein']
        del _BallotForm.base_fields['votes_gsc_atlarge']
        del _BallotForm.base_fields['votes_gsc_atlarge_writein']
    
    if ballot.is_smsa():
        _BallotForm.smsa = True
        
        smsa_data = (
            ('vote_smsa_execpres', 'SMSA-ExecP'),
            ('vote_smsa_pres', 'SMSA-P'),
            ('vote_smsa_vicepres', 'SMSA-VP'),
            ('vote_smsa_sec', 'SMSA-S'),
            ('vote_smsa_treas', 'SMSA-T'),
            ('vote_smsa_mentorship', 'SMSA-MC'),
            ('vote_smsa_psrc', 'SMSA-PSRC'),
            ('vote_smsa_ossosr', 'SMSA-OSS-OSR'),
            ('vote_smsa_classrep', 'SMSA-ClassRep'),
            ('vote_smsa_socialchair', 'SMSA-SocChair'),
            ('vote_smsa_ccap', 'SMSA-CCAP'),
            ('vote_smsa_pachair', 'SMSA-PAC'),
        )
        
        # set querysets
        smsa_electorates = [Electorate.objects.get(slug='smsa'), ballot.smsa_class_year, ballot.smsa_population]
        for f_id, kind in smsa_data:
            qs = kinds_classes[kind].objects.filter(kind=kind, electorates__in=smsa_electorates).all()
            _BallotForm.base_fields[f_id] = SMSACandidatesChoiceField(queryset=qs, required=False)
    else:
        for k,v in _BallotForm.base_fields.items():
            if 'smsa' in k:
                del _BallotForm.base_fields[k]
    
    specfee_qs = SpecialFeeRequest.objects.filter(kind=c.ISSUE_SPECFEE, electorates__in=ballot.assu_populations.all()).order_by('pk').all()
    _BallotForm.fields_specfees = []
    for sf in specfee_qs:
        initial = None
        if sf in ballot.votes_specfee_yes.all():
            initial = c.VOTE_YES
        elif sf in ballot.votes_specfee_no.all():
            initial = c.VOTE_NO
        else:
            initial = c.VOTE_AB
        f_id = 'vote_specfee_%d' % sf.pk
        f = forms.ChoiceField(choices=c.VOTES_YNA, label=sf.title, required=False, initial=initial, widget=forms.RadioSelect)
        f.is_special_fee = True
        f.issue = sf
        _BallotForm.base_fields[f_id] = f
    
    return _BallotForm


class CandidatesField(forms.ModelMultipleChoiceField):
    widget = forms.CheckboxSelectMultiple
    
    def __init__(self, *args, **kwargs):
        self.ballot = kwargs.pop('ballot', None)
        super(CandidatesField, self).__init__(*args, **kwargs)
        
    def label_from_instance(self, instance):
        return instance.ballot_name()

class SenateCandidatesField(CandidatesField):
    max_choices = 15
    
    def label_from_instance(self, instance):
        return instance.ballot_name()

class SlateChoiceField(forms.ModelChoiceField):
    #widget = forms.RadioSelect
    
    def label_from_instance(self, instance):
        return instance.ballot_name()
        
class GSCCandidatesField(CandidatesField):
    pass
    
class GSCDistrictCandidatesField(GSCCandidatesField):
    def __init__(self, *args, **kwargs):
        if kwargs['ballot'].gsc_district.slug == 'gsc-eng':
            self.max_choices = 2
            kwargs['label'] = 'Choose up to 2 candidates.'
            kwargs['widget'] = forms.CheckboxSelectMultiple
        else:
            self.max_choices = 1
            kwargs['label'] = 'Choose 1 candidate.'
            kwargs['widget'] = forms.CheckboxSelectMultiple
        super(GSCDistrictCandidatesField, self).__init__(*args, **kwargs)
    
    def section_title(self):
        return "GSC %s District" % self.electorate.name
    
    def gsc_district(self):
        self.electorates.filter(slug__in=Electorate.GSC_DISTRICTS)
    
    def is_engineering(self):
        return self.gsc_district().slug == 'gsc-eng'
    
    def label(self):
        if self.is_engineering():
            return "Choose up to 2."
        else:
            return "Choose 1."
        
class GSCAtLargeCandidatesField(GSCCandidatesField):
    max_choices = 5
    
    def label_from_instance(self, instance):
        return "%s (%s)" % (instance.ballot_name(), instance.get_typed().district().name)

class SMSACandidatesChoiceField(forms.ModelChoiceField):
    widget = forms.RadioSelect
    
    def __init__(self, *args, **kwargs):
        super(SMSACandidatesChoiceField, self).__init__(*args, empty_label='(none)', **kwargs)
    
    def label_from_instance(self, instance):
        return instance.ballot_name()

