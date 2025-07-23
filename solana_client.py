from solana.rpc.api import Client
from solana.rpc.types import TxOpts

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.solders import Signature
from solders.system_program import TransferParams, transfer
from solders.message import Message
from solders.transaction import Transaction


client = Client("https://api.devnet.solana.com")

def get_balance(pubkey_str):
    pubkey = Pubkey.from_string(pubkey_str)
    res = client.get_balance(pubkey)
    return res.value / 1_000_000_000

def send_sol(from_wallet: Keypair, to_pubkey_str: str, amount_sol: float) -> Signature:
    """
    Пересылает amount_sol SOL с from_wallet на to_pubkey_str.
    Возвращает подпись (signature) транзакции.
    """
    # 1. Парсим Pubkey получателя
    to_pubkey = Pubkey.from_string(to_pubkey_str)

    # 2. Конвертируем SOL в лампорты
    lamports = int(amount_sol * 1_000_000_000)

    # 3. Формируем Instruction перевода
    ix = transfer(
        TransferParams(
            from_pubkey=from_wallet.pubkey(),
            to_pubkey=to_pubkey,
            lamports=lamports,
        )
    )

    # 4. Упаковываем Instruction в Message, указывая отправителя (fee_payer)
    msg = Message([ix], from_wallet.pubkey())

    # 5. Берём свежий блокхеш (теперь через свойство .value.blockhash)
    latest = client.get_latest_blockhash()
    blockhash = latest.value.blockhash

    # 6. Строим Transaction, указываем список подписантов и blockhash
    txn = Transaction([from_wallet], msg, blockhash)

    # 7. Отправляем транзакцию
    resp = client.send_transaction(txn, opts=TxOpts(skip_preflight=False))

    # 8. Извлекаем подпись из поля .signature
    return resp.value