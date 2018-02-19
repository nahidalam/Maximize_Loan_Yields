
class facility:
    def __init__(self,
                amount,
                interest_rate,
                facility_id,
                bank_id,
                banned_state = None,
                max_default_likelihood = 1.0,
                yield_amount=0
                ):
        self.bank_id = bank_id
        self.facility_id = facility_id
        self.interest_rate = interest_rate
        self.amount = amount
        self.yield_amount = yield_amount
        self.loan_id = []
        self.amount_remaining = amount
        self.banned_state = banned_state
        self.max_default_likelihood = max_default_likelihood

    def get_facility_id(self):
        return self.facility_id

    def get_amount(self):
        return self.amount

    def get_amount_remaining(self):
        return self.amount_remaining

    def get_interest_rate(self):
        return self.interest_rate

    def get_yield_amount(self):
        return self.yield_amount

    def set_yield_amount(yield_amount):
        self.yield_amount = yield_amount

    def get_loan_ids(self):
        return self.loan_id

    def set_loan_ids(loan_id):
        self.loan_id = loan_id

    def set_banned_state(self, banned_state):
        self.banned_state = banned_state

    def get_banned_state(self):
        return self.banned_state

    def get_max_default_likelihood(self):
        return self.max_default_likelihood

    def set_max_default_likelihood(self, max_default_likelihood):
        self.max_default_likelihood = max_default_likelihood

    def assign_loan(self, loan_amount, max_expected_yield, loan_id_number):
        self.amount_remaining -=loan_amount
        self.yield_amount +=max_expected_yield
        self.loan_id.append(loan_id_number)
