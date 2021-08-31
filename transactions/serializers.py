
from rest_framework import serializers

from .models import CompanyTransaction, PersonTransaction


class CompanyTransactionSerializer(serializers.ModelSerializer):
    number = serializers.CharField()
    digit = serializers.CharField()
    agency = serializers.CharField()
    owner_id = serializers.CharField()

    class Meta:
        model = CompanyTransaction
        fields = ('transaction_type', 'amount', 'number', 'digit', 'agency', 'owner_id')


class ListCompanyTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyTransaction
        fields = '__all__'


class PersonTransactionSerializer(serializers.ModelSerializer):
    number = serializers.CharField()
    digit = serializers.CharField()
    agency = serializers.CharField()
    owner_id = serializers.CharField()

    class Meta:
        model = PersonTransaction
        fields = ('transaction_type', 'amount', 'number', 'digit', 'agency', 'owner_id')


class ListPersonTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonTransaction
        fields = '__all__'
