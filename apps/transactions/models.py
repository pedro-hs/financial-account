from uuid import uuid4

from django.db import models

from apps.accounts.models import CompanyAccount, PersonAccount

from .constants import (CANCELED_REASONS_CHOICES, TRANSACTION_STATUS_CHOICES,
                        TRANSACTION_TYPES_CHOICES)


class BaseTransaction(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=36)
    transaction_type = models.CharField(choices=TRANSACTION_TYPES_CHOICES, max_length=20)
    status = models.CharField(choices=TRANSACTION_STATUS_CHOICES, max_length=20)
    amount = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    canceled_reason = models.CharField(null=True, choices=CANCELED_REASONS_CHOICES, max_length=20)
    note = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class PersonTransaction(BaseTransaction):
    account = models.ForeignKey(PersonAccount, on_delete=models.CASCADE)

    class Meta:
        db_table = 'person_transaction'
        verbose_name = 'Person Transaction'
        verbose_name_plural = 'Persons Transaction'

    def __str__(self):
        return (f'CPF: {self.account.user.cpf} | NUMBER: {self.account.number}'
                f' | DIGIT: {self.account.digit} | AGENCY: {self.account.agency}')


class CompanyTransaction(BaseTransaction):
    account = models.ForeignKey(CompanyAccount, on_delete=models.CASCADE)

    class Meta:
        db_table = 'company_transaction'
        verbose_name = 'Company Transaction'
        verbose_name_plural = 'Companies Transaction'

    def __str__(self):
        return (f'CPF: {self.account.company.cnpj} | NUMBER: {self.account.number}'
                f' | DIGIT: {self.account.digit} | AGENCY: {self.account.agency}')
