from common.validators import IS_NUMERIC
from django.core.validators import MinLengthValidator
from django.db import models

from apps.users.models import User


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
