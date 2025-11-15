import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext

PORT = 8080  # must match server

sock = None

# ---------------- Helper ----------------
def safe_add_message(text, align="left", color="#000000"):
    chat_box.configure(state="normal")
    tag = align
    chat_box.tag_configure(tag, justify=align, foreground=color)
    chat_box.insert(tk.END, text + "\n", tag)
    chat_box.configure(state="disabled")
    chat_box.see(tk.END)
    entry.focus_set()

# ---------------- Connect ----------------
def connect_to_server():
    global sock, server_ip
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_ip, PORT))
        safe_add_message(f"[Connected to {server_ip}:{PORT}]", "left", "#888")
    except Exception as e:
        safe_add_message(f"[ERROR] {e}", "left", "red")
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
            safe_add_message(msg, "left", "#1E90FF")
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
    # server echoes your message; no local "You:" needed

def on_escape(event):
    window.destroy()

# ---------------- GUI ----------------
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

# ---------------- Ask for server IP ----------------
server_ip = simpledialog.askstring("Server IP", "Enter the server LAN IP:")
if server_ip:
    window.after(100, connect_to_server)
else:
    safe_add_message("[ERROR] No server IP provided.", "left", "red")

window.mainloop()
