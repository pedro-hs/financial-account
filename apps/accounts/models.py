from datetime import date, timedelta
from random import randint

from common.validators import IS_NUMERIC
from django.core.validators import MinLengthValidator
from django.db import models

from apps.company.models import Company
from apps.users.models import User

from .constants import ACCOUNT_STATUS_CHOICES


class BaseAccount(models.Model):
    number = models.CharField(primary_key=True, unique=True, max_length=11, default=str(randint(1111, 99999999999)),
                              validators=[IS_NUMERIC, MinLengthValidator(4)])
    digit = models.CharField(max_length=1, validators=[IS_NUMERIC, MinLengthValidator(1)])
    agency = models.CharField(max_length=4, validators=[IS_NUMERIC, MinLengthValidator(2)])
    status = models.CharField(default='open', choices=ACCOUNT_STATUS_CHOICES, max_length=20)
    credit_limit = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    credit_outlay = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    credit_expires = models.DateField(default=date.today() + timedelta(days=30))
    withdrawal_limit = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    balance = models.DecimalField(default=0, max_digits=12, decimal_places=2)

    class Meta:
        abstract = True


class CompanyAccount(BaseAccount):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        db_table = 'company_account'
        verbose_name = 'Company Account'
        verbose_name_plural = 'Companies Account'

    def __str__(self):
        return f'CPF: {self.company.cnpj} | NUMBER: {self.number} | DIGIT: {self.digit} | AGENCY: {self.agency}'


class PersonAccount(BaseAccount):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'person_account'
        verbose_name = 'Person Account'
        verbose_name_plural = 'Persons Account'

    def __str__(self):
        return f'CPF: {self.user.cpf} | NUMBER: {self.number} | DIGIT: {self.digit} | AGENCY: {self.agency}'
