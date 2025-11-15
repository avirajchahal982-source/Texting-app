import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext
import time  # <-- Added time import

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
        time.sleep(1)  # <-- sleep for 1 second to avoid busy looping

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
            except socket.gaierror:
                safe_add_message("[ERROR] Invalid server IP address.", "red")
                break  # <-- Stop trying to reconnect if the server IP is invalid
            except Exception as e:
                safe_add_message(f"[Reconnect failed → retrying in 5s]", "red")
                sock = None
                time.sleep(5)  # Retry connection after 5 seconds
        time.sleep(1)

# GUI Setup
window = tk.Tk()
window.tit
