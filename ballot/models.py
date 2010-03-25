from django.db import models
from openelections.issues.models import Issue, Electorate

class Vote(models.Model):
    voter_id = models.CharField(max_length=64)
    electorate = models.ForeignKey(Electorate)
    issue = models.ForeignKey(Issue, related_name='votes', blank=True)
    preference_rank = models.SmallIntegerField(default=1)
    write_in = models.CharField(max_length=100, blank=True)
