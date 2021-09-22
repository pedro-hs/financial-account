from rest_framework import serializers

from .constants import ACCOUNT_FIELDS, ACCOUNT_READONLY_FIELDS
from .models import Company, CompanyAccount, PersonAccount


class DefaultPersonAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonAccount
        fields = ('user', *ACCOUNT_FIELDS)
        read_only_fields = ('user', *ACCOUNT_READONLY_FIELDS)


class PostPersonAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonAccount
        fields = '__all__'


class DefaultCompanyAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyAccount
        fields = ('company', *ACCOUNT_FIELDS)
        read_only_fields = ('company', *ACCOUNT_READONLY_FIELDS)


class PostCompanyAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyAccount
        fields = '__all__'
