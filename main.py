import wallet
import solana_client
import utils
import transaction_log

def main():
    current_wallet = None

    while True:
        print("\nВыберите действие:")
        print("1. Создать новый кошелёк")
        print("2. Импортировать кошелёк по приватному ключу")
        print("3. Проверить баланс")
        print("4. Отправить SOL")
        print("5. Показать историю операций")
        print("6. Выход")

        choice = input("> ")

        if choice == "1":
            pub, priv = wallet.create_wallet()
            print("\n✅ Кошелёк создан")
            print("Public Key:", pub)
            print("Private Key:", priv)
            utils.save_wallet_to_file(pub, priv)
            current_wallet = wallet.load_wallet_from_private_key(priv)

        elif choice == "2":
            key = input("Введите приватный ключ: ")
            try:
                current_wallet = wallet.load_wallet_from_private_key(key)
                print("✅ Кошелёк импортирован. Адрес:", current_wallet.public_key)
            except Exception as e:
                print("❌ Ошибка:", e)

        elif choice == "3":
            if current_wallet:
                bal = solana_client.get_balance(str(current_wallet.public_key))
                print(f"💰 Баланс: {bal:.6f} SOL")
            else:
                print("Сначала создайте или импортируйте кошелёк")

        elif choice == "4":
            if current_wallet:
                to_addr = input("Введите адрес получателя: ")
                amount = float(input("Сколько SOL отправить: "))
                resp = solana_client.send_sol(current_wallet, to_addr, amount)
                print("🚀 Отправлено. Ответ:", resp)
                transaction_log.log_transaction(str(current_wallet.public_key), to_addr, amount, resp)
            else:
                print("Сначала создайте или импортируйте кошелёк")

        elif choice == "5":
            transaction_log.show_history()

        elif choice == "6":
            break

        else:
            print("Неверный выбор. Повторите.")

if __name__ == "__main__":
    main()