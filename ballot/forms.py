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

def ballot_form_factory(ballot):
    class _BallotForm(forms.ModelForm):
        class Meta:
            model = Ballot
            #fields = ('votes_exec1',)
            exclude = ('voter_id', 'electorates', )
            #exclude = ('voter_id', 'electorates', 'votes_senate', 'votes_gsc_district', 'votes_gsc_atlarge', 
            #           'votes_specfee_yes', 'votes_specfee_no', 'votes_classpres')
        
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
        
        def clean_special_fee_votes(self):
            yes_votes = []
            no_votes = []
            
            for k,v in self.cleaned_data.items():
                if k.startswith('vote_specfee'):
                    pk = int(k[len('vote_specfee')+1:])
                    sf = SpecialFeeRequest.objects.get(pk=pk)
                    v = int(v)
                    if v == c.VOTE_YES:
                        yes_votes.append(sf)
                    elif v == c.VOTE_NO:
                        no_votes.append(sf)
            
            self.cleaned_data['votes_specfee_yes'] = yes_votes
            self.cleaned_data['votes_specfee_no'] = no_votes
            
            return self.cleaned_data
        
        def save(self, commit=True):            
            print "cd: %s" % self.cleaned_data
            
            # special fees
            self.instance.votes_specfee_yes = self.cleaned_data['votes_specfee_yes']
            self.instance.votes_specfee_no = self.cleaned_data['votes_specfee_no']
            
            super(_BallotForm, self).save(commit)
    
    electorate_objs = ballot.electorate_objs()        
    
    exec_qs = ExecutiveSlate.objects.filter(kind=c.ISSUE_EXEC).all()
    for i in range(1, Ballot.N_EXEC_VOTES+1):
        f_id = 'vote_exec%d' % i
        f = SlateChoiceField(queryset=exec_qs, required=False)
        _BallotForm.base_fields[f_id] = f
        _BallotForm.base_fields[f_id+'_writein'] = forms.CharField(required=False)
    
    all_specfees_qs = SpecialFeeRequest.objects.filter(kind=c.ISSUE_SPECFEE).all()
    _BallotForm.base_fields['votes_specfee_yes'] = forms.ModelMultipleChoiceField(queryset=all_specfees_qs, required=False)
    _BallotForm.base_fields['votes_specfee_no'] = forms.ModelMultipleChoiceField(queryset=all_specfees_qs, required=False)

    if ballot.is_undergrad():
        senate_qs = SenateCandidate.objects.filter(kind=c.ISSUE_US).all()
        _BallotForm.base_fields['votes_senate'] = SenateCandidatesField(queryset=senate_qs, required=False)
        _BallotForm.base_fields['votes_senate_writein'] = forms.CharField(required=False, widget=forms.Textarea(attrs=dict(rows=2, cols=40)))
        
        classpres_qs = ClassPresidentSlate.objects.filter(kind=c.ISSUE_CLASSPRES, electorates__in=ballot.electorate_objs).all()
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
        print _BallotForm.base_fields.items()
        del _BallotForm.base_fields['vote_classpres1']
        del _BallotForm.base_fields['vote_classpres2']
        del _BallotForm.base_fields['vote_classpres3']
        del _BallotForm.base_fields['vote_classpres4']
    
    if ballot.is_gsc():
        gsc_district_elecs = electorate_objs.filter(slug__in=Electorate.GSC_DISTRICTS).all()
        gsc_district_qs = GSCCandidate.objects.filter(kind=c.ISSUE_GSC, electorates__in=gsc_district_elecs).all()
        f = GSCDistrictCandidatesField(queryset=gsc_district_qs, required=False)
        _BallotForm.base_fields['votes_gsc_district'] = f
        f.district_names = ', '.join(map(lambda o: o.name, gsc_district_elecs))
        
        gsc_atlarge_qs = GSCCandidate.objects.filter(kind=c.ISSUE_GSC).all()
        _BallotForm.base_fields['votes_gsc_atlarge'] = GSCAtLargeCandidatesField(queryset=gsc_atlarge_qs, required=False)
    else:
        del _BallotForm.base_fields['votes_gsc_district']
        del _BallotForm.base_fields['votes_gsc_atlarge']
    
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
        for f_id, kind in smsa_data:
            qs = kinds_classes[kind].objects.filter(kind=kind, electorates__in=electorate_objs).all()
            _BallotForm.base_fields[f_id] = forms.ModelChoiceField(queryset=qs, required=False, widget=forms.RadioSelect, empty_label='None')
    else:
        for k,v in _BallotForm.base_fields.items():
            if 'smsa' in k:
                del _BallotForm.base_fields[k]
    
    specfee_qs = SpecialFeeRequest.objects.filter(kind=c.ISSUE_SPECFEE, electorates__in=electorate_objs).order_by('pk').all()
    _BallotForm.fields_specfees = []
    for sf in specfee_qs:
        initial = None
        if sf in ballot.votes_specfee_yes.all():
            initial = c.VOTE_YES
        elif sf in ballot.votes_specfee_no.all():
            initial = c.VOTE_NO
        else:
            initial = c.VOTE_AB
        print initial
        f_id = 'vote_specfee_%d' % sf.pk
        f = forms.ChoiceField(choices=c.VOTES_YNA, label=sf.title, required=False, initial=initial)
        f.is_special_fee = True
        f.issue = sf
        _BallotForm.base_fields[f_id] = f
    
    return _BallotForm


