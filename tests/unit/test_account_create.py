from threading import active_count

from src.account import Account


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