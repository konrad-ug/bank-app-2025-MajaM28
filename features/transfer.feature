Feature: Transfer


Scenario: User receiving transfer will have a higher balance
  Given Account registry is empty
  And I create an account using name: "kurt", last name: "cobain", pesel: "89092909246"
  When I make incoming transfer of "100" to account with pesel "89092909246"
  Then Account with pesel "89092909246" has balance equal "100"

Scenario: User cant transfer out due to too low balance
  Given Account registry is empty
  And I create an account using name: "Dwight", last name: "Schrute", pesel: "11111111111"
  When I make outgoing transfer of "100" from account with pesel "11111111111"
  Then Last transfer failed

  Scenario: User CAN transfer out with high enough balance
  Given Account registry is empty
  And I create an account using name: "Pam", last name: "Beesly", pesel: "22222222222"
  When I make incoming transfer of "100000" to account with pesel "22222222222"
  And I make outgoing transfer of "10" from account with pesel "22222222222"
  Then Last transfer success
  And Account with pesel "22222222222" has balance equal "99990"