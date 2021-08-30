
from rest_framework import serializers

from .models import Company, PersonAccount


class PersonAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonAccount
        fields = ('user', 'number', 'digit', 'agency', 'status', 'credit_limit',
                  'credit_outlay', 'credit_expires', 'withdrawal_limit', 'balance', 'credit_fees')


class CompanyAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonAccount
        fields = ('company', 'number', 'digit', 'agency', 'status', 'credit_limit',
                  'credit_outlay', 'credit_expires', 'withdrawal_limit', 'balance', 'credit_fees')


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('user', 'cnpj', 'trademark')
