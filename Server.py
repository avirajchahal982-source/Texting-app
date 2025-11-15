import socket
import threading

HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 8080        # Port to use

clients = []  # List to store connected client sockets

# ---------------- Broadcast function ----------------
def broadcast(message):
    """Send a message to all connected clients"""
    for client in clients:
        try:
            client.sendall(message.encode())
        except:
            clients.remove(client)

# ---------------- Handle each client ----------------
def handle_client(conn, addr):
    print(f"[CONNECTED] {addr}")
    clients.append(conn)
    try:
        while True:
            data = conn.recv(2048)
            if not data:
                break

            message = data.decode()
            print(f"[{addr}] {message}")
            
            # Broadcast to everyone (including sender)
            broadcast(f"{addr[0]}: {message}")

    except Exception as e:
        print(f"[ERROR] {addr} → {e}")
    finally:
        conn.close()
        if conn in clients:
            clients.remove(conn)
        print(f"[DISCONNECTED] {addr}")

# ---------------- Start the server ----------------
def start_server():
    print(f"[STARTING] Server on {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"[LISTENING] Waiting for connections...")

        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()

if __name__ == "__main__":
    start_server()

