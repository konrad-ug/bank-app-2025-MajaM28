from flask import Flask, request, jsonify
from src.account import AccountRegistry
from src.account import Account
from tests.unit.test_account_create import account

app = Flask(__name__)
registry = AccountRegistry()

@app.route("/api/accounts", methods=['POST'])
def create_account():
    data = request.get_json()
    print(f"Create account request: {data}")
    account = Account(data["first_name"], data["last_name"], data["pesel"])
    registry.add_account(account)
    return jsonify({"message": "Account created"}), 201

@app.route("/api/accounts", methods=['GET'])
def get_all_accounts():
    print("Get all accounts request received")
    accounts = registry.all_accounts()
    accounts_data = [{"first_name": acc.first_name, "last_name": acc.last_name, "pesel":
    acc.pesel, "balance": acc.balance} for acc in accounts]
    return jsonify(accounts_data), 200

@app.route("/api/accounts/count", methods=['GET'])
def get_account_count():
    print("Get account count request received")
    count = registry.account_count()
    return jsonify({"count": count}), 200

@app.route("/api/accounts/<pesel>", methods=['GET'])
def get_account_by_pesel(pesel):
    print(f"Find account with pesel: {pesel}")
    account_p = registry.find_by_pesel(pesel)

    if account_p is None:
        return jsonify({"error": "No account with this pesel found"}), 404

    account_data = {
        "first_name": account_p.first_name,
        "last_name":account_p.last_name,
        "pesel":account_p.pesel,
        "balance":account_p.balance
    }
    return jsonify(account_data), 200


@app.route("/api/accounts/<pesel>", methods=['PATCH'])
def update_account(pesel):
    print(f"received request to update account with pesel {pesel}")

    account_p = registry.find_by_pesel(pesel)

    if account_p is None:
        return jsonify({"error": "No account with this pesel found"}), 404

    first_name = request.json.get("first_name")
    last_name = request.json.get("last_name")

    if first_name is not None:
        account_p.first_name = first_name

    if last_name is not None:
        account_p.last_name = last_name

    return jsonify({"message": "Account updated"}), 200


@app.route("/api/accounts/<pesel>", methods=['DELETE'])
def delete_account(pesel):
    print(f"received request to delete account with pesel {pesel}")

    account_p = registry.find_by_pesel(pesel)

    if account_p is None:
        return jsonify({"error": "No account with this pesel found"}), 404

    registry.accounts.remove(account_p)

    return jsonify({"message": "Account deleted"}), 200