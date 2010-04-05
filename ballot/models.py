from django.db import models
from openelections.issues.models import *

class Ballot(models.Model):
    voter_id = models.CharField(max_length=64)
    electorates = models.CharField(max_length=128)
    
    votes_senate = models.ManyToManyField(SenateCandidate, related_name='votes', blank=True)
    votes_exec = models.ManyToManyField(ExecutiveSlate, related_name='votes', blank=True)
    votes_classpres = models.ManyToManyField(ClassPresidentSlate, related_name='votes', blank=True)
    votes_gsc_district = models.ManyToManyField(GSCCandidate, related_name='votes_district', blank=True)
    votes_gsc_atlarge = models.ManyToManyField(GSCCandidate, related_name='votes_atlarge', blank=True)
    votes_specfee_yes = models.ManyToManyField(SpecialFeeRequest, related_name='votes_yes', blank=True)
    votes_specfee_no = models.ManyToManyField(SpecialFeeRequest, related_name='votes_no', blank=True)
    
    # updated_at
    
    def electorate_objs(self):
        slugs = self.electorates.split(',')
        return Electorate.objects.filter(slug__in=slugs).all()
        
    def is_undergrad(self):
        return 'undergrad' in self.electorates
    
    def __unicode__(self):
        return "Ballot: voter %s [%s]" % (self.voter_id, self.electorates)