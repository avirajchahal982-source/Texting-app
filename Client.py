import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

HOST = "127.0.0.1"
PORT = 8080

sock = None


# ---------------------------------------------------------
# Networking
# ---------------------------------------------------------
def connect_to_server():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    threading.Thread(target=receive_messages, daemon=True).start()


def receive_messages():
    global sock
    while True:
        try:
            data = sock.recv(2048)
            if not data:
                break

            msg = data.decode()
            add_message(msg, align="left", color="#1E90FF")

        except:
            break


def send_message():
    msg = entry.get().strip()
    if not msg:
        return

    # Display locally
    add_message(f"You: {msg}", align="right", color="#32CD32")

    try:
        sock.sendall(msg.encode())
    except:
        add_message("[ERROR] Could not send message.", align="left", color="red")

    entry.delete(0, tk.END)


def add_message(text, align="left", color="black"):
    chat_box.configure(state="normal")

    if align == "right":
        chat_box.tag_configure("right", justify="right", foreground=color)
        chat_box.insert(tk.END, text + "\n", "right")
    else:
        chat_box.tag_configure("left", justify="left", foreground=color)
        chat_box.insert(tk.END, text + "\n", "left")

    chat_box.configure(state="disabled")
    chat_box.see(tk.END)


def on_enter(event):
    send_message()


def on_escape(event):
    window.destroy()


# ---------------------------------------------------------
# UI Setup
# ---------------------------------------------------------
window = tk.Tk()
window.title("Multi-User Chat")
window.geometry("520x500")
window.config(bg="#ECECEC")

# Header bar
header = tk.Label(
    window,
    text="Online Chat",
    bg="#4A90E2",
    fg="white",
    font=("Arial", 16, "bold"),
    pady=10
)
header.pack(fill=tk.X)

# Chat display box
chat_box = scrolledtext.ScrolledText(
    window,
    wrap=tk.WORD,
    state="disabled",
    bg="white",
    font=("Arial", 12),
)
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Bottom frame for input bar
bottom_frame = tk.Frame(window, bg="#ECECEC")
bottom_frame.pack(fill=tk.X, padx=10, pady=10)

entry = tk.Entry(bottom_frame, font=("Arial", 14))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

send_btn = tk.Button(
    bottom_frame,
    text="Send",
    font=("Arial", 12, "bold"),
    bg="#4CAF50",
    fg="white",
    width=10,
    command=send_message
)
send_btn.pack(side=tk.RIGHT)

# Key bindings
window.bind("<Return>", on_enter)
window.bind("<Escape>", on_escape)

entry.focus()

# Connect at startup
connect_to_server()

window.mainloop()
