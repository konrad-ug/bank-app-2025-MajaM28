from flask import Flask, request, jsonify
from src.account import AccountRegistry
from src.account import Account
from src.account import MongoAccountsRepository


app = Flask(__name__)
registry = AccountRegistry()
mongoRepo = MongoAccountsRepository()

@app.route("/api/accounts", methods=['POST'])
def create_account():
    data = request.get_json()
    print(f"Create account request: {data}")
    account = Account(data["first_name"], data["last_name"], data["pesel"])
    created = registry.add_account(account)
    if not created:
        return jsonify({"message": "Account with this PESEL already created"}), 409
    return jsonify({"message": "Account created"}), 201

@app.route("/api/accounts", methods=['GET'])
def get_all_accounts():
    print("Get all accounts request received")
    accounts = registry.all_accounts()
    accounts_data = [{"first_name": acc.first_name, "last_name": acc.last_name, "pesel": acc.pesel, "balance": acc.balance} for acc in accounts]
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

@app.route("/api/accounts/<pesel>/transfer", methods=['POST'])
def transfer(pesel):
    account_p = registry.find_by_pesel(pesel)
    if account_p is None:
        return jsonify({"error": "No account with this pesel found"}), 404

    data = request.get_json()
    amount = data.get("amount")
    transfer_type = data.get("type")

    if transfer_type not in ["incoming", "outgoing", "express"]:
        return jsonify({"error": "Unknown transfer type"}), 400

    if transfer_type == "incoming":
        account_p.balance += amount
        return jsonify({"message": "Incoming transfer received"}), 200

    if transfer_type == "outgoing":
        if account_p.balance < amount:
            return jsonify({"error": "Not enough funds"}), 422

        account_p.balance -= amount
        return jsonify({"message": "Outgoing transfer received"}), 200

    if transfer_type == "express":
        account_p.balance += amount
        return jsonify({"message": "Express transfer received"}), 200

@app.route("/api/accounts/save", methods=['POST'])
def save_accounts_to_database():
    count = mongoRepo.save_all(registry)
    return jsonify({"message": "Accounts Saved to database"}), 200

@app.route("/api/accounts/load", methods=['POST'])
def load_accounts_from_database():
    count = mongoRepo.load_all(registry)
    return jsonify({"message": "Accounts loaded fromm database"}), 200


if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, port=5000, host='127.0.0.1')