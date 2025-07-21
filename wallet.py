from solders.keypair import Keypair
import base58

def create_wallet():
    wallet = Keypair()
    priv_bytes = wallet.to_bytes()
    priv_b58 = base58.b58encode(priv_bytes).decode("utf-8")
    pub_str = str(wallet.pubkey())
    return pub_str, priv_b58

def load_wallet_from_private_key(private_key_b58):
    priv_bytes = base58.b58decode(private_key_b58)
    wallet = Keypair.from_bytes(priv_bytes)
    return wallet


