from openelections.petitions.models import Signature
from django.contrib import admin

class SignatureAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Signer', {'fields': ('name', 'sunetid')}),
        ('Issue', {'fields': ('issue',)}),
    ]
    list_display = ('sunetid', 'name', 'electorate', 'issue', 'ip_address', 'signed_at')
    list_filter = ('issue', 'electorate')
    search_fields = ('sunetid', 'name')

admin.site.register(Signature, SignatureAdmin)