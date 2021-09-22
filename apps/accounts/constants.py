from common.utils import generate_choices

ACCOUNT_STATUS = ('open', 'closed', 'frozen')
ACCOUNT_TYPES = ('company', 'user')
ACCOUNT_FIELDS = ('number', 'digit', 'agency', 'status', 'credit_limit',
                  'credit_outlay', 'credit_expires', 'withdrawal_limit', 'balance')
ACCOUNT_READONLY_FIELDS = ('number', 'digit', 'agency', 'balance', 'credit_expires', 'credit_outlay')


ACCOUNT_STATUS_CHOICES = generate_choices(ACCOUNT_STATUS)
