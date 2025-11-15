import socket
import threading
from datetime import datetime

HOST = "0.0.0.0"
PORT = 8080

clients = {}  # addr -> {"socket": sock, "username": str, "queue": []}
lock = threading.Lock()
MAX_QUEUE = 100

def broadcast(msg, sender=None):
    timestamp = datetime.now().strftime("%H:%M")
    formatted = f"[{timestamp}] {msg}"
    with lock:
        for addr, info in clients.items():
            sock = info.get("socket")
            if sock:
                try:
                    sock.sendall(formatted.encode())
                except:
                    info["socket"] = None
                    info["queue"].append(formatted)
                    if len(info["queue"]) > MAX_QUEUE:
                        info["queue"].pop(0)
            else:
                info["queue"].append(formatted)
                if len(info["queue"]) > MAX_QUEUE:
                    info["queue"].pop(0)

def handle_client(conn, addr):
    try:
        conn.sendall("USERNAME?".encode())
        username = conn.recv(1024).decode().strip() or f"User{addr[1]}"
        with lock:
            clients.setdefault(addr, {"socket": conn, "username": username, "queue": []})
            clients[addr]["socket"] = conn
            clients[addr]["username"] = username

        # Send queued messages
        with lock:
            for m in clients[addr]["queue"]:
                try:
                    conn.sendall(m.encode())
                except:
                    break
            clients[addr]["queue"].clear()

        broadcast(f"[{username} joined the chat]")

        while True:
            data = conn.recv(2048)
            if not data:
                break
            message = data.decode().strip()
            broadcast(f"{username}: {message}")
    except:
        pass
    finally:
        with lock:
            clients[addr]["socket"] = None
        broadcast(f"[{username} left the chat]")
        conn.close()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"[LISTENING] Server on {HOST}:{PORT}")
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
