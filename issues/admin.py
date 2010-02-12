from openelections.issues.models import Electorate, Issue
from django.contrib import admin

admin.site.register(Electorate)

class IssueAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ('title', 'kind')}),
        ('Profile', {'fields': ('bio', 'bio_petition', 'image', 'slug')}),
        ('Electorate', {'fields': ('electorate',)}),
        ('Person 1', {'fields': ('name1', 'sunetid1',)}),
        ('People 2-5', {'classes': ('collapse',),
                        'fields': ('name2', 'sunetid2',
                                   'name3', 'sunetid3',
                                   'name4', 'sunetid4',
                                   'name5', 'sunetid5',)}),
        ('Special Fee group', {'classes': ('collapse',), 'fields': ('budget', 'budget_summary')}),
    ]
    prepopulated_fields = {'slug': ('title',)}
    save_on_top = True

admin.site.register(Issue, IssueAdmin)
