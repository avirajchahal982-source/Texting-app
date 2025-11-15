import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

HOST = "127.0.0.1"   # change to your server IP
PORT = 8080          # change to your server port


def send_message():
    msg = entry.get()
    if not msg:
        return
    
    # Display user message
    chat_box.insert(tk.END, f"You: {msg}\n")
    chat_box.see(tk.END)
    entry.delete(0, tk.END)

    # Run network call in a thread
    threading.Thread(target=network_send, args=(msg,), daemon=True).start()


def network_send(message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(message.encode())
            data = s.recv(1024).decode()

        chat_box.insert(tk.END, f"Server: {data}\n")
        chat_box.see(tk.END)

    except Exception as e:
        chat_box.insert(tk.END, f"[ERROR] {e}\n")
        chat_box.see(tk.END)


def on_enter(event):
    send_message()


def on_escape(event):
    window.destroy()


# ------------------- UI Setup -------------------
window = tk.Tk()
window.title("Socket Client UI")
window.geometry("500x450")
window.resizable(False, False)

chat_box = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=60, height=20, state="normal")
chat_box.pack(pady=10)

entry = tk.Entry(window, width=50, font=("Arial", 12))
entry.pack(side=tk.LEFT, padx=10, pady=10)

send_btn = tk.Button(window, text="Send", width=10, command=send_message)
send_btn.pack(side=tk.LEFT)

# Key bindings
window.bind("<Return>", on_enter)
window.bind("<Escape>", on_escape)

entry.focus()

window.mainloop()
