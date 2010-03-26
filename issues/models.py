from django.db import models
from django.db.models import Q
import simplejson
from openelections import constants as oe_constants
from openelections.issues.text import POSITION_DESCRIPTIONS

ELECTORATES = {
    'undergrad': 'Undergrad',
    'grad': 'Grad',
    'coterm': 'Coterm',
    'undergrad-freshman': 'Freshman',
    'undergrad-sophomore': 'Sophomore',
    'undergrad-junior': 'Junior',
    'undergrad-senior': 'Senior',
    
    # GSC
    'gsb': 'School of Business',
    'earthsci': 'School of Earth Sciences',
    'edu': 'School of Education',
    'eng': 'School of Engineering',
    'humsci-hum': 'School of Humanities and Sciences, Humanities',
    'humsci-natsci': 'School of Humanities and Sciences, Natural Sciences',
    'humsci-socsci': 'School of Humanities and Sciences, Social Sciences',
    'law': 'School of Law',
    'med': 'School of Medicine',
    'gsc-atlarge': 'At-Large',
    
    # SMSA
    'smsa-2': 'SMSA 2nd Year', 
    'smsa-3': 'SMSA 3rd Year', 
    'smsa-4': 'SMSA 4th Year', 
    'smsa-5plus': 'SMSA 5th-Plus Year',
    'smsa-preclinical': 'SMSA Pre-clinical',
    'smsa-clinical': 'SMSA Clinical', 
    'smsa-mdphd': 'SMSA MD-PhD',
}

UNDERGRAD_CLASS_YEARS = ('undergrad-sophomore', 'undergrad-junior', 'undergrad-senior')
ASSU_POPULATIONS_ALL = ('undergrad', 'coterm', 'grad')
SMSA_CLASS_YEARS = ('smsa-2', 'smsa-3', 'smsa-4', 'smsa-5plus')
SMSA_POPULATIONS = ('smsa-preclinical', 'smsa-clinical', 'smsa-mdphd')
GSC_DISTRICTS = ('gsb', 'earthsci', 'edu', 'eng', 'humsci-hum', 'humsci-natsci', 'humsci-socsci', 'law', 'med', 'gsc-atlarge')

def no_smsa(s):
    return str(s).replace('SMSA ', '')

class Electorate(models.Model):
    name = models.CharField(max_length=64)
    
    @classmethod
    def queryset_with_names(klass, names):
        full_names = [ELECTORATES[name] for name in names]
        return klass.objects.filter(name__in=full_names)
    
    @classmethod
    def undergrad_class_years(klass):
        return klass.queryset_with_names(UNDERGRAD_CLASS_YEARS)
    
    @classmethod
    def assu_populations_all(klass):
        return klass.queryset_with_names(ASSU_POPULATIONS_ALL)
    
    @classmethod
    def smsa_class_years(klass):
        return klass.queryset_with_names(SMSA_CLASS_YEARS)
        
    @classmethod
    def smsa_populations(klass):
        return klass.queryset_with_names(SMSA_POPULATIONS)
        
    @classmethod
    def gsc_districts(klass):
        return klass.queryset_with_names(GSC_DISTRICTS)
    
    def __unicode__(self):
        return self.name

