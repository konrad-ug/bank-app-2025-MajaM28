from behave import *
import requests

URL = "http://localhost:5000"

@when('I make incoming transfer of "{amount}" to account with pesel "{pesel}"')
def incoming_transfer(context, amount, pesel):
    json_body = {"amount": int(amount), "type": "incoming"}
    response = requests.post(URL + f"/api/accounts/{pesel}/transfer", json=json_body)
    assert response.status_code == 200

@when('I make outgoing transfer of "{amount}" from account with pesel "{pesel}"')
def outgoing_transfer(context, amount, pesel):
    json_body = {"amount": int(amount), "type": "outgoing"}
    response = requests.post(URL + f"/api/accounts/{pesel}/transfer", json=json_body)
    context.last_transfer_status = response.status_code

@then('Account with pesel "{pesel}" has balance equal "{balance}"')
def check_balance(context, pesel, balance):
    response = requests.get(URL + f"/api/accounts/{pesel}")
    assert response.status_code == 200
    assert response.json()["balance"] == int(balance)

@then('Last transfer failed')
def last_transfer_failed(context):
    assert context.last_transfer_status != 200

@then('Last transfer success')
def last_transfer_success(context):
    assert context.last_transfer_status == 200