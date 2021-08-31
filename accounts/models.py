from datetime import date
from random import randint

from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from users.models import User

from .constants import ACCOUNT_STATUS_CHOICES

IS_NUMERIC = RegexValidator(r'^[0-9+]', 'Only numeric characters.')


class Company(models.Model):
    cnpj = models.CharField(primary_key=True, max_length=14, unique=True,
                            validators=[IS_NUMERIC, MinLengthValidator(14)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trademark = models.CharField(max_length=256)

    class Meta:
        db_table = 'company'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.cnpj


class BaseAccount(models.Model):
    number = models.CharField(primary_key=True, unique=True, max_length=11, default=str(randint(1111, 99999999999)),
                              validators=[MinLengthValidator(4)])
    digit = models.CharField(max_length=1, validators=[MinLengthValidator(1)])
    agency = models.CharField(max_length=4, validators=[MinLengthValidator(2)])
    status = models.CharField(default='open', choices=ACCOUNT_STATUS_CHOICES, max_length=20)
    credit_limit = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    credit_outlay = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    credit_expires = models.DateField()
    withdrawal_limit = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    balance = models.DecimalField(default=0, max_digits=12, decimal_places=2)

    @property
    def credit_fees(self):
        today = date.today()

        if self.credit_expires > today:
            fees = 40
            difference = self.credit_expires - today
            fees = fees * (1 + 60 / 100) ** (difference.days / 365)

            return fees

        return 0

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
