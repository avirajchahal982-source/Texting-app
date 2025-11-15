import socket
import threading

HOST = "0.0.0.0"
PORT = 8080

clients = []        # list of client sockets
clients_lock = threading.Lock()


def broadcast(message, sender=None):
    """Send message to all connected clients except sender."""
    with clients_lock:
        for client in clients:
            if client != sender:
                try:
                    client.sendall(message.encode())
                except:
                    pass


def handle_client(conn, addr):
    print(f"[CONNECTED] {addr}")

    with clients_lock:
        clients.append(conn)

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            message = data.decode()
            print(f"[RECEIVED from {addr}] {message}")

            broadcast(f"[{addr[0]}] {message}", sender=conn)

    except Exception as e:
        print(f"[ERROR] {addr} → {e}")

    finally:
        with clients_lock:
            clients.remove(conn)

        conn.close()
        print(f"[DISCONNECTED] {addr}")
        broadcast(f"[SERVER] {addr[0]} left the chat.")


def start_server():
    print(f"[STARTING] Multi-user Server on {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()

        while True:
            conn, addr = server.accept()
            broadcast(f"[SERVER] {addr[0]} joined the chat.")
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()

