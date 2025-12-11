from threading import active_count
from typing import final

from src.account import Account,CompanyAccount,AccountRegistry
import pytest

@pytest.fixture
def account():
    return Account("John", "Doe", "59031412345", None)



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

    def test_company_account_transfer_in(self):
        account = CompanyAccount("XYZ", "1234567890")
        account.transferIn(1000)
        assert account.balance == 1000

    def test_company_account_transfer_out(self):
        account = CompanyAccount("XYZ", "1234567890")
        account.balance = 500
        account.transferOut(100)
        assert account.balance == 400

    def test_company_account_transfer_out_too_much(self):
        account = CompanyAccount("XYZ", "1234567890")
        account.balance = 500
        account.transferOut(-1000)
        assert account.balance == 500

    def test_personal_account_express_transfer_account_positive(self):
        account = Account("John","Doe","60010112345")
        account.balance = 100.0
        account.expressTransferOut(50.0)
        assert account.balance == 49.0

    def test_personal_account_express_transfer_account_empty(self):
        account = Account("John","Doe","60010112345")
        account.balance = 0.0
        account.expressTransferOut(50.0)
        assert account.balance == 0.0

    def test_personal_account_express_transfer_account_exact_amount(self):
        account = Account("John","Doe","60010112345")
        account.balance = 100.0
        account.expressTransferOut(100.0)
        assert account.balance == -1.0

    def test_personal_account_express_transfer_account_too_much(self):
        account = Account("John","Doe","60010112345")
        account.balance = 100.0
        account.expressTransferOut(200.0)
        assert account.balance == 100.0

    def test_personal_account_express_transfer_account_negative_amount(self):
        account = Account("John","Doe","60010112345")
        account.balance = 100.0
        account.expressTransferOut(-50.0)
        assert account.balance == 100.0

    def test_company_account_express_transfer_account_positive(self):    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        account = CompanyAccount("XYZ","1234567890")
        account.balance = 100.0
        account.expressTransferOut(50.0)
        assert account.balance == 45.0

    def test_company_account_express_transfer_account_empty(self):
        account = CompanyAccount("XYZ","1234567890")
        account.balance = 0.0
        account.expressTransferOut(50.0)
        assert account.balance == 0.0

    def test_company_account_express_transfer_account_exact_amount(self):
        account = CompanyAccount("XYZ","1234567890")
        account.balance = 100.0
        account.expressTransferOut(100.0)
        assert account.balance == -5.0

    def test_company_account_express_transfer_account_too_much(self):
        account = CompanyAccount("XYZ","1234567890")
        account.balance = 100.0
        account.expressTransferOut(200.0)
        assert account.balance == 100.0

    def test_company_account_express_transfer_account_negative_amount(self):
        account = CompanyAccount("XYZ","1234567890")
        account.balance = 100.0
        account.expressTransferOut(-50.0)
        assert account.balance == 100.0


    def test_historyTransferIn(self):
        account = Account("John", "Doe", "59031412345", None)
        assert account.balance == 0.0
        account.transferIn(50.0)
        assert account.history == [50.0]

    def test_historyTransferOut(self):
        account = Account("John", "Doe", "59031412345", None)
        account.balance = 300.0
        account.transferOut(100.0)
        assert account.history == [-100.0]

    def test_historyExpressTransferOut(self):
        account = Account("John", "Doe", "59031412345", None)
        account.balance = 300.0
        account.expressTransferOut(100.0)
        assert account.history == [-100.0,-1.0]

    def test_isHistory(self):
        account = Account("John", "Doe", "59031412345", None)
        assert account.history == []


    def test_history_too_short(self):
        account = Account("John", "Doe", "59031412345", None)
        account.balance = 100.0
        account.history = [40]
        assert account.balance == 100.0

    @pytest.mark.parametrize(
        'before,history,amount,final_balance',
        [
            (100.0, [-19.0, 10, 80, 10], 300, 400.0),
            (100.0, [-19.0, 10, 80, -10], 300, 100.0),
            (650.0, [-19.0, 10, 80, 10, -30, 500], 300, 950.0),
            (650.0, [-19.0, 10, 80, 12, -2, 500], 600, 650.0),
            (650.0, [-19.0, 10, 80, 12, -2, 500], 10000, 650.0),
        ],
    )

    def test_submit_for_loan(self,account,before,history,amount,final_balance):
        account.balance = before
        account.history = history

        account.submit_for_loan(amount)

        assert account.balance == final_balance
        

class TestAccount3:
    def test_if_registry(self):
        reg = AccountRegistry()
        assert reg.accounts == []

    def test_add_accounts(self,account):
        reg = AccountRegistry()
        account1 = account
        reg.add_account(account1)
        assert reg.accounts == [account1]

    def test_find_by_pesel_successful(self,account):
        reg = AccountRegistry()
        account1 = account
        account2 = Account("Jack", "Doe", "59031425345", None)
        reg.add_account(account1)
        reg.add_account(account2)
        res = reg.find_by_pesel("59031412345")
        assert res == account1

    def test_find_by_pesel_failure(self,account):
        reg = AccountRegistry()
        account1 = account
        account2 = Account("Jack", "Doe", "59031425345", None)
        reg.add_account(account1)
        reg.add_account(account2)
        res = reg.find_by_pesel("59031418345")
        assert res is None

    def test_list_accounts(self,account):
        reg = AccountRegistry()
        account1 = account
        account2 = Account("Jack", "Doe", "59031425345", None)
        reg.add_account(account1)
        reg.add_account(account2)
        res = reg.all_accounts()
        assert res == [account1,account2]

    def test_count_accounts(self,account):
        reg = AccountRegistry()
        account1 = account
        reg.add_account(account1)
        res = reg.account_count()
        assert res == 1


##pozostałą refaktoryzje zrobie na dniach