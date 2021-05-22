from rest_framework import serializers
from stdimage_serializer.fields import StdImageField

from .models import Picture


class PictureSerializer(serializers.ModelSerializer):
    image = StdImageField(validators=Picture._meta.get_field('image').validators[:])

    class Meta:
        model = Picture
        fields = '__all__'


class InlinePictureSerializer(serializers.ModelSerializer):
    image = StdImageField(read_only=True)

    class Meta:
        model = Picture
        fields = ('image',)

    def to_representation(self, instance):
        return self.fields['image'].to_representation(instance.image)
