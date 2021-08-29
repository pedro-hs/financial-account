from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from users.models import User

IS_NUMERIC = RegexValidator(r'^[0-9+]', 'Only numeric characters.')

STATUS = [
    ('open', 'open'),
    ('closed', 'closed'),
    ('frozen', 'frozen'),
]


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
    number = models.CharField(primary_key=True, unique=True, max_length=11,
                              validators=[MinLengthValidator(4)])  # TODO: readonly (block update)
    digit = models.CharField(max_length=1, validators=[MinLengthValidator(1)])  # TODO: readonly (block update
    agency = models.CharField(max_length=4, validators=[MinLengthValidator(2)])  # TODO: readonly (block update
    status = models.CharField(default='open', choices=STATUS, max_length=20)
    credit_limit = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    credit_outlay = models.DecimalField(default=0, max_digits=12, decimal_places=2)
    credit_expires = models.DateField()
    withdraw_limit = models.DecimalField(default=0, max_digits=12, decimal_places=2)
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
