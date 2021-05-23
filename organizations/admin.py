from django.contrib import admin

# Register your models here.
from gisp.admin import SingletonAdmin
from organizations.models import (
    Subsidies, Organization, SupportMeasures, Okved, Branch, Tass, OrganizationSize,
    OrganizationCorrelation, Coefficients)


@admin.register(OrganizationSize)
class OrganizationSizeAdmin(admin.ModelAdmin):
    pass


@admin.register(Subsidies)
class SubsidiesAdmin(admin.ModelAdmin):
    raw_id_fields = ('support_measure', 'organization')


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_filter = ('branch', 'is_active')
    search_fields = ('inn', 'ogrn')


@admin.register(SupportMeasures)
class SupportMeasuresAdmin(admin.ModelAdmin):
    list_filter = ('is_active', )
    ordering = ('name', )


@admin.register(Okved)
class OkvedAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


@admin.register(Tass)
class TassAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


@admin.register(OrganizationCorrelation)
class OrganizationCorrelationAdmin(admin.ModelAdmin):
    list_display = ('org_1', 'org_2', 'correlation')
    search_fields = ('org_1__inn', 'org_2__inn')


@admin.register(Coefficients)
class CoefficientsPageAdmin(SingletonAdmin):
    pass
