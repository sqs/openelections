from openelections.petitions.models import Signature
from django.contrib import admin

class SignatureAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Signer', {'fields': ('name', 'sunetid', 'studentid', 'enrollment_status')}),
        ('Issue', {'fields': ('issue',)}),
    ]

admin.site.register(Signature, SignatureAdmin)