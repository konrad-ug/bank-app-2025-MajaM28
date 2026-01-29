import os
import requests
from datetime import date
from smtp.smtp import SMTPClient
from pymongo import MongoClient

class Account:
    def __init__(self, first_name, last_name, pesel, promoCode = None):
        self.first_name = first_name
        self.last_name = last_name
        self.balance = 0.0
        self.pesel = self.checkPesel(pesel)
        self.promoCode = promoCode
        self.canUsePromo(self.pesel, promoCode)
        self.history = []


    def checkPesel(self,pesel):
        if pesel is not None and (len(pesel) == 11) :
            return pesel
        else:
            return "Invalid"

    def usePromo(self,promo):
        if isinstance(promo,str) and promo.startswith("PROM_"):
            self.balance += 50.0

    def canUsePromo(self, pesel, promo):
        if pesel != "Invalid":
            year = int(pesel[0:2])
            month = int(pesel[2:4])

            if month >= 20 :
                self.usePromo(promo)
            elif year >= 60 :
                    self.usePromo(promo)

    def transferOut(self,amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            self.history.append(-amount)

    def transferIn(self,amount):
        if amount > 0 :
            self.balance += amount
            self.history.append(amount)

    def expressTransferOut(self,amount):
        if 0 < amount <= self.balance:
            self.balance -= (amount + 1)
            self.history.append(-amount)
            self.history.append(-1)

    def _last_three_plus(self):
        if len(self.history) < 3:
            return False
        last_three = self.history[-3:]
        return min(last_three) > 0

    def _last_five_sum_larger(self, amount):
        if len(self.history) < 5:
            return False
        last_five = self.history[-5:]
        return sum(last_five) > amount

    def submit_for_loan(self,amount):
        decision = False

        if self._last_three_plus():
            decision = True

        if self._last_five_sum_larger(amount):
            decision = True

        if decision:
            self.balance += amount

        return decision

    def send_history_by_email(self,email_address):
        today = date.today().strftime('%Y-%m-%d')
        subject = f"Account Transfer History {today}"
        text = f"Personal account history: {self.history}"

        smtp_client = SMTPClient()
        return smtp_client.send(subject, text, email_address)


class CompanyAccount(Account): # pragma: no cover
    def __init__(self,company_name,nip_number):
        self.company_name = company_name
        self.nip_number = self.check_nip(nip_number)
        if self.nip_number != "Invalid":
            if not self.verify_nip_in_registry(nip_number):
                raise ValueError("Company not registered!!")
        self.balance = 0.0
        self.history = []

    def verify_nip_in_registry(self,nip):
        base = os.getenv('BANK_APP_MF_URL', 'https://wl-test.mf.gov.pl')
        today = date.today().strftime('%Y-%m-%d')
        url = f"{base}/api/search/nip/{nip}?date={today}"

        response = requests.get(url)
        print(f"MF API response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            if 'result' in data and 'subject' in data['result']:
                return data['result']['subject'].get('statusVat') == 'Czynny'

        return False

    def check_nip(self,number):
        if isinstance(number,str) and len(number)==10 :
            return number
        else:
            return "Invalid"

    def expressTransferOut(self,amount):
        if self.balance >= amount > 0:
            self.balance -= (amount + 5)
            self.history.append(-amount)
            self.history.append(-5)

    def take_loan(self,amount):
        if self.balance >= (2*amount) and -1775 in self.history:
            self.balance += amount
            return True
        else:
            return False

    def send_history_by_email(self, email_address):
        today = date.today().strftime('%Y-%m-%d')
        subject = f"Account Transfer History {today}"
        text = f"Company account history: {self.history}"

        smtp_client = SMTPClient()
        return smtp_client.send(subject, text, email_address)

class AccountRegistry:
    def __init__(self):
        self.accounts = []

    def add_account(self,account: Account):
        if self.find_by_pesel(account.pesel) is None:
            self.accounts.append(account)
            return True
        return False


    def find_by_pesel(self,pesel):
        for a in self.accounts:
            if a.pesel == pesel:
                return a
        return None

    def all_accounts(self):
        return list(self.accounts)

    def account_count(self):
        return len(self.accounts)

class MongoAccountsRepository:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017")
        self.collection = self.client["bank"]["accounts"]

    def save_all(self, registry):
        self.collection.delete_many({})
        accounts_data = []

        for account in registry.all_accounts():
            account_dict = {
                "first_name": account.first_name,
                "last_name": account.last_name,
                "pesel": account.pesel,
                "balance": account.balance,
                "history": account.history
            }
            accounts_data.append(account_dict)

        if accounts_data:
            self.collection.insert_many(accounts_data)


    def load_all(self, registry):
        registry.accounts.clear()

        for acc_data in self.collection.find():
            account = Account(
                acc_data["first_name"],
                acc_data["last_name"],
                acc_data["pesel"]
            )

            account.balance = acc_data["balance"]
            account.history = acc_data["history"]
            registry.add_account(account)

