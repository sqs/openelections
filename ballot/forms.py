from django import forms
from django.utils.safestring import mark_safe
from openelections import constants as oe_constants
from openelections.ballot.models import Vote
from openelections.issues.models import Issue #, CandidateUS, CandidateGSC, SlateExec, SlateClassPresident, SpecialFeeRequest

# class CandidatesField(forms.ModelMultipleChoiceField):
#     def label_from_instance(self, obj):
#         s = ['<ul class="issues">']
#         for cand in self.queryset:
#             s.append(self.widget_for_candidate(cand))
#         s.append('</ul>')
#         return mark_safe(''.join(s))
#         
#     def widget_for_candidate(self, cand):
#         attrs = dict(html_id="issue_%d" % cand.pk, html_name="candidates_us",
#                      label=cand.display_title())
#         return '''<li class="issue">
#                     <input type="checkbox" name="%(html_name)s" id="%(html_id)s">
#                     <label for="%(html_id)s">%(label)s</label>
#                   </li>''' % attrs
#         
#     def __unicode__(self):
#         return self.label_from_instance(None)
# 
# class CandidatesUSField(CandidatesField):
#     pass
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
def ballot_form_factory(voter_type):
    class _BallotForm(forms.Form):
        pass
    
    _BallotForm.votes_us = CandidatesUSField(queryset=CandidateUS.objects.all())
    _BallotForm.votes_gsc = CandidatesGSCField(queryset=CandidateGSC.objects.all())
    _BallotForm.votes_exec = SlatesExecField(queryset=SlateExec.objects.all()) # verify that this maintains order
    _BallotForm.votes_classpres = SlatesClassPresField(queryset=SlateClassPresident.objects.all())
    
    _BallotForm.fields_specfees = []
    for fee in SpecialFeeRequest.objects.all():
        field_name = "specfee_%d" % fee.pk
        field = SpecialFeeRequestField()
        field.specialfeerequest = fee
        _BallotForm.base_fields[field_name] = field
        _BallotForm.fields_specfees.append(field)
    
    return _BallotForm
