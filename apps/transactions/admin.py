from django.contrib import admin

from .models import CompanyTransaction, PersonTransaction

MODELS = [CompanyTransaction, PersonTransaction]

for model in MODELS:
    admin.site.register(model)
