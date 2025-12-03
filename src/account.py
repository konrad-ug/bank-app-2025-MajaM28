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



class CompanyAccount(Account):
    def __init__(self,company_name,nip_number):
        self.company_name = company_name
        self.nip_number = self.check_nip(nip_number)
        self.balance = 0.0
        self.history = []

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