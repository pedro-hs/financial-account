from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('cpf', 'email', 'full_name', 'password', 'is_active', 'is_staff', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        request = self.context.get('request', None)

        if request and getattr(request, 'method', None) == "PUT":
            for key, _ in dict(fields).items():
                fields[key].required = False

        return fields

    def validate(self, data):
        if not data:
            raise serializers.ValidationError('Body cannot be empty')

        self.__validate_unknown_fields()
        return data

    def validate_full_name(self, value):
        if isinstance(value, str) and value.replace(' ', '').isalpha() and len(value) > 3:
            return value

        raise serializers.ValidationError('Invalid name')

    def validate_password(self, value):
        if not self.context['request'].method == 'PUT':
            return validate_password(value)

        raise serializers.ValidationError('Cannot update password')

    def validate_cpf(self, value):
        if not self.context['request'].method == 'PUT':
            return self.__validate_numeric(value, 'cpf', len(value) == 11)

        raise serializers.ValidationError('Cannot update cpf')

    def __validate_numeric(self, value, field_name, valid_length):
        if isinstance(value, str) and value.isnumeric() and valid_length:
            return str(int(value))

        raise serializers.ValidationError(f'Invalid {field_name}')

    def __validate_unknown_fields(self):
        unknown = set(self.initial_data.keys()) - set(self.fields)

        if unknown:
            raise serializers.ValidationError("Unknown field(s): {}".format(", ".join(unknown)))
