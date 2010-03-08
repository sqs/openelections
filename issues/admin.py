from openelections.issues.models import Electorate, Issue
from django.contrib import admin

admin.site.register(Electorate)

def issue_num_signatures(issue):
    return issue.signatures.count()
issue_num_signatures.short_description = '# signatures (unverified)'

def issue_members(issue):
    m = ((issue.sunetid1, issue.name1), (issue.sunetid2, issue.name2), (issue.sunetid3, issue.name3), 
         (issue.sunetid4, issue.name4), (issue.sunetid5, issue.name5))
    return ', '.join(['%s (%s)' % (s,n) for (s,n) in m if s])
issue_members.short_description = 'Candidate/members/sponsors'      

class IssueAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ('title', 'kind')}),
        ('Profile', {'fields': ('bio', 'bio_petition', 'image', 'slug', 'public')}),
        ('Electorate', {'fields': ('electorate',)}),
        ('Person 1', {'fields': ('name1', 'sunetid1',)}),
        ('People 2-5', {'classes': ('collapse',),
                        'fields': ('name2', 'sunetid2',
                                   'name3', 'sunetid3',
                                   'name4', 'sunetid4',
                                   'name5', 'sunetid5',)}),
        ('Petition', {'classes': ('collapse',),
                      'fields': ('petition_validated', 'petition_signatures_count')}),
        ('Special Fee group', {'classes': ('collapse',), 'fields': ('budget', 'budget_summary')}),
    ]
    prepopulated_fields = {'slug': ('title',)}
    save_on_top = True
    list_display = ('title', 'kind', issue_members, issue_num_signatures, 'petition_validated')

admin.site.register(Issue, IssueAdmin)
