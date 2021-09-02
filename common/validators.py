from django.core.validators import RegexValidator

IS_NUMERIC = RegexValidator(r'^[0-9+]', 'Only numeric characters.')
