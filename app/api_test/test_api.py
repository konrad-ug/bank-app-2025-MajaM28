import requests

from tests.unit.test_account_create import account

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