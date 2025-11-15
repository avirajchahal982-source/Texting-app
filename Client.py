import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

HOST = "149.102.225.58"  # replace with your server LAN IP, e.g., 192.168.1.5
PORT = 8080

sock = None


def safe_add_message(text, align="left", color="#000000"):
    """Add a message to the chat box safely from any thread"""
    chat_box.configure(state="normal")
    tag = align
    chat_box.tag_configure(tag, justify=align, foreground=color)
    chat_box.insert(tk.END, text + "\n", tag)
    chat_box.configure(state="disabled")
    chat_box.see(tk.END)
    entry.focus_set()  # keep typing focus


def connect_to_server():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
        window.after(0, safe_add_message, "[Connected to server]", "left", "#888")
    except Exception as e:
        window.after(0, safe_add_message, f"[ERROR] {e}", "left", "red")
        return

    threading.Thread(target=receive_messages, daemon=True).start()


def receive_messages():
    global sock
    while True:
        try:
            data = sock.recv(2048)
            if not data:
                break
            msg = data.decode()
            # Show incoming messages from server
            # We do not add "You:" here to avoid duplication
            window.after(0, safe_add_message, msg, "left", "#1E90FF")
        except:
            break


def send_message(*args):
    msg = entry.get().strip()
    if not msg:
        return
    try:
        sock.sendall(msg.encode())
    except:
        safe_add_message("[ERROR sending message]", "left", "red")
        return
    entry.delete(0, tk.END)
    # Optionally: do not show "You: ..." locally because server will echo it
    # safe_add_message(f"You: {msg}", "right", "#32CD32")


def on_escape(event):
    window.destroy()


# ------------------ GUI ------------------
window = tk.Tk()
window.title("LAN Chat")
window.geometry("520x500")

header = tk.Label(window, text="🟢 LAN Chat", bg="#4A90E2",
                  fg="white", font=("Arial", 16, "bold"), pady=10)
header.pack(fill=tk.X)

chat_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, state="disabled",
                                     bg="white", font=("Arial", 12))
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

bottom = tk.Frame(window)
bottom.pack(fill=tk.X, padx=10, pady=10)

entry = tk.Entry(bottom, font=("Arial", 14))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

send_btn = tk.Button(bottom, text="Send", font=("Arial", 12, "bold"),
                     bg="#4CAF50", fg="white", width=10, command=send_message)
send_btn.pack(side=tk.RIGHT)

entry.bind("<Return>", send_message)
window.bind("<Escape>", on_escape)

entry.focus_set()
window.after(200, connect_to_server)

window.mainloop()
