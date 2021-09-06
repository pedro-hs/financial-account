import logging
from datetime import timedelta

from apps.transactions.executor.transaction import Transaction


class PayCreditTransaction(Transaction):
    def __init__(self, account, amount, transaction_type, account_type):
        super().__init__(account, amount, transaction_type, account_type)
        self.balance = self.account_instance.balance
        self.credit_outlay = self.account_instance.credit_outlay
        self.credit_expires = self.account_instance.credit_expires
        self.credit_fees = self.calculate_credit_fees(self.credit_expires)

    def process(self):
        if not self.credit_outlay and not self.credit_fees:
            logging.info('PayCredit transaction canceled. Nothing to pay')
            return self.create({'status': 'canceled',
                                'canceled_reason': 'no_pay',
                                'note': 'Nothing to pay',
                                'transaction_type': self.transaction_type,
                                'amount': self.amount})

        if self.credit_fees:
            if self.amount < self.credit_fees:
                logging.info("PayCredit transaction canceled. Fees are pending and the amount can't pay the fees")
                return self.create({'status': 'canceled',
                                    'canceled_reason': 'insufficient_fund',
                                    'note': "Fees are pending and the amount can't pay the fees",
                                    'transaction_type': self.transaction_type,
                                    'amount': self.amount})
            self.pay_credit_fees(self.amount)

        else:
            self.pay_credit_outlay(self.amount)

        if not self.account_instance.credit_outlay:
            self.account_instance.credit_expires = self.credit_expires + timedelta(days=30)

        logging.info('PayCredit transaction done')
        return self.create({'status': 'done',
                            'transaction_type': self.transaction_type,
                            'amount': self.amount})

    def pay_credit_outlay(self, amount):
        if amount >= self.credit_outlay:
            chargeback = float(amount) - float(self.credit_outlay)
            self.account_instance.credit_outlay = 0

            if chargeback:
                self.account_instance.balance = float(self.balance) + float(chargeback)

        if amount < self.credit_outlay:
            self.account_instance.credit_outlay = float(self.credit_outlay) - float(amount)

    def pay_credit_fees(self, amount):
        if amount >= self.credit_fees:
            remaining = amount - self.credit_fees

            if remaining:
                self.pay_credit_outlay(remaining)