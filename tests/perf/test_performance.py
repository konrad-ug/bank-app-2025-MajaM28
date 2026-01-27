import requests
import random

r = "http://127.0.0.1:5000"


def test_create_delete_100_times():
    for i in range(100):
        pesel = f"900101{random.randint(10000, 99999)}" #trzeba w kazdej iteracji dac inny pesel zeby nie dostac 409

        data = {
            "first_name": "Performance",
            "last_name": "Test",
            "pesel": pesel
        }

        res_create = requests.post(
            f"{r}/api/accounts",
            json=data,
            timeout=0.5
        )
        assert res_create.status_code == 201

        res_delete = requests.delete(
            f"{r}/api/accounts/{pesel}",
            timeout=0.5
        )
        assert res_delete.status_code == 200


def test_create_and_100_transfers():
    pesel = f"950101{random.randint(10000, 99999)}"

    data = {
        "first_name": "Transfer",
        "last_name": "Test",
        "pesel": pesel
    }

    res_create = requests.post(
        f"{r}/api/accounts",
        json=data,
        timeout=0.5
    )
    assert res_create.status_code == 201

    for i in range(100):
        t_data = {
            "amount": 10,
            "type": "incoming"
        }

        res_transfer = requests.post(
            f"{r}/api/accounts/{pesel}/transfer",
            json=t_data,
            timeout=0.5
        )
        assert res_transfer.status_code == 200

    res_get = requests.get(f"{r}/api/accounts/{pesel}", timeout=0.5)
    assert res_get.status_code == 200
    assert res_get.json()["balance"] == 1000.0