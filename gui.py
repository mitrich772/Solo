import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, scrolledtext
import wallet
import solana_client
import utils
import transaction_log
import json
import os

class SolanaWalletGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Solana Wallet (Devnet)")
        self.current_wallet = None
        self.current_pubkey = None
        self.setup_ui()

    def setup_ui(self):
        # Wallet Frame
        wallet_frame = tk.LabelFrame(self.root, text="Wallet", padx=10, pady=10)
        wallet_frame.pack(padx=10, pady=5, fill="x")

        self.wallet_name_var = tk.StringVar()
        tk.Label(wallet_frame, text="Wallet Name:").grid(row=0, column=0, sticky="e")
        self.wallet_name_entry = tk.Entry(wallet_frame, textvariable=self.wallet_name_var, width=50)
        self.wallet_name_entry.grid(row=0, column=1, padx=5)
        self._add_paste_support(self.wallet_name_entry)

        self.pubkey_var = tk.StringVar()
        self.privkey_var = tk.StringVar()

        tk.Label(wallet_frame, text="Public Key:").grid(row=1, column=0, sticky="e")
        self.pubkey_entry = tk.Entry(wallet_frame, textvariable=self.pubkey_var, width=50)
        self.pubkey_entry.grid(row=1, column=1, padx=5)
        self._add_paste_support(self.pubkey_entry)
        self._make_entry_clickable(self.pubkey_entry, 'Public key copied!')

        tk.Label(wallet_frame, text="Private Key:").grid(row=2, column=0, sticky="e")
        self.privkey_entry = tk.Entry(wallet_frame, textvariable=self.privkey_var, width=50)
        self.privkey_entry.grid(row=2, column=1, padx=5)
        self._add_paste_support(self.privkey_entry)
        self._make_entry_clickable(self.privkey_entry, 'Private key copied!')

        btn_frame = tk.Frame(wallet_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=5)
        tk.Button(btn_frame, text="Create Wallet", command=self.create_wallet).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Import Wallet", command=self.import_wallet).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Import from File", command=self.import_wallet_from_file).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Save Wallet", command=self.save_wallet).pack(side="left", padx=5)

        # Balance Frame
        balance_frame = tk.LabelFrame(self.root, text="Balance", padx=10, pady=10)
        balance_frame.pack(padx=10, pady=5, fill="x")
        self.balance_var = tk.StringVar(value="0.0 SOL")
        tk.Label(balance_frame, text="Current Balance:").pack(side="left")
        tk.Label(balance_frame, textvariable=self.balance_var, font=("Arial", 12, "bold")).pack(side="left", padx=10)
        tk.Button(balance_frame, text="Check Balance", command=self.check_balance).pack(side="left", padx=5)

        # Send Frame
        send_frame = tk.LabelFrame(self.root, text="Send SOL", padx=10, pady=10)
        send_frame.pack(padx=10, pady=5, fill="x")
        tk.Label(send_frame, text="Recipient Address:").grid(row=0, column=0, sticky="e")
        self.recipient_entry = tk.Entry(send_frame, width=44)
        self.recipient_entry.grid(row=0, column=1, padx=5)
        self._add_paste_support(self.recipient_entry)

        tk.Label(send_frame, text="Amount (SOL):").grid(row=1, column=0, sticky="e")
        self.amount_entry = tk.Entry(send_frame, width=20)
        self.amount_entry.grid(row=1, column=1, sticky="w", padx=5)
        self._add_paste_support(self.amount_entry)
        tk.Button(send_frame, text="Send", command=self.send_sol).grid(row=2, column=0, columnspan=2, pady=5)

        # History Frame
        history_frame = tk.LabelFrame(self.root, text="Transaction History", padx=10, pady=10)
        history_frame.pack(padx=10, pady=5, fill="both", expand=True)
        self.history_text = scrolledtext.ScrolledText(history_frame, height=10, state="disabled", font=("Consolas", 10))
        self.history_text.pack(fill="both", expand=True)
        tk.Button(history_frame, text="Refresh History", command=self.load_history).pack(pady=5)
        self._add_paste_support(self.history_text)

        self.load_history()

    def _add_paste_support(self, widget):
        # Universal copy/cut/paste support
        def do_paste(event=None):
            try:
                widget.insert(tk.INSERT, widget.clipboard_get())
            except Exception:
                pass
            return 'break'

        def do_copy(event=None):
            try:
                widget.clipboard_clear()
                sel = widget.selection_get()
                widget.clipboard_append(sel)
            except Exception:
                pass
            return 'break'

        def do_cut(event=None):
            try:
                widget.clipboard_clear()
                sel = widget.selection_get()
                widget.clipboard_append(sel)
                widget.delete("sel.first", "sel.last")
            except Exception:
                pass
            return 'break'

        # Keyboard bindings
        widget.bind('<Control-v>', do_paste)
        widget.bind('<Control-V>', do_paste)
        widget.bind('<Shift-Insert>', do_paste)
        widget.bind('<Control-c>', do_copy)
        widget.bind('<Control-C>', do_copy)
        widget.bind('<Control-x>', do_cut)
        widget.bind('<Control-X>', do_cut)
        widget.bind('<Shift-Delete>', do_cut)

        # Context menu
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Cut", command=lambda: do_cut())
        menu.add_command(label="Copy", command=lambda: do_copy())
        menu.add_command(label="Paste", command=lambda: do_paste())

        def show_menu(event):
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
            return 'break'

        widget.bind('<Button-3>', show_menu)  # Windows/Linux
        widget.bind('<Button-2>', show_menu)  # macOS

    def _make_entry_clickable(self, entry, message):
        # On single left click, select all and copy to clipboard, then show a tooltip/messagebox
        def on_click(event):
            entry.selection_range(0, tk.END)
            entry.clipboard_clear()
            entry.clipboard_append(entry.get())
            # Show a quick tooltip-like message (non-blocking)
            self._show_temp_tooltip(entry, message)
        entry.bind('<Button-1>', on_click)

    def _show_temp_tooltip(self, widget, text, duration=1200):
        # Show a small label below the widget for a short time
        x = widget.winfo_rootx() - widget.winfo_toplevel().winfo_rootx()
        y = widget.winfo_rooty() - widget.winfo_toplevel().winfo_rooty() + widget.winfo_height() + 2
        tooltip = tk.Label(widget.master, text=text, bg='#ffffe0', relief='solid', borderwidth=1, font=("Arial", 9))
        tooltip.place(x=x, y=y)
        widget.after(duration, tooltip.destroy)

    def create_wallet(self):
        pub, priv = wallet.create_wallet()
        self.pubkey_var.set(pub)
        self.privkey_var.set(priv)
        self.current_wallet = wallet.load_wallet_from_private_key(priv)
        self.current_pubkey = pub
        self.wallet_name_var.set("") # Leave blank for manual import
        messagebox.showinfo("Wallet Created", f"A new wallet has been created.\n\nPublic Key:\n{pub}\n\nPrivate Key:\n{priv}")

    def import_wallet(self):
        priv = simpledialog.askstring("Import Wallet", "Enter your base58-encoded private key:")
        if not priv:
            return
        try:
            w = wallet.load_wallet_from_private_key(priv)
            pub = str(w.pubkey())
            self.pubkey_var.set(pub)
            self.privkey_var.set(priv)
            self.current_wallet = w
            self.current_pubkey = pub
            self.wallet_name_var.set("")  # Leave blank for manual import
            messagebox.showinfo("Wallet Imported", f"Wallet imported successfully.\n\nPublic Key:\n{pub}")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import wallet:\n{e}")

    def import_wallet_from_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Private Key File",
            filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')]
        )
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            priv = None
            pub = None
            # Try to parse both formats
            for line in lines:
                if line.startswith('Private Key:'):
                    priv = line.split('Private Key:')[1].strip()
                elif line.startswith('Public Key:'):
                    pub = line.split('Public Key:')[1].strip()
            if not priv:
                # Fallback: single-line file
                if len(lines) == 1:
                    priv = lines[0]
            if not priv:
                messagebox.showerror("Import Error", "No private key found in the selected file.")
                return
            w = wallet.load_wallet_from_private_key(priv)
            if not pub:
                pub = str(w.pubkey())
            self.pubkey_var.set(pub)
            self.privkey_var.set(priv)
            self.current_wallet = w
            self.current_pubkey = pub
            # Set wallet name from filename (strip extension)
            import os
            base = os.path.basename(file_path)
            name, _ = os.path.splitext(base)
            self.wallet_name_var.set(name)
            messagebox.showinfo("Wallet Imported", f"Wallet imported successfully from file.\n\nPublic Key:\n{pub}")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import wallet from file:\n{e}")

    def save_wallet(self):
        pub = self.pubkey_var.get()
        priv = self.privkey_var.get()
        if not pub or not priv:
            messagebox.showwarning("No Wallet", "No wallet to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text Files', '*.txt')], title='Save Wallet As')
        if file_path:
            utils.save_wallet_to_file(pub, priv, filename=file_path)
            messagebox.showinfo("Wallet Saved", f"Wallet saved to {file_path}")

    def check_balance(self):
        if not self.current_wallet:
            messagebox.showwarning("No Wallet", "Please create or import a wallet first.")
            return
        try:
            bal = solana_client.get_balance(str(self.current_wallet.pubkey()))
            self.balance_var.set(f"{bal:.6f} SOL")
            messagebox.showinfo("Balance", f"Current balance: {bal:.6f} SOL")
        except Exception as e:
            messagebox.showerror("Balance Error", f"Failed to fetch balance:\n{e}")

    def send_sol(self):
        if not self.current_wallet:
            messagebox.showwarning("No Wallet", "Please create or import a wallet first.")
            return
        to_addr = self.recipient_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        if not to_addr or not amount_str:
            messagebox.showwarning("Missing Data", "Please enter recipient address and amount.")
            return
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
        except Exception as e:
            messagebox.showerror("Amount Error", f"Invalid amount: {e}")
            return
        try:
            resp = solana_client.send_sol(self.current_wallet, to_addr, amount)
            transaction_log.log_transaction(str(self.current_wallet.pubkey()), to_addr, amount, resp)
            messagebox.showinfo("Transaction Sent", f"Transaction sent!\nSignature: {resp}")
            self.load_history()
        except Exception as e:
            messagebox.showerror("Send Error", f"Failed to send SOL:\n{e}")

    def load_history(self):
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)
        if not os.path.exists("history.json"):
            self.history_text.insert(tk.END, "No transaction history found.\n")
            self.history_text.config(state="disabled")
            return
        try:
            with open("history.json", "r", encoding="utf-8") as f:
                history = json.load(f)
            if not history:
                self.history_text.insert(tk.END, "No transactions yet.\n")
            else:
                for tx in reversed(history):
                    self.history_text.insert(tk.END, f"From: {tx['from']}\nTo: {tx['to']}\nAmount: {tx['amount']} SOL\nSignature: {tx['response']}\n---\n")
        except Exception as e:
            self.history_text.insert(tk.END, f"Failed to load history: {e}\n")
        self.history_text.config(state="disabled")


def start_gui():
    root = tk.Tk()
    app = SolanaWalletGUI(root)
    root.mainloop()

if __name__ == "__main__":
    start_gui()