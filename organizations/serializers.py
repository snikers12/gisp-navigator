from rest_framework import serializers

from organizations.models import SupportMeasures


class SupportMeasuresListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMeasures
        fields = ('id', 'kbk', 'name', 'is_federal', 'support_type')


class SupportMeasuresSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMeasures
        fields = '__all__'
