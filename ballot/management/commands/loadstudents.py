import re, csv, os
from django.core.management.base import LabelCommand
from openelections.ballot.models import Ballot
from openelections.ballot.tests import elec

gsc_districts = {
    #'H&S': 'gsc-hs',
    'Medicine': 'gsc-med',
    'Engineer': 'gsc-eng',
    'EarthSci': 'gsc-earthsci',
    'Law': 'gsc-law',
    'Education': 'gsc-edu',
    'GSB': 'gsc-gsb',
}
assu_pops = {
    '1- Undergraduate Student': ['undergrad'],
    '2 - Coterm': ['undergrad','graduate'],
    '3 - Graduate Student': ['graduate'],
}
class_years = {
    '5 - Fifth year or more Senior': 'undergrad-5plus',
    '4 - Senior Class Affiliation': 'undergrad-5plus',
    '3 - Junior Class Affiliation': 'undergrad-4',
    '2 - Sophomore Class Affiliation': 'undergrad-3',
    '1 - Freshman Class Affiliation': 'undergrad-2',
}

def get_ballot(sunetid):
    b, created = Ballot.get_or_create_by_sunetid(sunetid)
    return b

class Command(LabelCommand):
    def handle_label(self, label, **options):
        output = []
        
        undergrad_path = os.path.join(label, 'undergrad.csv')
        undergrad = csv.DictReader(open(undergrad_path))
        grad_path = os.path.join(label, 'grad.csv')
        grad = csv.DictReader(open(grad_path))
        smsa_path = os.path.join(label, 'smsa.csv')
        smsa = csv.DictReader(open(smsa_path))
        
    
        for row in undergrad:
            sunetid = row['SUNet ID']
            b = get_ballot(sunetid)
            groups = map(str.strip, row['Class Level '].split(','))
            for g in groups:
                if g in assu_pops:
                    b.assu_populations = map(elec, assu_pops[g])
                if g in class_years:
                    b.undergrad_class_year = elec(class_years[g])
            print "%s\t%s" % (sunetid, b)
            b.save()

        did_set_gsc_districts_for_sunet_ids = set()
        for row in grad:
            sunetid = row['SUNet ID']
            b = get_ballot(sunetid)

            groups = map(str.strip, row['Class Level '].split(',')) + map(str.strip, row['School'].split(','))
            for g in groups:
                if g in assu_pops:
                    b.assu_populations = map(elec, assu_pops[g])
                if g in gsc_districts:
                    # if multiple GSC districts, erase all and force them to choose
                    if sunetid in did_set_gsc_districts_for_sunet_ids:
                        b.gsc_district = None
                    else:
                        b.gsc_district = elec(gsc_districts[g])
                        did_set_gsc_districts_for_sunet_ids.add(sunetid)

            print "%s\t%s" % (sunetid, b)
            b.save()
