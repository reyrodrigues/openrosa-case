import os

from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password

from . import models


# Register your models here.

class CaseDisplayItemInline(admin.TabularInline):
    model = models.ModuleDisplayItem


class FormCaseMappingAdmin(admin.TabularInline):
    model = models.FormCaseMapping


class ModuleAdmin(admin.ModelAdmin):
    inlines = [
        CaseDisplayItemInline,
    ]


class FormCaseAdmin(admin.ModelAdmin):
    inlines = [
        FormCaseMappingAdmin,
    ]


class ApplicationUserForm(forms.ModelForm):
    exclude = ()

    def clean_password(self):
        salt = os.urandom(5).encode('hex')
        password = make_password(self.cleaned_data['password'], salt=salt,
                                 hasher='sha1')

        return password

    class Meta:
        model = models.ApplicationUser


class ApplicationUserAdmin(admin.ModelAdmin):
    form = ApplicationUserForm


admin.site.register(models.Module, ModuleAdmin)
admin.site.register(models.Application, admin.ModelAdmin)
admin.site.register(models.ApplicationGroup, admin.ModelAdmin)
admin.site.register(models.ApplicationUser, ApplicationUserAdmin)
admin.site.register(models.Form, admin.ModelAdmin)
admin.site.register(models.FormCase, FormCaseAdmin)
