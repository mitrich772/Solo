
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.system_program import transfer, TransferParams

client = Client("https://api.devnet.solana.com")

def get_balance(pubkey_str):
    pubkey = Pubkey.from_string(pubkey_str)
    res = client.get_balance(pubkey)
    return res.value / 1_000_000_000

def send_sol(from_wallet, to_pubkey_str, amount_sol):
    to_pubkey = Pubkey.from_string(to_pubkey_str)
    lamports = int(amount_sol * 1_000_000_000)

    txn = Transaction().add(
        transfer(
            TransferParams(
                from_pubkey=from_wallet.pubkey(),
                to_pubkey=to_pubkey,
                lamports=lamports,
            )
        )
    )

    response = client.send_transaction(txn, from_wallet)
    return response.value