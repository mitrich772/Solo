import json
import os

LOG_FILE = "history.json"

def log_transaction(from_addr, to_addr, amount, response):
    record = {
        "from": from_addr,
        "to": to_addr,
        "amount": amount,
        "response": response,
    }
    history = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            history = json.load(f)
    history.append(record)
    with open(LOG_FILE, "w") as f:
        json.dump(history, f, indent=2)

def show_history():
    if not os.path.exists(LOG_FILE):
        print("Нет истории операций.")
        return
    with open(LOG_FILE, "r") as f:
        history = json.load(f)
    if not history:
        print("История пуста.")
    else:
        print("\n📜 История операций:")
        for tx in history:
            print(f"От: {tx['from']}\nКому: {tx['to']}\nСумма: {tx['amount']} SOL\nОтвет: {tx['response']}\n---")