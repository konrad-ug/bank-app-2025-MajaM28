from threading import active_count

from src.account import Account, CompanyAccount


class TestAccount:
    def test_account_creation(self):
        account = Account("John", "Doe","12345678910")
        assert account.first_name == "John"
        assert account.last_name == "Doe"
        assert account.balance == 0.0
        assert account.pesel == "12345678910"

    def test_pesel_too_short(self):
        account = Account("Jane","Doe","12345")
        assert account.pesel == "Invalid"

    def test_pesel_too_long(self):
        account = Account("Jane","Doe","123456789101112")
        assert account.pesel == "Invalid"

    def test_pesel_is_none(self):
        account = Account("Jane","Doe",None)
        assert account.pesel == "Invalid"

    def test_no_code(self):
        account = Account("John", "Doe","12345678910",None)
        assert account.balance == 0.0

    def test_correct_code(self):
        account = Account("John", "Doe", "12345678910", "PROM_ABC")
        assert account.balance == 50.0

    def test_incorret_code(self):
        account = Account("John", "Doe", "12345678910", "PROT_ABC")
        assert account.balance == 0.0

    def test_older_age_right_code(self):
        account = Account("John","Doe","59031412345", "PROM_ABC")
        assert account.balance == 0.0

    def test_older_age_wrong_code(self):
        account = Account("John", "Doe", "59031412345", "PROT_ABC")
        assert account.balance == 0.0

    def test_younger_age_right_code(self):
        account = Account("John", "Doe", "60010112345", "PROM_ABC")
        assert account.balance == 50.0

    def test_younger_age_wrong_code(self):
        account = Account("John", "Doe", "60010112345", "PROT_ABC")
        assert account.balance == 0.0

    def test_younger_age_no_code(self):
        account = Account("John", "Doe", "60010112345", None)
        assert account.balance == 0.0

    def test_older_age_no_code(self):
        account = Account("John", "Doe", "59031412345", None)
        assert account.balance == 0.0

class TestAccount2:
    def test_transfer_out_if_account_positive(self):
        account = Account("John","Doe","60010112345")
        account.balance = 100.0
        account.transferOut(50.0)
        assert account.balance == 50.0

    def test_transfer_out_if_account_empty(self):
        account = Account("John","Doe","60010112345")
        account.balance = 0.0
        account.transferOut(50.0)
        assert account.balance == 0.0

    def test_transfer_out_exact_amount(self):
        account = Account("John","Doe","60010112345")
        account.balance = 100.0
        account.transferOut(100.0)
        assert account.balance == 0.0

    def test_transfer_out_too_much(self):
        account = Account("John","Doe","60010112345")
        account.balance = 10.0
        account.transferOut(50.0)
        assert account.balance == 10.0

    def test_transfer_out_neg_number(self):
        account = Account("John","Doe","60010112345")
        account.balance = 10.0
        account.transferOut(-5.0)
        assert account.balance == 10.0

    def test_transfer_in_normal(self):
        account = Account("John", "Doe", "60010112345")
        account.balance = 10.0
        account.transferIn(5.0)
        assert account.balance == 15.0

    def test_transfer_in_neg_number(self):
        account = Account("John", "Doe", "60010112345")
        account.balance = 10.0
        account.transferIn(-5.0)
        assert account.balance == 10.0

    def test_company_account_ok(self):
        account = CompanyAccount("XYZ","1234567890")
        assert account.nip_number == "1234567890"

    def test_company_account_nip_too_short(self):
        account = CompanyAccount("XYZ","12345")
        assert account.nip_number == "Invalid"

    def test_company_account_nip_too_long(self):
        account = CompanyAccount("XYZ","12345678901234")
        assert account.nip_number == "Invalid"

    def test_company_account_none(self):
        account = CompanyAccount("XYZ",None)
        assert account.nip_number == "Invalid"

    def test_company_acccount_transfer_in(self):
        account = CompanyAccount("XYZ", "1234567890")
        account.transferIn(1000)
        assert account.balance == 1000

    def test_company_acccount_transfer_out(self):
        account = CompanyAccount("XYZ", "1234567890")
        account.balance = 500
        account.transferOut(100)
        assert account.balance == 400

    def test_company_acccount_transfer_out_too_much(self):
        account = CompanyAccount("XYZ", "1234567890")
        account.balance = 500
        account.transferOut(-1000)
        assert account.balance == 500