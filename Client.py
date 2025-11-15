import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext

PORT = 8080
sock = None
connected = False
username = None
server_ip = None

# GUI update function
def safe_add_message(text, color="#000000", align="left"):
    chat_box.configure(state="normal")
    tag = align
    chat_box.tag_configure(tag, justify=align, foreground=color)
    chat_box.insert(tk.END, text + "\n", tag)
    chat_box.configure(state="disabled")
    chat_box.see(tk.END)
    entry.focus_set()

# Send message to server
def send_message(*args):
    msg = entry.get().strip()
    if not msg or not connected:
        return
    try:
        sock.sendall(msg.encode())
    except:
        safe_add_message("[ERROR sending message]", "red")
        return
    entry.delete(0, tk.END)

# Receive messages from server
def receive_messages():
    global sock, connected
    while True:
        if sock:
            try:
                data = sock.recv(2048)
                if not data:
                    raise ConnectionError
                msg = data.decode()
                safe_add_message(msg, "#1E90FF")
            except:
                if connected:
                    safe_add_message("[Disconnected, reconnecting...]", "red")
                    connected = False
                    if sock:
                        sock.close()
                    sock = None
        time.sleep(1)

# Connect to server
def connect_loop():
    global sock, connected, username, server_ip
    while True:
        if not connected:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((server_ip, PORT))

                # Receive username prompt
                sock.recv(1024)
                
                # Send username to server
                sock.sendall(username.encode())
                safe_add_message(f"[Connected to {server_ip}:{PORT}]", "#888")
                connected = True
            except Exception as e:
                safe_add_message(f"[Reconnect failed → retrying in 5s]", "red")
                sock = None
                time.sleep(5)
        time.sleep(1)

# GUI Setup
window = tk.Tk()
window.title("Global Chat")
window.geometry("520x500")

header = tk.Label(window, text="Global Chat", bg="#4A90E2", fg="white", font=("Arial", 16, "bold"), pady=10)
header.pack(fill=tk.X)

chat_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, state="disabled", bg="white", font=("Arial", 12))
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

bottom = tk.Frame(window)
bottom.pack(fill=tk.X, padx=10, pady=10)

entry = tk.Entry(bottom, font=("Arial", 14))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

send_btn = tk.Button(bottom, text="Send", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", width=10, command=send_message)
send_btn.pack(side=tk.RIGHT)

entry.bind("<Return>", send_message)
window.bind("<Escape>", lambda e: window.destroy())
entry.focus_set()

# Server IP and Username
server_ip = simpledialog.askstring("Server IP", "Enter server IP:")
username = simpledialog.askstring("Username", "Enter your username:")

if server_ip and username:
    threading.Thread(target=receive_messages, daemon=True).start()
    threading.Thread(target=connect_loop, daemon=True).start()
else:
    safe_add_message("[ERROR] Server IP or username not provided.", "red")

window.mainloop()