class CandidatesField(forms.ModelMultipleChoiceField):
    widget = forms.CheckboxSelectMultiple

class SenateCandidatesField(CandidatesField):
    def label_from_instance(self, instance):
        return instance.ballot_name()

class SlateChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, instance):
        return instance.ballot_name()

def irv_n_choices(n):
    return [(0, '------')] + [(i,i) for i in range(1, n+1)]

class SelectIRVOrder(forms.Select):
    def __init__(self, n, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        super(SelectIRVOrder, self).__init__(choices=irv_n_choices(n), *args, **kwargs)
        
    def render(self, name, value, attrs=None):
        return ('<label for="%s">%s: </label>' % (None, self.instance.title)) +  super(SelectIRVOrder, self).render(name, value, attrs=attrs)

class GSCCandidatesField(CandidatesField):
    pass
    
class GSCDistrictCandidatesField(GSCCandidatesField):
    def section_title(self):
        return "GSC %s District" % self.electorate.name
    
    def gsc_district(self):
        self.electorates.filter(slug__in=Electorate.GSC_DISTRICTS)
    
    def is_engineering(self):
        return self.gsc_district().slug == 'gsc-eng'
    
    def description(self):
        if self.is_engineering():
            return "Choose up to 2."
        else:
            return "Choose 1."
        
class GSCAtLargeCandidatesField(GSCCandidatesField):
    pass

class SMSACandidatesField(CandidatesField):
    def section_title(self):
        if not self.queryset: return "Empty (%s)" % self.kind
        return self.queryset[0].get_typed().kind_name()
    
    def help_text(self):
        return None


         
# class ExecSlatesIRVField(SlatesIRVField):
#     def section_title(self):
#         return "ASSU Executive"
#     
#     def description(self):
#         return "Rank the slates in order of your preference, with 1 being your first choice."    
# 
# class ClassPresSlatesIRVField(SlatesIRVField):
#     def section_title(self):
#         return self.queryset[0].get_typed().kind_name()
#     
#     def description(self):
#         return "Rank the slates in order of your preference, with 1 being your first choice."    

#class __CandidatesField(forms.ModelMultipleChoiceField):
    # def label_from_instance(self, obj):
    #     s = ['<ul class="issues">']
    #     for cand in self.queryset:
    #         s.append(self.widget_for_candidate(cand))
    #     s.append('</ul>')
    #     return mark_safe(''.join(s))
        
    # def widget_for_candidate(self, cand):
    #     attrs = dict(issue_pk=cand.pk, html_id="issue_%d" % cand.pk, 
    #                  html_name="candidates_us", label=cand.title)
    #     return '''<li class="issue">
    #                 <input type="checkbox" name="%(html_name)s" id="%(html_id)s" value="%(issue_pk)d">
    #                 <label for="%(html_id)s">%(label)s</label>
    #               </li>''' % attrs


# 
# class CandidatesGSCField(CandidatesField):
#     pass
#     
# class SlatesIRVField(forms.ModelMultipleChoiceField):
#     def label_from_instance(self, obj):        
#         self.num_slates = len(self.queryset)
#         rank_choices = [(i,i) for i in range(1,self.num_slates+1)]
#         rank_choices.insert(0, (0, '----'))
#         self.rank_select = forms.Select(choices=rank_choices)
#         
#         s = ['<ul class="issues">']
#         for slate in self.queryset:
#             s.append(self.widget_for_slate(slate))
#         s.append('</ul>')
#         return mark_safe(''.join(s))
# 
#         
#     def widget_for_slate(self, slate):
#         html_id = "issue_%d" % slate.pk
#         attrs = dict(html_id=html_id, html_name=html_id,
#                      label=slate.display_title(),
#                      select=self.rank_select.render(html_id, None))
#         return '''<li class="issue">
#                     <label for="%(html_id)s">%(label)s</label>
#                     %(select)s
#                   </li>''' % attrs
#                   
#     def __unicode__(self):
#         return self.label_from_instance(None)
#     

