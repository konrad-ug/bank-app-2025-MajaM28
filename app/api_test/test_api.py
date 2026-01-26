import requests

from src.account import AccountRegistry, Account

r = "http://127.0.0.1:5000"

def test_create_account():
    account_g ={
        "first_name": "James",
        "last_name": "Hetfield",
        "pesel": "89092909825"
    }

    res = requests.post(
        f"{r}/api/accounts",
        json = account_g
    )

    assert res.status_code== 201

    res_get = requests.get(f"{r}/api/accounts/89092909825")
    assert res_get.status_code == 200

    account_data = res_get.json()
    assert account_data["first_name"] == "James"
    assert account_data["last_name"] == "Hetfield"
    assert account_data["pesel"] == "89092909825"

def test_search_by_pesel():
    account_g = {
        "first_name": "James",
        "last_name": "Hetfield",
        "pesel": "89092909826"
    }

    res = requests.post(
        f"{r}/api/accounts",
        json=account_g
    )

    assert res.status_code == 201

    res_get = requests.get(f"{r}/api/accounts/{account_g['pesel']}")
    assert res_get.status_code == 200

    account_data = res_get.json()

    assert account_data["first_name"] == "James"
    assert account_data["last_name"] == "Hetfield"
    assert account_data["pesel"] == "89092909826"
    assert account_data["balance"] == 0.0

def test_no_account_with_pesel():
    res_get = requests.get(f"{r}/api/accounts/12345678901")
    assert  res_get.status_code == 404
    assert res_get.json() == {"error": "No account with this pesel found"}

def test_update_account():
    account_g = {
        "first_name": "James",
        "last_name": "Hetfield",
        "pesel": "89092909827"
    }

    res = requests.post(
        f"{r}/api/accounts",
        json=account_g
    )

    assert res.status_code == 201

    patch = {
        "first_name" : "Jan",
        "last_name": "Suszek"
    }

    res_p = requests.patch(f"{r}/api/accounts/{account_g['pesel']}",json=patch)
    assert res_p.status_code == 200
    assert res_p.json() == {"message": "Account updated"}

    res_g = requests.get(f"{r}/api/accounts/{account_g['pesel']}")
    assert res_g.status_code == 200
    account_data = res_g.json()
    assert account_data["first_name"] == "Jan"
    assert account_data["last_name"] == "Suszek"

def test_delete_account():
    account_g = {
        "first_name": "James",
        "last_name": "Hetfield",
        "pesel": "89092909828"
    }

    res = requests.post(
        f"{r}/api/accounts",
        json=account_g
    )

    assert res.status_code == 201

    delete_res = requests.delete(f"{r}/api/accounts/{account_g['pesel']}")
    assert delete_res.status_code == 200
    assert delete_res.json() == {"message": "Account deleted"}

    get_res = requests.get(f"{r}/api/accounts/{account_g['pesel']}")
    assert get_res.status_code == 404
    assert get_res.json() == {"error": "No account with this pesel found"}

def test_delete_account_no_pesel():
    res = requests.delete(f"{r}/api/accounts/12345678901")
    assert res.status_code == 404
    assert res.json() == {"error": "No account with this pesel found"}


def test_add_account_duplicate_pesel():
    registry = AccountRegistry()
    acc1 = Account("Jan", "Kowalski", "12345678901")
    acc2 = Account("Anna", "Nowak", "12345678901")

    assert registry.add_account(acc1) is True
    assert registry.add_account(acc2) is False
    assert len(registry.accounts) == 1

def test_transfer_account_not_found():
    transfer_data = {
        "amount": 500,
        "type": "incoming"
    }
    res = requests.post(
        f"{r}/api/accounts/99999999999/transfer",
        json=transfer_data
    )
    assert res.status_code == 404
    assert res.json() == {"error": "No account with this pesel found"}