class Issue(models.Model):        
    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=64, choices=oe_constants.ISSUE_TYPES)
    statement = models.TextField(default='', blank=True)
    statement_short = models.TextField(default='', blank=True)
    statement_petition = models.TextField(default='', blank=True)
    image = models.ImageField(upload_to='media/issue_images', blank=True)
    slug = models.SlugField(blank=False)
    
    # whether the issue should be shown in the public list of petitions, issues, etc.
    public = models.BooleanField(default=True)
    
    # petition
    petition_validated = models.BooleanField(default=False)
    petition_signatures_count = models.IntegerField(default=0)
    
    received_declaration = models.BooleanField(default=False)
    signed_voterguide_agreement = models.BooleanField(default=True)
    
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
    budget = models.FileField(upload_to='media/specialfees', blank=True)
    past_budget = models.FileField(upload_to='media/specialfees', blank=True)
    account_statement = models.FileField(upload_to='media/specialfees', blank=True)
    total_request_amount = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    total_past_request_amount = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    budget_summary = models.TextField(blank=True)
    petition_budget_summary = models.TextField(blank=True)
    
    def __unicode__(self):
        return "%s: %s" % (self.kind, self.title)

    def can_declare(self):
        return False
    
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
            
    def candidate_electorates(self):
        if not hasattr(self, 'candidate_electorate_names'):
            return None
        names = self.candidate_electorate_names()
        if names:
            return Electorate.queryset_with_names(names)
        else:
            return None
    
    def petition_electorate_names(self):
        raise NotImplementedError
    
    def needs_petition(self):
        return False
    
    def petition_open(self):
        return False
        
    def show_petition_results(self):
        return False
    
    def statement_is_public(self):
        return True
        
    def position_description(self):
        return POSITION_DESCRIPTIONS.get(self.kind, None)
    
    def noun(self):
        raise NotImplementedError
    
    def kind_name(self):
        return "Generic issue"
    
    def name_and_office(self):
        return "Generic issue"
        
    def sunetids(self):
        """Returns the SUNet IDs associated with this issue, such as 
        the candidate's, the slate members', the sponsor's, etc.
        >>> issue = Issue(sunetid1='jsmith', sunetid2='aliceb')
        >>> issue.sunetids()
        ['jsmith', 'aliceb']
        """
        
        ids = (self.sunetid1, self.sunetid2, self.sunetid3,
               self.sunetid4, self.sunetid5)
        return [s for s in ids if s]
        
    def sunetid_can_manage(self, sunetid):
        admins = ('sqs', 'cotism2', 'aneeshka', 'mtvand2')
        return sunetid in self.sunetids() or sunetid in admins
    
    def partial_template(self):
        '''Returns the name of the partial template that should be used
        to render this issue in views, relative to the templates/ dir.'''
        return "issues/partials/issue.html"
    
    @classmethod
    def filter_by_kinds(klass, kinds):
        '''Returns all Issues whose kind is one of those in +kinds+, a list
        of strings.'''
        return klass.objects.filter(kind__in=kinds)
    
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
        
    def noun(self):
        return "candidate"

class FeeRequest(Issue):
    class Meta:
        proxy = True
    
    def noun(self):
        return "group" # e.g., Special Fee "group"
        
class SpecialFeeRequest(FeeRequest):
    class Meta:
        proxy = True
    
    def petition_electorates(self):
        return self.electorate
    
    def kind_name(self):
        return "Special Fee group"
        
    def statement_is_public(self):
        return False
        
    def elected_name(self):
        return "Special Fees"
    
    def name_and_office(self):
        return "a Special Fee request from %s" % self.title
        
    def partial_template(self):
        return "issues/partials/special-fee-request.html"

class Slate(Issue):
    class Meta:
        proxy = True
        
    def kind_name(self):
        return "slate"
        
    def noun(self):
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

class GSCCandidate(Candidate):
    class Meta:
        proxy = True
    
    def can_declare(self):
        return True
    
    def district(self):
        district_names = Electorate.gsc_districts()
        district_names = [d.name for d in district_names]
        districts = self.electorate.filter(name__in=district_names)
        if not districts:
            raise Exception('no district found for GSC candidate %d' % self.pk)
        return districts[0]
    
    def needs_petition(self):
        return False
    
    def kind_name(self):
        if self.pk:
            return "Grad Student Council (%s District) candidate" % self.district().name
        else:
            # if we haven't saved this, we don't know what district -- so be general
            return "Grad Student Council candidate"
        
    def elected_name(self):
        return "Grad Student Council rep"
    
    def name_and_office(self):
        return "%s, a candidate for ASSU Grad Student Council, %s District" % (self.name1, self.district().name)

class SMSACandidate(Candidate):
    class Meta:
        proxy = True

    def can_declare(self):
        return True
     
    def candidate_electorate_label(self):
        return None
    
    def candidate_electorate_names(self):
        return None
    
    def needs_petition(self):
        return False
        
    def statement_is_public(self):
        return True
    
    def kind_name(self):
        return "%s candidate" % self.elected_name()
    
    def name_and_office(self):
        return "%s, a candidate for %s" % (self.name1, self.elected_name())
    
    def elected_name(self):
        name_map = {
            'SMSA-ExecP': 'Executive President',
            'SMSA-P': 'President',
            'SMSA-VP': 'Vice President',
            'SMSA-S': 'Secretary',
            'SMSA-T': 'Treasurer',
            'SMSA-MC': 'Mentorship Chair',
            'SMSA-PSRC': 'Prospective Student Recruitment Chair',
            'SMSA-OSS-OSR': 'OSS/OSR Rep',
            'SMSA-CSAC': 'Clinical Student Advisory Council Member',
        }
        return 'SMSA ' + name_map.get(self.kind, 'Unknown')

