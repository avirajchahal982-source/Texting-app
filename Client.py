import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext
import time
import queue

PORT = 8080
sock = None
connected = False
reconnect_interval = 5  # seconds
message_queue = queue.Queue()

# ---------------- Helper ----------------
def safe_add_message(text, align="left", color="#000000"):
    # Use after() to safely update Tkinter from any thread
    def _insert():
        chat_box.configure(state="normal")
        tag = align
        chat_box.tag_configure(tag, justify=align, foreground=color)
        chat_box.insert(tk.END, text + "\n", tag)
        chat_box.configure(state="disabled")
        chat_box.see(tk.END)
        entry.focus_set()
    window.after(0, _insert)

# ---------------- Connect ----------------
def connect_to_server():
    global sock, connected
    while not connected:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.connect((server_ip, PORT))
            connected = True
            safe_add_message(f"[Connected to {server_ip}:{PORT}]", "left", "#888")
            send_btn.config(state=tk.NORMAL)
            entry.config(state=tk.NORMAL)
            threading.Thread(target=receive_messages, daemon=True).start()
        except Exception as e:
            safe_add_message(f"[Reconnect failed: {e} → retrying in {reconnect_interval}s]", "left", "red")
            try:
                sock.close()
            except: pass
            time.sleep(reconnect_interval)

def receive_messages():
    global sock, connected
    while connected:
        try:
            data = sock.recv(2048)
            if not data:
                safe_add_message("[Disconnected from server]", "left", "red")
                connected = False
                sock.close()
                send_btn.config(state=tk.DISABLED)
                entry.config(state=tk.DISABLED)
                threading.Thread(target=connect_to_server, daemon=True).start()
                break
            msg = data.decode()
            safe_add_message(msg, "left", "#1E90FF")
        except Exception as e:
            safe_add_message(f"[Receive error: {e}]", "left", "red")
            connected = False
            try: sock.close() 
            except: pass
            send_btn.config(state=tk.DISABLED)
            entry.config(state=tk.DISABLED)
            threading.Thread(target=connect_to_server, daemon=True).start()
            break

def send_message(*args):
    global sock, connected
    msg = entry.get().strip()
    if not msg:
        return
    if not connected:
        safe_add_message("[ERROR] Not connected to server", "left", "red")
        entry.delete(0, tk.END)
        return
    try:
        sock.sendall(msg.encode())
    except Exception as e:
        safe_add_message(f"[Send error: {e}]", "left", "red")
        connected = False
        try: sock.close() 
        except: pass
        send_btn.config(state=tk.DISABLED)
        entry.config(state=tk.DISABLED)
        threading.Thread(target=connect_to_server, daemon=True).start()
    entry.delete(0, tk.END)

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

send_btn.config(state=tk.DISABLED)
entry.config(state=tk.DISABLED)

entry.bind("<Return>", send_message)
window.bind("<Escape>", on_escape)
entry.focus_set()

# ---------------- Ask for server IP ----------------
server_ip = simpledialog.askstring("Server IP", "Enter the server LAN IP:")
if server_ip:
    threading.Thread(target=connect_to_server, daemon=True).start()
else:
    safe_add_message("[ERROR] No server IP provided.", "left", "red")

window.mainloop()
