from rest_framework import serializers


from regions.models import FederalSubjectType, FederalSubject


class OpenApiFederalSubjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FederalSubjectType
        fields = ('full_name', 'short_name')


class OpenApiFederalSubjectSerializer(serializers.ModelSerializer):
    federal_subject_type = OpenApiFederalSubjectTypeSerializer()

    # timezones is a json:
    # [{timezone: 'Europe/Moscow', title: 'видимое в интерфейсе название: Московское время'}, ...]

    class Meta:
        model = FederalSubject
        fields = ('id', 'name', 'federal_subject_type', 'federal_subject_type_position',
                  'full_pretty_name', 'timezones')
