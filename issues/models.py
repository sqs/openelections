from django.db import models
import simplejson
from openelections import constants as oe_constants

class Issue(models.Model):        
    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=50, choices=oe_constants.ISSUE_TYPES)
    profile = models.TextField(default='', blank=True)
    summary = models.TextField(default='', blank=True)
    image = models.ImageField(upload_to='issue_images', blank=True)
    slug = models.SlugField()
    
    # class pres
    class_year = models.CharField(max_length=1, choices=oe_constants.UNDERGRAD_CLASS_YEARS, blank=True)
    
    # gsc
    district = models.CharField(max_length=50, choices=oe_constants.GSC_DISTRICTS, blank=True)
    
    name1 = models.CharField(max_length=100)
    sunetid1 = models.CharField(max_length=8)
    studentid1 = models.CharField(max_length=8)
    
    name2 = models.CharField(max_length=100, blank=True)
    sunetid2 = models.CharField(max_length=8, blank=True)
    studentid2 = models.CharField(max_length=8, blank=True)
    
    name3 = models.CharField(max_length=100, blank=True)
    sunetid3 = models.CharField(max_length=8, blank=True)
    studentid3 = models.CharField(max_length=8, blank=True)
    
    name4 = models.CharField(max_length=100, blank=True)
    sunetid4 = models.CharField(max_length=8, blank=True)
    studentid4 = models.CharField(max_length=8, blank=True)
    
    name5 = models.CharField(max_length=100, blank=True)
    sunetid5 = models.CharField(max_length=8, blank=True)
    studentid5 = models.CharField(max_length=8, blank=True)
    
    # special fee groups
    budget = models.FileField(upload_to='budgets', blank=True)
    budget_summary = models.TextField(blank=True)
    
    def display_title(self):
        return self.title
    
    def __unicode__(self):
        return "%s: %s" % (self.kind, self.display_title())

    def get_typed(self):
        real_class = kinds_classes.get(self.kind, Issue)
        return real_class.objects.get(pk=self.pk)
    
    # candidates_us = issue_proxy_manager_factory(oe_constants.ISSUE_US)
    # candidates_gsc = issue_proxy_manager_factory(oe_constants.ISSUE_GSC)
    # slates_exec = issue_proxy_manager_factory(oe_constants.ISSUE_EXEC)
    # slates_classpres = issue_proxy_manager_factory(oe_constants.ISSUE_CLASSPRES)
    
        

def issue_proxy_manager_factory(kind):
    class IssueProxyManager(models.Manager):
        def get_query_set(self):
            return super(IssueProxyManager, self).get_query_set().filter(kind=kind)
    return IssueProxyManager()

class CandidateUS(Issue):
    is_candidate_us = True
    class Meta:
        proxy = True
    objects = issue_proxy_manager_factory(oe_constants.ISSUE_US)
    
    def office_name(self):
        return "Candidate for ASSU Undergraduate Senate"
        
class CandidateGSC(Issue):
    is_candidate_gsc = True
    class Meta:
        proxy = True
    objects = issue_proxy_manager_factory(oe_constants.ISSUE_GSC)
    
    def office_name(self):
        return "Candidate for ASSU Graduate Student Council"

class SlateExec(Issue):
    is_slate_exec = True
    class Meta:
        proxy = True
    objects = issue_proxy_manager_factory(oe_constants.ISSUE_EXEC)
    
    def office_name(self):
        return "Candidate for ASSU Executive"

class SlateClassPresident(Issue):
    is_slate_class_president = True
    class Meta:
        proxy = True
    objects = issue_proxy_manager_factory(oe_constants.ISSUE_CLASSPRES)
    
    def office_name(self):
        return "Candidate for ASSU %s Class President" % self.get_class_year_display()
    
    @classmethod
    def by_class_year(klass, class_year):
        return klass.objects.filter(class_year=class_year)

class SpecialFeeRequest(Issue):
    is_special_fee = True
    class Meta:
        proxy = True
    objects = issue_proxy_manager_factory(oe_constants.ISSUE_SPECFEE)

kinds_classes = {
    oe_constants.ISSUE_US: CandidateUS,
    oe_constants.ISSUE_GSC: CandidateGSC,
    oe_constants.ISSUE_EXEC: SlateExec,
    oe_constants.ISSUE_CLASSPRES: SlateClassPresident,
    oe_constants.ISSUE_SPECFEE: SpecialFeeRequest,
}