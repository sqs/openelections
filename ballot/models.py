from django.db import models
from openelections.issues.models import Issue, Electorate

class Vote(models.Model):
    voter_id = models.CharField(max_length=64)
    electorate = models.ForeignKey(Electorate)
    issue = models.ForeignKey(Issue, related_name='votes')
    preference_rank = models.SmallIntegerField()
    write_in = models.CharField(max_length=100)
