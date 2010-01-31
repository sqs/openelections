from openelections.issues.models import Issue
from django.contrib import admin

class IssueAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ('title', 'kind')}),
        ('Profile', {'fields': ('profile', 'summary', 'image', 'slug')}),
        ('Person 1', {'fields': ('name1', 'sunetid1', 'studentid1',)}),
        ('People 2-5', {'classes': ('_collapse',),
                        'fields': ('name2', 'sunetid2', 'studentid2',
                                   'name3', 'sunetid3', 'studentid3',
                                   'name4', 'sunetid4', 'studentid4',
                                   'name5', 'sunetid5', 'studentid5')}),
        ('Class year/GSC district/etc.', {'classes': ('_collapse',), 'fields': ('class_year', 'district')}),
        ('Special Fee group', {'classes': ('_collapse',), 'fields': ('budget', 'budget_summary')}),
    ]
    prepopulated_fields = {'slug': ('title',)}
    save_on_top = True

admin.site.register(Issue, IssueAdmin)