from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.publickey import PublicKey

client = Client("https://api.devnet.solana.com")

def get_balance(pubkey_str):
    return client.get_balance(PublicKey(pubkey_str))["result"]["value"] / 1_000_000_000

def send_sol(from_wallet, to_pubkey_str, amount_sol):
    to_pubkey = PublicKey(to_pubkey_str)
    txn = Transaction().add(
        transfer(
            TransferParams(
                from_pubkey=from_wallet.public_key,
                to_pubkey=to_pubkey,
                lamports=int(amount_sol * 1_000_000_000),
            )
        )
    )
    return client.send_transaction(txn, from_wallet)
