from apps.transactions.executor.transaction import Transaction


class WithDrawalTransaction(Transaction):
    def process(self):
        balance = self.account_instance.balance

        if self.amount > balance:
            return self.create('canceled', self.amount, canceled_reason='insufficient_fund',
                               note='Fund is lower than balance')

        if self.amount > self.account_instance.withdrawal_limit:
            return self.create('canceled', self.amount, canceled_reason='limit',
                               note='Limit of withdrawal achieved')

        self.account_instance.balance = balance - self.amount

        return self.create('done', self.amount)
