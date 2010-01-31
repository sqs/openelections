from django.db import models
from openelections.constants import ENROLLMENT_STATUSES
from openelections.issues.models import Issue

class Vote(models.Model):
    voter_id = models.CharField(max_length=64)
    voter_type = models.CharField(max_length=1, choices=ENROLLMENT_STATUSES)
    issue = models.ForeignKey(Issue, related_name='votes')
    preference_rank = models.SmallIntegerField()
    write_in = models.CharField(max_length=100)
