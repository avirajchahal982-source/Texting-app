import socket
import threading
import time

HOST = "0.0.0.0"
PORT = 8080

clients = {}  # Map: client_address -> {"socket": sock, "queue": []}
clients_lock = threading.Lock()
history_limit = 50  # Max number of messages to keep per client

# ---------------- Broadcast function ----------------
def broadcast(message, sender_addr=None):
    """Send message to all clients, queue if disconnected"""
    with clients_lock:
        for addr, info in clients.items():
            sock = info.get("socket")
            if sock:
                try:
                    sock.sendall(message.encode())
                except (ConnectionResetError, BrokenPipeError):
                    # Mark as disconnected
                    print(f"[WARN] Client {addr} disconnected, queuing messages")
                    info["socket"] = None
                    info["queue"].append(message)
                    if len(info["queue"]) > history_limit:
                        info["queue"].pop(0)
            else:
                # Client is disconnected, queue the message
                info["queue"].append(message)
                if len(info["queue"]) > history_limit:
                    info["queue"].pop(0)

# ---------------- Handle each client ----------------
def handle_client(conn, addr):
    print(f"[CONNECTED] {addr}")
    with clients_lock:
        if addr not in clients:
            clients[addr] = {"socket": conn, "queue": []}
        else:
            clients[addr]["socket"] = conn
    try:
        # Send queued messages first
        with clients_lock:
            for msg in clients[addr]["queue"]:
                try:
                    conn.sendall(msg.encode())
                except:
                    break
            clients[addr]["queue"].clear()

        while True:
            data = conn.recv(2048)
            if not data:
                break
            message = data.decode()
            print(f"[{addr}] {message}")
            broadcast(f"{addr[0]}: {message}", sender_addr=addr)

    except Exception as e:
        print(f"[ERROR] {addr} → {e}")
    finally:
        with clients_lock:
            if addr in clients:
                clients[addr]["socket"] = None  # Mark as disconnected
        conn.close()
        print(f"[DISCONNECTED] {addr}")

# ---------------- Start the server ----------------
def start_server():
    print(f"[STARTING] Server on {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"[LISTENING] Waiting for connections...")

        while True:
            try:
                conn, addr = server.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                thread.start()
            except Exception as e:
                print(f"[ERROR] Accepting connection: {e}")

if __name__ == "__main__":
    start_server()
