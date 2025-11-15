import socket
import threading
from datetime import datetime

HOST = "0.0.0.0"
PORT = 8080

clients = {}  # addr -> {"socket": sock, "username": str, "queue": []}
lock = threading.Lock()

# Broadcast message to all clients
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
                    if len(info["queue"]) > 100:
                        info["queue"].pop(0)
            else:
                info["queue"].append(formatted)
                if len(info["queue"]) > 100:
                    info["queue"].pop(0)

# Handle each client
def handle_client(conn, addr):
    try:
        conn.sendall("USERNAME?".encode())  # Ask for the username
        username = conn.recv(1024).decode().strip()
        if not username:
            username = f"User{addr[1]}"  # Default username if none provided

        with lock:
            clients[addr] = {"socket": conn, "username": username, "queue": []}
        
        # Send a welcome message
        broadcast(f"[{username} joined the chat]")

        # Send queued messages to the client
        with lock:
            for message in clients[addr]["queue"]:
                try:
                    conn.sendall(message.encode())
                except:
                    break
            clients[addr]["queue"].clear()

        while True:
            data = conn.recv(2048)
            if not data:
                break
            message = data.decode().strip()
            broadcast(f"{username}: {message}")
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        with lock:
            del clients[addr]  # Remove the client from the list
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
