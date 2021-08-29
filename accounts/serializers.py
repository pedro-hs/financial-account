
from rest_framework import serializers

from .models import Company, PersonAccount


class PersonAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonAccount
        fields = ('user', 'number', 'digit', 'agency', 'status', 'credit_limit',
                  'credit_outlay', 'credit_expires', 'withdraw_limit', 'balance')


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('user', 'cnpj', 'trademark')
