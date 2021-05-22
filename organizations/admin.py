from django.contrib import admin

# Register your models here.
from organizations.models import (
    Subsidies, Organization, SupportMeasures, Okved, Branch, Tass, OrganizationSize
)


@admin.register(OrganizationSize)
class OrganizationSizeAdmin(admin.ModelAdmin):
    pass


@admin.register(Subsidies)
class SubsidiesAdmin(admin.ModelAdmin):
    pass


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_filter = ('branch', )


@admin.register(SupportMeasures)
class SupportMeasuresAdmin(admin.ModelAdmin):
    list_filter = ('is_active', )


@admin.register(Okved)
class OkvedAdmin(admin.ModelAdmin):
    pass


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    pass


@admin.register(Tass)
class TassAdmin(admin.ModelAdmin):
    pass
