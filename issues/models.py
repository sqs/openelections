from django.db import models
from django.db.models import Q
import simplejson
from openelections import constants as oe_constants

ELECTORATES = {
    'undergrad': 'Undergrad',
    'grad': 'Grad',
    'coterm': 'Coterm',
    'undergrad-freshman': 'Freshman',
    'undergrad-sophomore': 'Sophomore',
    'undergrad-junior': 'Junior',
    'undergrad-senior': 'Senior',
}

UNDERGRAD_CLASS_YEARS = ('undergrad-sophomore', 'undergrad-junior', 'undergrad-senior')

class Electorate(models.Model):
    name = models.CharField(max_length=50)
    
    @classmethod
    def queryset_with_names(klass, names):
        full_names = [ELECTORATES[name] for name in names]
        return klass.objects.filter(name__in=full_names)
    
    @classmethod
    def undergrad_class_years(klass):
        return klass.queryset_with_names(UNDERGRAD_CLASS_YEARS)
    
    def __unicode__(self):
        return self.name

class Issue(models.Model):        
    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=50, choices=oe_constants.ISSUE_TYPES)
    bio = models.TextField(default='', blank=True)
    bio_short = models.TextField(default='', blank=True)
    bio_petition = models.TextField(default='', blank=True)
    image = models.ImageField(upload_to='site_media/issue_images', blank=True)
    slug = models.SlugField()
    
    # restriction to certain populations
    electorate = models.ManyToManyField(Electorate, related_name='issues') #MultipleChoiceField(max_length=250, choices=oe_constants.ELECTORATES)

    name1 = models.CharField(max_length=100)
    sunetid1 = models.CharField(max_length=15)
    
    name2 = models.CharField(max_length=100, blank=True)
    sunetid2 = models.CharField(max_length=8, blank=True)
    
    name3 = models.CharField(max_length=100, blank=True)
    sunetid3 = models.CharField(max_length=8, blank=True)
    
    name4 = models.CharField(max_length=100, blank=True)
    sunetid4 = models.CharField(max_length=8, blank=True)
    
    name5 = models.CharField(max_length=100, blank=True)
    sunetid5 = models.CharField(max_length=8, blank=True)
    
    # special fee groups
    budget = models.FileField(upload_to='budgets', blank=True)
    budget_summary = models.TextField(blank=True)
    
    def __unicode__(self):
        return "%s: %s" % (self.kind, self.title)

    def get_typed(self):
        issue_class = kinds_classes.get(self.kind, Issue)
        self.__class__ = issue_class
        return self
    
    def petition_electorates(self):
        names = self.petition_electorate_names()
        if names:
            return Electorate.queryset_with_names(names)
        else:
            return None
    
    def petition_electorate_names(self):
        raise NotImplementedError
    
    def kind_name(self):
        return "Generic issue"
    
    def name_and_office(self):
        return "Generic issue"
        
    @classmethod
    def filter_by_sponsor(klass, sunetid):
        '''Returns all issues sponsored by sunetid or of which sunetid
        is a member.'''
        return klass.objects.filter(Q(sunetid1=sunetid) | Q(sunetid2=sunetid) |
                                    Q(sunetid3=sunetid) | Q(sunetid4=sunetid) |
                                    Q(sunetid5=sunetid))

class Candidate(Issue): 
    class Meta:
        proxy = True
        
    def kind_name(self):
        return "candidate"

class FeeRequest(Issue):
    class Meta:
        proxy = True
        
class SpecialFeeRequest(FeeRequest):
    class Meta:
        proxy = True

class Slate(Issue):
    class Meta:
        proxy = True
        
    def kind_name(self):
        return "slate"
    
class ExecutiveSlate(Slate):
    class Meta:
        proxy = True
    
    def petition_electorate_names(self):
        return ('undergrad', 'coterm', 'grad')
    
    def kind_name(self):
        return "Executive slate"
        
    def elected_name(self):
        return "ASSU Executive"
    
    def name_and_office(self):
        return "%s, a slate for ASSU Executive with %s for President and %s for Vice President" \
               % (self.title, self.name1, self.name2)

class ClassPresidentSlate(Slate):
    class Meta:
        proxy = True
        
    def petition_electorate_names(self):
        return ('undergrad', 'coterm')
        
    def class_year(self):
        class_years = Electorate.undergrad_class_years()
        class_years = [cy.name for cy in class_years]
        slate_year = self.electorate.filter(name__in=class_years)
        if not slate_year:
            raise Exception('no slate year found for class president slate %d' % self.pk)
        return slate_year[0]
    
    def kind_name(self):
        if self.pk:
            return "%s Class President slate" % self.class_year()
        else:
            # if we haven't saved this, we don't know what year -- so be general
            return "Class President slate"
    
    def elected_name(self):
        return "Class President"
    
    def name_and_office(self):
        # join names with ", and" before last one
        names = [self.name1, self.name2, self.name3, self.name4, self.name5]
        names = [n for n in names if n]
        names_str = ', '.join(names[:-1]) + ', and ' + names[-1]
        return "%s, a slate for ASSU %s Class President with %s" \
               % (self.title, self.class_year().name, names_str)

class SenateCandidate(Candidate):
    class Meta:
        proxy = True
    
    def petition_electorate_names(self):
        return ('undergrad', 'coterm')
    
    def kind_name(self):
        return "Undergraduate Senate candidate"
        
    def elected_name(self):
        return "Undergrad Senator"
    
    def name_and_office(self):
        return "%s, a candidate for ASSU Undergraduate Senate" % self.name1

###############
# Class map
###############
kinds_classes = {
    oe_constants.ISSUE_US: SenateCandidate,
    oe_constants.ISSUE_GSC: Candidate,
    oe_constants.ISSUE_EXEC: ExecutiveSlate,
    oe_constants.ISSUE_CLASSPRES: ClassPresidentSlate,
    oe_constants.ISSUE_SPECFEE: SpecialFeeRequest,
    
    # SMSA
    #oe_constants.ISSUE_SMSA_SCHOOLWIDE_OFFICE: Candidate,
    #oe_constants.ISSUE_SMSA_CLASS_REP: Candidate,
    #oe_constants.ISSUE_SMSA_CLASS_SOCIAL_CHAIR: Candidate,
    #oe_constants.ISSUE_SMSA_CCAP_REP: Candidate,
}