from common.utils import generate_choices

ACCOUNT_STATUS = ['open', 'closed', 'frozen']
ACCOUNT_TYPES = ['company', 'user']


ACCOUNT_STATUS_CHOICES = generate_choices(ACCOUNT_STATUS)
