import random
from django import forms
from django.forms.formsets import formset_factory, BaseFormSet
from django.utils.safestring import mark_safe
from openelections import constants as oe_constants
from openelections.ballot.models import Vote
from openelections.issues.models import Issue, SenateCandidate

class BallotFormSet(BaseFormSet):
    max_num = 0
    extra = 0
    
    def __init__(self, electorate, *args, **kwargs):
        self.electorate = electorate
        super(BallotFormSet, self).__init__(*args, **kwargs)
        self.make_forms()
        
    def make_forms(self):
        forms = {
            'form_us': (oe_constants.ISSUE_US, CandidatesForm),
            'form_exec': (oe_constants.ISSUE_EXEC, SlatesIRVForm),
            'form_classpres': (oe_constants.ISSUE_CLASSPRES, SlatesIRVForm),
            'form_specfees': (oe_constants.ISSUE_SPECFEE, SpecialFeesForm)
        }
        for form_name, (kind, form_class) in forms.items():
            setattr(self, form_name, form_class(queryset=Issue.objects.filter(kind=kind).all()))
            self.forms.append(getattr(self, form_name))
        
        
    
class CandidatesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')
        super(CandidatesForm, self).__init__(*args, **kwargs)
        self.make_fields()
    
    def make_fields(self):
        for s in self.queryset:
            field_id = 'vote_%d' % s.pk
            field = forms.BooleanField(label=s.title, required=False)
            self.fields[field_id] = field

class SlatesIRVForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')
        super(SlatesIRVForm, self).__init__(*args, **kwargs)
        self.make_fields()

    def make_fields(self):
        self.num_slates = len(self.queryset)
        choices = [(i,i) for i in range(1,self.num_slates+1)]
        choices.insert(0, (0, '----'))
        
        for s in self.queryset:
            field_id = 'vote_%d' % s.pk
            field = forms.ChoiceField(label=s.title, required=False, choices=choices)
            self.fields[field_id] = field

class SpecialFeesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset')
        super(SpecialFeesForm, self).__init__(*args, **kwargs)
        self.make_fields()

    def make_fields(self):
        for s in self.queryset:
            field_id = 'vote_%d' % s.pk
            field = forms.ChoiceField(label=s.title, required=False, choices=oe_constants.VOTES_YNA, widget=forms.RadioSelect)
            self.fields[field_id] = field

# class IRVWidget(forms.MultiWidget):
#     def __init__(self):
#         widgets = (forms.TextInput(),)
#         super(IRVWidget, self).__init__(widgets)
#     
#     def decompress(self, value):
#         return value
#     
#     def format_output(self, rendered_widgets):
#         return 'abcd'
#         return ' | '.join(rendered_widgets)
    
        # 
        # def render(self, name, value, attrs=None, choices=()):
        #     if not value: value = []
        #     return 'asdf'

class CandidatesField(forms.ModelMultipleChoiceField):
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
        
    def __unicode__(self):
        return self.label_from_instance(None)

class SenateCandidateField(forms.BooleanField):
    def __unicode__(self):
        return self.label_from_instance(None)
        
class SlatesIRVField(forms.ModelMultipleChoiceField):
    pass

class ClassPresidentsField(SlatesIRVField):
    pass

class ExecField(SlatesIRVField):
    pass

class ExecMultiWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (forms.CharField(),)
        super(ExecMultiWidget, self).__init__(widgets=widgets, attrs=attrs)
    
    def decompress(self, value):
        return value

class ExecMultiField(forms.MultiValueField):
    widget = ExecMultiWidget
    
    def __init__(self, **kwargs):
        fields = (forms.CharField(), forms.CharField(), forms.CharField(),)
        del kwargs['queryset']
        super(ExecMultiField, self).__init__(fields=fields, **kwargs)
    
    def compress(self, data_list):
        return data_list
        #return ','.join(data_list)
    
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
# class SlatesExecField(SlatesIRVField):
#     pass
#     
# class SlatesClassPresField(SlatesIRVField):
#     pass
#     
# class SpecialFeeRequestField(forms.ChoiceField):
#     choices = oe_constants.VOTES_YNA
#     specialfeerequest = None
#     
#     def __unicode__(self):
#         return super(SpecialFeeRequestField, self).__unicode__()
# 
#

def ballot_form_factory(_electorate):
    if not _electorate:
        raise Exception
    
    class _BallotForm(forms.Form):
        electorate = _electorate
        voter_id = forms.CharField()
        
        def __init__(self, *args, **kwargs):
            super(_BallotForm, self).__init__(*args, **kwargs)
            self.make_fields()
        
        def make_fields(self):
            self.votes_us = []
            self.votes_classpres = []
            self.votes_exec = []
            
            senators = Issue.objects.filter(kind='US').all()
            for s in senators:
                field_id = 'vote_us_%d' % s.pk
                field = SenateCandidateField(required=False, label='hello')
                self.fields[field_id] = field
                self.votes_us.append(field)
        
        # votes_us = SenateCandidatesField(widget=forms.CheckboxSelectMultiple, queryset=Issue.objects.filter(kind='US').all(), required=False)
        # votes_classpres = ClassPresidentsField(widget=forms.CheckboxSelectMultiple, queryset=Issue.objects.filter(kind=oe_constants.ISSUE_CLASSPRES).all(), required=False)
        # 
        # votes_exec = ExecMultiField(widget=ExecMultiWidget, queryset=Issue.objects.filter(kind=oe_constants.ISSUE_EXEC).all(), required=False)
        # 
        def save(self):
            # TODO: transactions
            voter_id = self.cleaned_data['voter_id']
            vote_fields = ('votes_us', 'votes_classpres', 'votes_exec',)
            for vote_field in vote_fields:
                for issue in self.cleaned_data[vote_field]:
                    v = Vote(voter_id=voter_id, issue=issue, electorate=self.electorate)
                    v.save()
                
        def clean(self):
            return self.cleaned_data
        
    
    #_BallotForm.electorate = electorate
    
    #_BallotForm.votes_gsc = CandidatesGSCField(queryset=CandidateGSC.objects.all())
    #_BallotForm.votes_exec = SlatesExecField(queryset=SlateExec.objects.all()) # verify that this maintains order
    #_BallotForm.votes_classpres = SlatesClassPresField(queryset=SlateClassPresident.objects.all())
    
    # _BallotForm.fields_specfees = []
    # for fee in SpecialFeeRequest.objects.all():
    #     field_name = "specfee_%d" % fee.pk
    #     field = SpecialFeeRequestField()
    #     field.specialfeerequest = fee
    #     _BallotForm.base_fields[field_name] = field
    #     _BallotForm.fields_specfees.append(field)
    
    return _BallotForm
