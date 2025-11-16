import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext
import time  # <-- Ensure this line is here to import the time module

PORT = 8080  # The port number the server is listening on
sock = None
connected = False
username = None
server_ip = None

# Function to update chat window with messages
def safe_add_message(text, color="#000000", align="left"):
    chat_box.configure(state="normal")
    tag = align
    chat_box.tag_configure(tag, justify=align, foreground=color)
    chat_box.insert(tk.END, text + "\n", tag)
    chat_box.configure(state="disabled")
    chat_box.see(tk.END)
    entry.focus_set()

# Function to send message to server
def send_message(*args):
    msg = entry.get().strip()
    if not msg or not connected:
        return
    try:
        sock.sendall(msg.encode())  # Send message to server
    except:
        safe_add_message("[ERROR sending message]", "red")
        return
    entry.delete(0, tk.END)  # Clear entry field after sending message

# Function to receive messages from server
def receive_messages():
    global sock, connected
    while True:
        if sock:
            try:
                data = sock.recv(2048)  # Receive message from server
                if not data:
                    raise ConnectionError
                msg = data.decode()
                safe_add_message(msg, "#1E90FF")  # Display message in chat window
            except:
                if connected:
                    safe_add_message("[Disconnected, reconnecting...]", "red")
                    connected = False
                    if sock:
                        sock.close()
                    sock = None
        time.sleep(1)  # <-- sleep for 1 second to avoid busy looping

# Function to handle connection attempts to the server
def connect_loop():
    global sock, connected, username, server_ip
    while True:
        if not connected:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((server_ip, PORT))  # Connect to server

                # Receive prompt for username from server
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
        time.sleep(1)  # <-- sleep for 1 second to avoid busy looping

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

send_btn = tk.Button(bottom, text="Send", font=("Arial", 12, "bold"), bg="_
