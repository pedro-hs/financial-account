from django.contrib import admin

from .models import CompanyAccount, PersonAccount

MODELS = (CompanyAccount, PersonAccount)

for model in MODELS:
    admin.site.register(model)
