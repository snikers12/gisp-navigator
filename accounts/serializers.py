from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from pictures.models import Picture
from pictures.serializers import InlinePictureSerializer

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    photo = InlinePictureSerializer(read_only=True)
    photo_id = serializers.PrimaryKeyRelatedField(queryset=Picture.objects.all(), source='photo',
                                                  required=False, allow_null=True)
    phone = PhoneNumberField(required=True, allow_blank=False, allow_null=False)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'photo',
            'photo_id',
            'groups',
            'phone',
            'birth_date'
        ]

    def validate_phone(self, phone):
        users = User.objects.filter(phone=phone)
        if not self.instance:
            if users.count() > 0:
                raise ValidationError('На этот номер уже зарегистрирован другой пользователь')
            else:
                return phone
        else:
            if users.exclude(id=self.instance.id).count() > 0:
                raise ValidationError('На этот номер уже зарегистрирован другой пользователь')
            else:
                return phone


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = None
        exclude = ['user_permissions']

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, password):
        validate_password(password)
        return password

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # Null out the username to let the Volunteer.save()
        # refresh it from the new first/last names.
        if not attrs.get('username'):
            attrs['username'] = ""

        return attrs

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(raw_password)
        if not validated_data['username']:
            user.username = validated_data['email'].split('@')[0]
        user.save()
        return user


class UserLightSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email'
        )
