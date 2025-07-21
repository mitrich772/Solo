def save_wallet_to_file(pub, priv, filename="wallet.txt"):
    with open(filename, "w") as f:
        f.write(f"Public Key: {pub}\n")
        f.write(f"Private Key: {priv}\n")