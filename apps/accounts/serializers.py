
from rest_framework import serializers

from .models import Company, CompanyAccount, PersonAccount

ACCOUNT_FIELDS = ('number', 'digit', 'agency', 'status', 'credit_limit',
                  'credit_outlay', 'credit_expires', 'withdrawal_limit', 'balance')
ACCOUNT_READONLY_FIELDS = ('number', 'digit', 'agency', 'balance', 'credit_expires', 'credit_outlay')


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


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
