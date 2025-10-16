class Account:
    def __init__(self, first_name, last_name, pesel):
        self.first_name = first_name
        self.last_name = last_name
        self.balance = 0.0
        self.pesel = self.checkPesel(pesel)

    def checkPesel(self,pesel):
        if pesel is not None and (len(pesel) == 11) :
            return pesel
        else:
            return "Invalid"

