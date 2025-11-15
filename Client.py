import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

HOST = "127.0.0.1"
PORT = 8080

sock = None


def connect_to_server():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    threading.Thread(target=receive_messages, daemon=True).start()


def receive_messages():
    """Constantly listen for server messages."""
    global sock
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break

            msg = data.decode()
            chat_box.insert(tk.END, msg + "\n")
            chat_box.see(tk.END)

        except:
            break


def send_message():
    msg = entry.get()
    if not msg:
        return

    # Display locally
    chat_box.insert(tk.END, f"You: {msg}\n")
    chat_box.see(tk.END)

    # Send to server
    try:
        sock.sendall(msg.encode())
    except:
        chat_box.insert(tk.END, "[ERROR] Failed to send.\n")

    entry.delete(0, tk.END)


def on_enter(event):
    send_message()


def on_escape(event):
    window.destroy()


# ---- GUI ----
window = tk.Tk()
window.title("Multi-User Chat Client")
window.geometry("500x450")
window.resizable(False, False)

chat_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=60, height=20)
chat_box.pack(pady=10)

entry = tk.Entry(window, width=50, font=("Arial", 12))
entry.pack(side=tk.LEFT, padx=10, pady=10)

send_btn = tk.Button(window, text="Send", width=10, command=send_message)
send_btn.pack(side=tk.LEFT)

window.bind("<Return>", on_enter)
window.bind("<Escape>", on_escape)

entry.focus()

# Connect to server at startup
connect_to_server()

window.mainloop()
