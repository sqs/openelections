from django.db import models
from openelections.issues.models import *
from django.conf import settings
import hashlib

def make_voter_id(sunetid):
    m = hashlib.md5()
    m.update(settings.WEBAUTH_SECRET + 'sunetid_to_voter_id' + sunetid)
    return m.hexdigest()

class Ballot(models.Model):
    @classmethod
    def get_or_create_by_sunetid(klass, sunetid):
        v = make_voter_id(sunetid)
        return klass.objects.get_or_create(voter_id=v)
    
    voter_id = models.CharField(max_length=64, db_index=True)
    electorates = models.CharField(max_length=128)
    
    votes_senate = models.ManyToManyField(SenateCandidate, related_name='votes', blank=True)
    votes_senate_writein = models.CharField(max_length=500, blank=True)
    
    votes_gsc_district = models.ManyToManyField(GSCCandidate, related_name='votes_district', blank=True)
    votes_gsc_district_writein = models.CharField(max_length=500, blank=True)
    
    votes_gsc_atlarge = models.ManyToManyField(GSCCandidate, related_name='votes_atlarge', blank=True)
    votes_gsc_atlarge_writein = models.CharField(max_length=500, blank=True)
    
    votes_specfee_yes = models.ManyToManyField(SpecialFeeRequest, related_name='votes_yes', blank=True)
    votes_specfee_no = models.ManyToManyField(SpecialFeeRequest, related_name='votes_no', blank=True)
    
    N_EXEC_VOTES = 6
    vote_exec1 = models.ForeignKey(ExecutiveSlate, blank=True, null=True, related_name='votes_exec1')
    vote_exec2 = models.ForeignKey(ExecutiveSlate, blank=True, null=True, related_name='votes_exec2')
    vote_exec3 = models.ForeignKey(ExecutiveSlate, blank=True, null=True, related_name='votes_exec3')
    vote_exec4 = models.ForeignKey(ExecutiveSlate, blank=True, null=True, related_name='votes_exec4')
    vote_exec5 = models.ForeignKey(ExecutiveSlate, blank=True, null=True, related_name='votes_exec5')
    vote_exec6 = models.ForeignKey(ExecutiveSlate, blank=True, null=True, related_name='votes_exec6')
    vote_exec1_writein = models.CharField(max_length=75, blank=True)
    vote_exec2_writein = models.CharField(max_length=75, blank=True)
    vote_exec3_writein = models.CharField(max_length=75, blank=True)
    vote_exec4_writein = models.CharField(max_length=75, blank=True)
    vote_exec5_writein = models.CharField(max_length=75, blank=True)
    vote_exec6_writein = models.CharField(max_length=75, blank=True)

    N_CLASSPRES_VOTES = 4
    vote_classpres1 = models.ForeignKey(ClassPresidentSlate, blank=True, null=True, related_name='votes_classpres1')
    vote_classpres2 = models.ForeignKey(ClassPresidentSlate, blank=True, null=True, related_name='votes_classpres2')
    vote_classpres3 = models.ForeignKey(ClassPresidentSlate, blank=True, null=True, related_name='votes_classpres3')
    vote_classpres4 = models.ForeignKey(ClassPresidentSlate, blank=True, null=True, related_name='votes_classpres4')
    vote_classpres1_writein = models.CharField(max_length=75, blank=True)
    vote_classpres2_writein = models.CharField(max_length=75, blank=True)
    vote_classpres3_writein = models.CharField(max_length=75, blank=True)
    vote_classpres4_writein = models.CharField(max_length=75, blank=True)
    
    vote_smsa_execpres = models.ForeignKey(SMSACandidate, related_name='votes_execpres', blank=True, null=True)
    vote_smsa_pres = models.ForeignKey(SMSACandidate, related_name='votes_pres', blank=True, null=True)
    vote_smsa_vicepres = models.ForeignKey(SMSACandidate, related_name='votes_vicepres', blank=True, null=True)
    vote_smsa_sec = models.ForeignKey(SMSACandidate, related_name='votes_sec', blank=True, null=True)
    vote_smsa_treas = models.ForeignKey(SMSACandidate, related_name='votes_treas', blank=True, null=True)
    vote_smsa_mentorship = models.ForeignKey(SMSACandidate, related_name='votes_mentorship', blank=True, null=True)
    vote_smsa_psrc = models.ForeignKey(SMSACandidate, related_name='votes_psrc', blank=True, null=True)
    vote_smsa_ossosr = models.ForeignKey(SMSACandidate, related_name='votes_ossosr', blank=True, null=True)
    vote_smsa_classrep = models.ForeignKey(SMSAClassRepCandidate, related_name='votes', blank=True, null=True)
    vote_smsa_socialchair = models.ForeignKey(SMSASocialChairCandidate, related_name='votes', blank=True, null=True)
    vote_smsa_ccap = models.ForeignKey(SMSACCAPRepCandidate, related_name='votes', blank=True, null=True)
    vote_smsa_pachair = models.ForeignKey(SMSAPolicyAndAdvocacyChairCandidate, related_name='votes', blank=True, null=True)
    
    
    # updated_at
    
    def electorate_objs(self):
        return Electorate.objects.filter(slug__in=self.electorates_list()).all()
    
    def electorates_list(self):
        return self.electorates.split(',')
    
    def is_undergrad(self):
        return 'undergrad' in self.electorates_list()
        
    def is_gsc(self):
        return 'gsc' in self.electorates_list()
    
    def is_smsa(self):
        return 'smsa' in self.electorates_list()
    
    def __unicode__(self):
        return "Ballot: voter %s [%s]" % (self.voter_id, self.electorates)