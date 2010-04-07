from openelections.ballot.models import Ballot
from django.contrib import admin

class BallotAdmin(admin.ModelAdmin):
    save_on_top = True

admin.site.register(Ballot, BallotAdmin)
