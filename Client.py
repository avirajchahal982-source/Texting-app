import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

HOST = "127.0.0.1"
PORT = 8080

sock = None


# ---------------------------------------------------------
# Safe UI message insert (main thread only)
# ---------------------------------------------------------
def safe_add_message(text, align, color):
    chat_box.configure(state="normal")

    tag = align
    chat_box.tag_configure(tag, justify=align, foreground=color, font=("Arial", 12))

    chat_box.insert(tk.END, text + "\n", tag)
    chat_box.configure(state="disabled")
    chat_box.see(tk.END)


# ---------------------------------------------------------
# Networking
# ---------------------------------------------------------
def connect_to_server():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((HOST, PORT))
    except Exception as e:
        safe_add_message(f"[ERROR] Could not connect: {e}", "left", "red")
        return

    threading.Thread(target=receive_messages, daemon=True).start()
    safe_add_message("[Connected to server]", "left", "#888")


def receive_messages():
    global sock

    while True:
        try:
            data = sock.recv(2048)
            if not data:
                break

            msg = data.decode()

            # schedule UI update from main thread
            window.after(0, safe_add_message, msg, "left", "#1E90FF")

        except:
            break


def send_message():
    msg = entry.get().strip()
    if not msg:
        return

    # Display your own message
    safe_add_message(f"You: {msg}", "right", "#32CD32")

    try:
        sock.sendall(msg.encode())
    except:
        safe_add_message("[ERROR] Failed to send message", "left", "red")

    entry.delete(0, tk.END)


def on_enter(event):
    send_message()


def on_escape(event):
    window.destroy()


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
window = tk.Tk()
window.title("Multi-User Chat")
window.geometry("520x500")
window.config(bg="#ECECEC")

# Header bar
header = tk.Label(
    window,
    text="🟢 Online Chat",
    bg="#4A90E2",
    fg="white",
    font=("Arial", 16, "bold"),
    pady=10
)
header.pack(fill=tk.X)

# Chat box
chat_box = scrolledtext.ScrolledText(
    window,
    wrap=tk.WORD,
    state="disabled",
    bg="white",
    font=("Arial", 12)
)
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Bottom input area
bottom = tk.Frame(window, bg="#ECECEC")
bottom.pack(fill=tk.X, padx=10, pady=10)

entry = tk.Entry(bottom, font=("Arial", 14))
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

send_btn = tk.Button(
    bottom,
    text="Send",
    font=("Arial", 12, "bold"),
    bg="#4CAF50",
    fg="white",
    width=10,
    command=send_message
)
send_btn.pack(side=tk.RIGHT)

window.bind("<Return>", on_enter)
window.bind("<Escape>", on_escape)

entry.focus()

# Connect after UI loads
window.after(200, connect_to_server)

window.mainloop()

