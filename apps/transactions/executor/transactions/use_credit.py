from apps.transactions.executor.transaction import Transaction


class UseCreditTransaction(Transaction):
    def process(self):
        credit_outlay = self.account_instance.credit_outlay
        self.credit_expires = self.account_instance.credit_expires
        self.credit_fees = self.calculate_credit_fees(self.credit_expires)

        if self.credit_fees:
            return self.create('canceled', self.amount, 'debitor',
                               'Is need to pay the credit outlay and fees in order to use credit again')

        if (credit_outlay + self.amount) > self.account_instance.credit_limit:
            return self.create('canceled', self.amount, 'limit', 'Limit of credit achieved')

        self.account_instance.credit_outlay = + self.amount

        return self.create('done', self.amount)
