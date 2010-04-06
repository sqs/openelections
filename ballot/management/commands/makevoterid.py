import re, csv, os
from django.core.management.base import LabelCommand
from openelections.ballot.models import make_voter_id

class Command(LabelCommand):
    def handle_label(self, label, **options):
        return make_voter_id(label)