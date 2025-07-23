import json
import os

LOG_FILE = "history.json"

def log_transaction(from_addr, to_addr, amount, response):
    # Приводим response к строке, чтобы избежать ошибки сериализации
    record = {
        "from": from_addr,
        "to": to_addr,
        "amount": amount,
        "response": str(response),
    }

    history = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []

    history.append(record)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def show_history():
    if not os.path.exists(LOG_FILE):
        print("Нет истории операций.")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        try:
            history = json.load(f)
        except json.JSONDecodeError:
            print("История повреждена.")
            return

    if not history:
        print("История пуста.")
    else:
        print("\n📜 История операций:")
        for tx in history:
            print(f"От: {tx['from']}\nКому: {tx['to']}\nСумма: {tx['amount']} SOL\nОтвет: {tx['response']}\n---")
