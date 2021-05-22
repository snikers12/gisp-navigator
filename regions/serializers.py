from rest_framework import serializers
from rest_framework_gis.fields import GeometrySerializerMethodField

from .models import FederalSubjectType, FederalSubject, FederalSubjectWithPolygon, FederalDistrict


class FederalSubjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FederalSubjectType
        fields = ('full_name', 'short_name')


class FederalSubjectSerializer(serializers.ModelSerializer):
    federal_subject_type = FederalSubjectTypeSerializer()

    # timezones is a json:
    # [{timezone: 'Europe/Moscow', title: 'видимое в интерфейсе название: Московское время'}, ...]

    class Meta:
        model = FederalSubject
        fields = ('id', 'name', 'federal_subject_type', 'federal_subject_type_position',
                  'full_pretty_name', 'timezones', 'kladr_id')


class FederalSubjectWithPolygonSerializer(FederalSubjectSerializer):
    center = GeometrySerializerMethodField()

    def get_center(self, obj):
        return obj.center or obj.polygon_location.point_on_surface

    class Meta:
        model = FederalSubjectWithPolygon
        fields = FederalSubjectSerializer.Meta.fields + ('center', 'polygon_location',)


class FederalDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = FederalDistrict
        fields = '__all__'
