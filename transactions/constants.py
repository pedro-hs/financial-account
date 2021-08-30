TRANSACTION_TYPES = ['deposit', 'withdrawal', 'buy_credit', 'pay_credit']
TRANSACTION_STATUS = ['done', 'canceled']
CANCELED_REASONS = ['insufficient_fund', 'limit', 'frozen', 'debtor', 'invalid_enum']


def generate_choices(data):
    return[(item, item) for item in data]


CANCELED_REASONS_CHOICES = generate_choices(CANCELED_REASONS)
TRANSACTION_TYPES_CHOICES = generate_choices(TRANSACTION_TYPES)
TRANSACTION_STATUS_CHOICES = generate_choices(TRANSACTION_STATUS)
