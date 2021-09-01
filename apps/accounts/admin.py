from django.contrib import admin

from .models import Company, CompanyAccount, PersonAccount

MODELS = [Company, CompanyAccount, PersonAccount]

for model in MODELS:
    admin.site.register(model)
