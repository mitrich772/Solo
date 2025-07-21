from solders.keypair import Keypair

import base58

def create_wallet():
    wallet = Keypair()
    private_key_b58 = base58.b58encode(wallet.secret_key).decode("utf-8")
    public_key_str = str(wallet.public_key)
    return public_key_str, private_key_b58

def load_wallet_from_private_key(private_key_b58):
    private_key = base58.b58decode(private_key_b58)
    wallet = Keypair.from_secret_key(private_key)
    return wallet