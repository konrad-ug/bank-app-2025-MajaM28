from threading import active_count
from typing import final
from unittest.mock import patch, Mock

from src.account import Account,CompanyAccount,AccountRegistry, MongoAccountsRepository
import pytest

@pytest.fixture
def account():
    return Account("John", "Doe", "59031412345", None)

@pytest.fixture
def mock_nip_verification(mocker):
    mock_get = mocker.patch('src.account.requests.get')
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "result": {"subject": {"statusVat": "Czynny"}}
    }
    mock_get.return_value = mock_response
    return mock_get


@pytest.fixture
def mock_repo(mocker):
    mock_collection = mocker.Mock()
    repo = MongoAccountsRepository()
    repo.collection = mock_collection
    return repo, mock_collection


#testowanie tworzenia konta osobistego
class TestAccountCreation:
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


#testowanie przelewów dla konta osobistego
class TestAccountTransfers:
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


#testowanie tworzenie konta firmowego (razem z walidacja NIP)
class TestCompanyAccountCreate:
    @pytest.fixture(autouse=True)
    def _mock_mf(self, mock_nip_verification):
        pass

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


#testowanie przelewów konta firmowego
class TestCompanyAccountTransfers:
    @pytest.fixture(autouse=True)
    def _mock_mf(self, mock_nip_verification):
        pass

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

#testowanie zapisu historii konta
class TestAccountHistory:
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

    def test_last_three_and_less_than_three_trans(self):
        account = Account("Jan", "Kowalski", "12345678901")
        account.history = [100, 50]

        result = account._last_three_plus()
        assert result is False

#testowanie pożyczek dla konta osobistego
class TestAccountLoan:
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

#testowanie dla pożyczek dla konta firmowego
class TestCompanyLoan:
    @pytest.fixture(autouse=True)
    def _mock_mf(self, mock_nip_verification):
        pass
    def test_company_take_loan_success(self):
        account = CompanyAccount("XYZ", "1234567890")
        account.balance = 10000
        account.history = [-1775, 100, 200]

        result = account.take_loan(4000)
        assert result is True
        assert account.balance == 14000.0

    def test_company_take_loan_insufficient_balance(self):
        account = CompanyAccount("XYZ", "1234567890")
        account.balance = 5000
        account.history = [-1775, 100]

        result = account.take_loan(4000)
        assert result is False
        assert account.balance == 5000.0

    def test_company_take_loan_no_special_transaction(self):
        account = CompanyAccount("XYZ", "1234567890")
        account.balance = 10000
        account.history = [100, 200]

        result = account.take_loan(4000)
        assert result is False
        assert account.balance == 10000.0

        
#testowanie registry konta
class TestAccountRegistry:
    @pytest.fixture(autouse=True)
    def _mock_mf(self, mock_nip_verification):
        pass

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

    def test_add_account_duplicate(self):
        registry = AccountRegistry()
        acc1 = Account("Jan", "Kowalski", "12345678901")
        acc2 = Account("Anna", "Nowak", "12345678901")

        registry.add_account(acc1)
        result = registry.add_account(acc2)

        assert result is False
        assert len(registry.accounts) == 1

#testowanie walidacji nip
class TestCompanyAccountNIPValidation:
    @patch('src.account.requests.get')
    def test_valid_nip_creates_account(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"result": {"subject": {"statusVat": "Czynny"}}}'
        mock_response.json.return_value = {
            "result": {
                "subject": {
                    "statusVat": "Czynny"
                }
            }
        }
        mock_get.return_value = mock_response

        account = CompanyAccount("Test Sp. z o.o.", "1234567890")

        assert account.company_name == "Test Sp. z o.o."
        assert account.nip_number == "1234567890"
        mock_get.assert_called_once()

    @patch('src.account.requests.get')
    def test_invalid_nip_raises_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "subject": {
                    "statusVat": "Nieczynny"
                }
            }
        }
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Company not registered!!"):
            CompanyAccount("Bad Company", "9999999999")

        mock_get.assert_called_once()

    @patch('src.account.requests.get')
    def test_nip_not_found_raises_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Company not registered!!"):
            CompanyAccount("NonExistent", "1111111111")

    def test_invalid_nip_length_no_api_call(self):
        account = CompanyAccount("Test", "123")

        assert account.nip_number == "Invalid"
        assert account.company_name == "Test"


class TestEmailHistory:

    def test_personal_account_send_email_success(self, mocker):
        mock_send = mocker.patch('src.account.SMTPClient.send', return_value=True)

        account = Account("Jan", "Test", "12345678901")
        account.history = [100, -50, 200]

        result = account.send_history_by_email("test@example.com")

        assert result is True
        mock_send.assert_called_once()

    def test_personal_account_send_email_failure(self, mocker):
        mock_send = mocker.patch('src.account.SMTPClient.send', return_value=False)

        account = Account("Jan", "Test", "12345678901")
        result = account.send_history_by_email("test@example.com")

        assert result is False

    def test_company_account_send_email_success(self, mocker):
        mock_get = mocker.patch('src.account.requests.get')
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "result": {"subject": {"statusVat": "Czynny"}}
        }

        mock_send = mocker.patch('src.account.SMTPClient.send', return_value=True)

        company = CompanyAccount("Comp", "1234567890")
        result = company.send_history_by_email("test@example.com")

        assert result is True

    def test_company_account_send_email_failure(self, mocker):
        mock_get = mocker.patch('src.account.requests.get') #to to mockowanie walidacji nipu
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "result": {"subject": {"statusVat": "Czynny"}}
        }

        mock_send = mocker.patch('src.account.SMTPClient.send', return_value=False)

        company = CompanyAccount("Comp", "1234567890")
        result = company.send_history_by_email("test@example.com")

        assert result is False

class TestMongo:
    def test_save_clears_and_inserts(self, mock_repo):
        repo, mock_collection = mock_repo

        registry = AccountRegistry()
        acc1 = Account("Jan", "Padarewski", "12345678901")
        acc2 = Account("Fryderyk", "Chopin", "98765432109")
        registry.add_account(acc1)
        registry.add_account(acc2)

        repo.save_all(registry)

        mock_collection.delete_many.assert_called_once_with({})
        assert mock_collection.insert_many.call_count == 1

        call_args = mock_collection.insert_many.call_args[0][0]
        assert len(call_args) == 2
        assert call_args[0]["pesel"] == "12345678901"
        assert call_args[1]["pesel"] == "98765432109"

    def test_save_with_empty_reg(self, mock_repo):
        repo, mock_collection = mock_repo

        registry = AccountRegistry()

        repo.save_all(registry)

        mock_collection.delete_many.assert_called_once_with({})
        mock_collection.insert_many.assert_not_called()

    def test_load_all_loads_accounts(self,mock_repo):
        repo, mock_collection = mock_repo
        mock_collection.find.return_value = [
            {
                "first_name": "Walter",
                "last_name": "White",
                "pesel": "11111111111",
                "balance": 500,
                "history": ["+500"]
            }
        ]

        registry = AccountRegistry()
        repo.load_all(registry)
        account = registry.accounts[0]
        assert account.pesel == "11111111111"
