import re, csv, os
from django.core.management.base import LabelCommand
from openelections.ballot.models import Ballot

default_electorates = 'assu'
elecmap = {
    'H&S': 'gsc-hs',
    'Medicine': 'gsc-med,smsa',
    'Engineer': 'gsc-eng',
    'EarthSci': 'gsc-earthsci',
    'Law': 'gsc-law',
    'Education': 'gsc-edu',
    'GSB': 'gsc-gsb',
    '1- Undergraduate Student': 'undergrad',
    '2 - Coterm': 'coterm',
    '3 - Graduate Student': 'graduate',
    'frosh admit': '',
    'transfer admit': '',
    '5 - Fifth year or more Senior': 'undergrad-5plus',
    '4 - Senior Class Affiliation': 'undergrad-5plus',
    '3 - Junior Class Affiliation': 'undergrad-4',
    '2 - Sophomore Class Affiliation': 'undergrad-3',
    '1 - Freshman Class Affiliation': 'undergrad-2',
}

def get_ballot(sunetid, erase_elec=False):
    b, created = Ballot.get_or_create_by_sunetid(sunetid)
    if erase_elec or not b.electorates:
        b.electorates = default_electorates
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
            b = get_ballot(sunetid, erase_elec=True)
            groups = map(str.strip, row['Class Level '].split(','))
            for g in groups:
                elec = elecmap[g]
                b.electorates += ',' + elec
            print "%s\t%s" % (sunetid, b.electorates)
            b.save()
        
        for row in grad:
            sunetid = row['SUNet ID']
            b = get_ballot(sunetid)
            
            groups = map(str.strip, row['Class Level '].split(','))
            for g in groups:
                if not g: continue
                elec = elecmap[g]
                b.electorates += ',' + elec
                
            school = row['School']
            b.electorates += ',' + elecmap[school]
            
            print "%s:\t%s" % (voter_id, b.electorates)
            b.save()