def test_create_new_account_duplicate_pesel():
    account_data = {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "pesel": "99010112345"
    }

    res1 = requests.post(f"{r}/api/accounts", json=account_data)
    assert res1.status_code == 201

    res2 = requests.post(f"{r}/api/accounts", json=account_data)
    assert res2.status_code == 409
    assert "PESEL" in res2.json()["message"]

def test_update_account_not_found():
    patch_data = {
        "first_name": "Jan",
        "last_name": "Nowak"
    }

    res = requests.patch(f"{r}/api/accounts/99999999999", json=patch_data)
    assert res.status_code == 404
    assert res.json() == {"error": "No account with this pesel found"}


def test_transfer_unknown_type():
    pesel = f"88010145618"
    account_data = {
        "first_name": "Jan",
        "last_name": "Testowy",
        "pesel": pesel
    }
    res = requests.post(f"{r}/api/accounts", json=account_data)
    assert res.status_code == 201

    transfer_data = {
        "amount": 100,
        "type": "unknown_type"
    }
    res = requests.post(
        f"{r}/api/accounts/{pesel}/transfer",
        json=transfer_data
    )
    assert res.status_code == 400
    assert res.json() == {"error": "Unknown transfer type"}


def test_transfer_incoming_success():
    pesel = f"88010195618"
    account_data = {
        "first_name": "Anna",
        "last_name": "Testowa",
        "pesel": pesel
    }
    res = requests.post(f"{r}/api/accounts", json=account_data)
    assert res.status_code == 201
    transfer_data = {
        "amount": 500,
        "type": "incoming"
    }
    res = requests.post(f"{r}/api/accounts/{pesel}/transfer", json=transfer_data)
    assert res.status_code == 200
    assert res.json() == {"message": "Incoming transfer received"}

    res_get = requests.get(f"{r}/api/accounts/{pesel}")
    assert res_get.status_code == 200
    assert res_get.json()["balance"] == 500.0


def test_transfer_outgoing_success():
    pesel = f"88010195617"
    account_data = {
        "first_name": "Jan",
        "last_name": "Test",
        "pesel": pesel
    }
    res = requests.post(f"{r}/api/accounts", json=account_data)
    assert res.status_code == 201

    transfer_in = {
        "amount": 1000,
        "type": "incoming"
    }
    res = requests.post(f"{r}/api/accounts/{pesel}/transfer", json=transfer_in)
    assert res.status_code == 200

    transfer_out = {
        "amount": 300,
        "type": "outgoing"
    }
    res = requests.post(f"{r}/api/accounts/{pesel}/transfer", json=transfer_out)
    assert res.status_code == 200
    assert res.json() == {"message": "Outgoing transfer received"}

    res_get = requests.get(f"{r}/api/accounts/{pesel}")
    assert res_get.status_code == 200
    assert res_get.json()["balance"] == 700.0


def test_transfer_outgoing_insufficient_funds():

    pesel = f"88010195616"
    account_data = {
        "first_name": "Jan",
        "last_name": "Test",
        "pesel": pesel
    }
    res = requests.post(f"{r}/api/accounts", json=account_data)
    assert res.status_code == 201

    transfer_data = {
        "amount": 500,
        "type": "outgoing"
    }
    res = requests.post(f"{r}/api/accounts/{pesel}/transfer", json=transfer_data)
    assert res.status_code == 422
    assert res.json() == {"error": "Not enough funds"}


def test_transfer_express_success():
    pesel = f"84010151678"
    account_data = {
        "first_name": "Jan",
        "last_name": "Test",
        "pesel": pesel
    }
    res = requests.post(f"{r}/api/accounts", json=account_data)
    assert res.status_code == 201
    transfer_data = {
        "amount": 750,
        "type": "express"
    }
    res = requests.post(f"{r}/api/accounts/{pesel}/transfer", json=transfer_data)
    assert res.status_code == 200
    assert res.json() == {"message": "Express transfer received"}

    res_get = requests.get(f"{r}/api/accounts/{pesel}")
    assert res_get.status_code == 200
    assert res_get.json()["balance"] == 750.0