class SMSAClassRepCandidate(SMSACandidate):
    class Meta:
        proxy = True
      
    def candidate_electorate_label(self):
        return 'SMSA class year'
    
    def candidate_electorate_names(self):
        return SMSA_CLASS_YEARS
    
    def class_year(self):
        class_years = Electorate.smsa_class_years()
        class_years = [cy.name for cy in class_years]
        year = self.electorate.filter(name__in=class_years)
        if not year:
            raise Exception('no year found for smsa class rep %d' % self.pk)
        return year[0]
        
    def elected_name(self):
        if self.pk:
            return "%s Class Rep" % self.class_year()
        else:
            return "Class Rep"
        
class SMSASocialChairCandidate(SMSACandidate):
    class Meta:
        proxy = True

    def candidate_electorate_label(self):
        return 'SMSA population'
    
    def candidate_electorate_names(self):
        return ('smsa-preclinical', 'smsa-clinical')
    
    def population(self):
        pops = Electorate.smsa_populations()
        pops = [p.name for p in pops]
        pop = self.electorate.filter(name__in=pops)
        if not pop:
            raise Exception('no pop found for smsa social chair %d' % self.pk)
        return pop[0]
    
    def elected_name(self):
        if self.pk:
            return "SMSA Social Chair (%s)" % no_smsa(self.population())
        else:
            return "SMSA Social Chair"
        
class SMSACCAPRepCandidate(SMSACandidate):
    class Meta:
        proxy = True

    def candidate_electorate_label(self):
        return 'SMSA population'
    
    def candidate_electorate_names(self):
        return ('smsa-preclinical', 'smsa-clinical', 'smsa-mdphd')
    
    def population(self):
        pops = Electorate.smsa_populations()
        pops = [p.name for p in pops]
        pop = self.electorate.filter(name__in=pops)
        if not pop:
            raise Exception('no pop found for smsa ccap rep %d' % self.pk)
        return pop[0]
    
    def elected_name(self):
        if self.pk:
            return "SMSA CCAP Rep (%s)" % no_smsa(self.population())
        else:
            return "SMSA CCAP Rep"

class SMSAPolicyAndAdvocacyChairCandidate(SMSACandidate):
    class Meta:
        proxy = True
        
    def candidate_electorate_label(self):
        return 'SMSA population'
    
    def candidate_electorate_names(self):
        return ('smsa-preclinical', 'smsa-clinical')
        
    def population(self):
        pops = Electorate.smsa_populations()
        pops = [p.name for p in pops]
        pop = self.electorate.filter(name__in=pops)
        if not pop:
            raise Exception('no pop found for smsa p and a rep %d' % self.pk)
        return pop[0]
    
    def elected_name(self):
        if self.pk:
            return "SMSA Policy and Advocacy Chair (%s)" % no_smsa(self.population())
        else:
            return "SMSA Policy and Advocacy Chair"
        

###############
# Class map
###############
kinds_classes = {
    oe_constants.ISSUE_US: SenateCandidate,
    oe_constants.ISSUE_GSC: GSCCandidate,
    oe_constants.ISSUE_EXEC: ExecutiveSlate,
    oe_constants.ISSUE_CLASSPRES: ClassPresidentSlate,
    oe_constants.ISSUE_SPECFEE: SpecialFeeRequest,
    
    # SMSA
    'SMSA-ExecP': SMSACandidate,
    'SMSA-P': SMSACandidate,
    'SMSA-VP': SMSACandidate,
    'SMSA-S': SMSACandidate,
    'SMSA-T': SMSACandidate,
    'SMSA-ClassRep': SMSAClassRepCandidate,
    'SMSA-SocChair': SMSASocialChairCandidate,
    'SMSA-CCAP': SMSACCAPRepCandidate,
    'SMSA-PAC': SMSAPolicyAndAdvocacyChairCandidate,
    'SMSA-MC': SMSACandidate,
    'SMSA-PSRC': SMSACandidate,
    'SMSA-OSS-OSR': SMSACandidate,
    'SMSA-CSAC': SMSACandidate,
}
