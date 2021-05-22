from django.contrib import admin

from regions.models import (
    FederalSubjectType, FederalSubject, FederalSubjectWithPolygon, FederalDistrict,
)


@admin.register(FederalSubjectType)
class FederalSubjectTypeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'short_name')


@admin.register(FederalSubject)
class FederalSubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'federal_subject_type', 'federal_subject_type_position',
                    'district', 'kladr_id', 'email')
    list_filter = ('district',)

    def get_queryset(self, request):
        return FederalSubject.admin_objects.all()


@admin.register(FederalSubjectWithPolygon)
class FederalSubjectWithPolygonAdmin(admin.ModelAdmin):
    list_display = ('name', 'federal_subject_type', 'federal_subject_type_position',
                    'kladr_id', 'email')


@admin.register(FederalDistrict)
class FederalDistrictAdmin(admin.ModelAdmin):
    list_display = ('name_short', 'name')
