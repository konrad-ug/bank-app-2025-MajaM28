class Account:
    def __init__(self, first_name, last_name, pesel, promoCode = None):
        self.first_name = first_name
        self.last_name = last_name
        self.balance = 0.0
        self.pesel = self.checkPesel(pesel)
        self.promoCode = promoCode
        self.usePromo(promoCode)

    def checkPesel(self,pesel):
        if pesel is not None and (len(pesel) == 11) :
            return pesel
        else:
            return "Invalid"

    def usePromo(self,promo):
        if isinstance(promo,str) and promo.startswith("PROM_"):
            self.balance += 50.0
